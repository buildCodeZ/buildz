"""
MemoryGraph v2.0 — AI Agent 语义记忆图系统
==========================================
核心特性:
1. 语义化边: 边携带自然语言描述 + 独立向量嵌入, 可被直接检索
2. Spreading Activation (ACT-R): 联想记忆扩散
3. Ebbinghaus Forgetting + SM-2: 记忆衰减与间隔重复强化
4. Hybrid Retrieval: 节点向量 + BM25 + 边语义 + 图扩散 + 时序 5路融合
5. Memory Consolidation: 相似记忆自动合并去重
6. Temporal Validity: 边的时效性追踪 (valid_from / valid_to)
7. Agent Tool Schema: 兼容 OpenAI Function Calling

存储: SQLite (WAL模式) + 内嵌向量 (numpy)
依赖: numpy, sqlite3(内置), json(内置)
"""

import sqlite3
import json
import math
import time
import uuid
import heapq
import hashlib
import logging
import re
import threading
from enum import Enum
from typing import Optional, Callable
from dataclasses import dataclass, field, asdict
from collections import defaultdict
from datetime import datetime, timezone
from contextlib import contextmanager

import numpy as np

logger = logging.getLogger(__name__)


# ============================================================
# 1. 数据模型
# ============================================================

class MemoryType(Enum):
    EPISODIC = "episodic"      # 情景记忆: 具体事件/对话
    SEMANTIC = "semantic"      # 语义记忆: 抽象事实/知识
    PROCEDURAL = "procedural"  # 程序记忆: 操作步骤/技能


class EdgeType(Enum):
    CAUSES = "causes"
    RELATES_TO = "relates_to"
    CONTRADICTS = "contradicts"
    SUPPORTS = "supports"
    SEQUENCE = "sequence"
    GENERALIZES = "generalizes"
    SPECIALIZES = "specializes"
    CO_OCCURS = "co_occurs"


@dataclass
class MemoryNode:
    id: str = ""
    content: str = ""
    memory_type: MemoryType = MemoryType.SEMANTIC
    embedding: Optional[list] = None
    importance: float = 0.5
    activation: float = 0.0
    access_count: int = 0
    last_accessed: float = 0.0
    created_at: float = 0.0
    half_life: float = 3600.0 * 24 * 7  # 默认7天半衰期
    metadata: dict = field(default_factory=dict)
    tags: list = field(default_factory=list)
    source: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        now = time.time()
        if not self.created_at:
            self.created_at = now
        if not self.last_accessed:
            self.last_accessed = now
        if isinstance(self.memory_type, str):
            self.memory_type = MemoryType(self.memory_type)


@dataclass
class MemoryEdge:
    """语义化记忆边 — 边本身也是可检索的记忆单元"""
    id: str = ""
    source_id: str = ""
    target_id: str = ""
    description: str = ""                    # ★ 自然语言关系描述 (核心!)
    edge_type: EdgeType = EdgeType.RELATES_TO
    weight: float = 1.0
    created_at: float = 0.0
    updated_at: float = 0.0
    access_count: int = 0
    embedding: Optional[list] = None         # ★ 边的独立向量嵌入
    valid_from: Optional[float] = None       # ★ 事实生效时间
    valid_to: Optional[float] = None         # ★ 事实失效时间 (None=当前有效)
    confidence: float = 1.0                  # ★ 置信度 [0, 1]
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        now = time.time()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now
        if isinstance(self.edge_type, str):
            self.edge_type = EdgeType(self.edge_type)


@dataclass
class RetrievalResult:
    node: MemoryNode
    score: float
    score_breakdown: dict = field(default_factory=dict)
    path: list = field(default_factory=list)
    is_edge_result: bool = False             # ★ 标记是否为边检索结果
    edge_id: Optional[str] = None            # ★ 关联的边ID


# ============================================================
# 2. 向量工具 & 嵌入提供者
# ============================================================

class VectorOps:
    @staticmethod
    def cosine_similarity(a, b) -> float:
        a, b = np.asarray(a, dtype=np.float32), np.asarray(b, dtype=np.float32)
        norm_a, norm_b = np.linalg.norm(a), np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))

    @staticmethod
    def normalize(vec) -> np.ndarray:
        v = np.asarray(vec, dtype=np.float32)
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    @staticmethod
    def weighted_average(vectors: list, weights: list) -> list:
        vecs = np.array(vectors, dtype=np.float32)
        w = np.array(weights, dtype=np.float32).reshape(-1, 1)
        total = np.sum(w)
        if total == 0:
            return vecs[0].tolist()
        return (np.sum(vecs * w, axis=0) / total).tolist()


class EmbeddingProvider:
    def embed(self, text: str) -> list[float]:
        raise NotImplementedError

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(t) for t in texts]


class HashEmbeddingProvider(EmbeddingProvider):
    """基于哈希+随机投影的轻量嵌入, 零外部依赖"""

    def __init__(self, dim: int = 384, seed: int = 42):
        self.dim = dim
        rng = np.random.RandomState(seed)
        self._projection = rng.randn(4096, dim).astype(np.float32) / np.sqrt(dim)

    def embed(self, text: str) -> list[float]:
        vec = np.zeros(4096, dtype=np.float32)
        tokens = text.lower().split()
        for i, token in enumerate(tokens):
            h = int(hashlib.md5(token.encode()).hexdigest(), 16) % 4096
            vec[h] += 1.0
            if i > 0:
                bigram = f"{tokens[i - 1]}_{token}"
                h2 = int(hashlib.md5(bigram.encode()).hexdigest(), 16) % 4096
                vec[h2] += 0.5
            # 字符级trigram补充
            for j in range(len(token) - 2):
                tri = token[j:j + 3]
                h3 = int(hashlib.md5(tri.encode()).hexdigest(), 16) % 4096
                vec[h3] += 0.3
        projected = vec @ self._projection
        norm = np.linalg.norm(projected)
        if norm > 0:
            projected = projected / norm
        return projected.tolist()


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.api_key = api_key
        self.model = model

    def embed(self, text: str) -> list[float]:
        import urllib.request
        data = json.dumps({"input": text, "model": self.model}).encode()
        req = urllib.request.Request(
            "https://api.openai.com/v1/embeddings",
            data=data,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
        return result["data"][0]["embedding"]


# ============================================================
# 3. BM25 全文检索
# ============================================================

class BM25Index:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_freq: dict[str, int] = defaultdict(int)
        self.doc_lengths: dict[str, int] = {}
        self.doc_tokens: dict[str, list[str]] = {}
        self.avg_dl: float = 0.0
        self.n_docs: int = 0

    def _tokenize(self, text: str) -> list[str]:
        return re.findall(r'\w+', text.lower())

    def add_document(self, doc_id: str, text: str):
        tokens = self._tokenize(text)
        self.doc_tokens[doc_id] = tokens
        self.doc_lengths[doc_id] = len(tokens)
        for t in set(tokens):
            self.doc_freq[t] += 1
        self.n_docs += 1
        self.avg_dl = sum(self.doc_lengths.values()) / self.n_docs if self.n_docs > 0 else 1.0

    def remove_document(self, doc_id: str):
        if doc_id not in self.doc_tokens:
            return
        for t in set(self.doc_tokens[doc_id]):
            self.doc_freq[t] -= 1
            if self.doc_freq[t] <= 0:
                del self.doc_freq[t]
        del self.doc_tokens[doc_id]
        del self.doc_lengths[doc_id]
        self.n_docs -= 1
        if self.n_docs > 0:
            self.avg_dl = sum(self.doc_lengths.values()) / self.n_docs

    def score(self, query: str, top_k: int = 20) -> list[tuple[str, float]]:
        query_tokens = self._tokenize(query)
        scores: dict[str, float] = {}
        for token in query_tokens:
            df = self.doc_freq.get(token, 0)
            if df == 0:
                continue
            idf = math.log((self.n_docs - df + 0.5) / (df + 0.5) + 1.0)
            for doc_id, tokens in self.doc_tokens.items():
                tf = tokens.count(token)
                if tf == 0:
                    continue
                dl = self.doc_lengths[doc_id]
                num = tf * (self.k1 + 1)
                den = tf + self.k1 * (1 - self.b + self.b * dl / max(self.avg_dl, 1.0))
                scores[doc_id] = scores.get(doc_id, 0.0) + idf * num / den
        return heapq.nlargest(top_k, scores.items(), key=lambda x: x[1])


# ============================================================
# 4. SQLite 持久化层 (含语义化边支持)
# ============================================================

class StorageBackend:
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._connections: dict[int, sqlite3.Connection] = {}
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        tid = threading.get_ident()
        if tid not in self._connections:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            self._connections[tid] = conn
        return self._connections[tid]

    def _init_db(self):
        conn = self._get_conn()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS memory_nodes (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                memory_type TEXT NOT NULL DEFAULT 'semantic',
                embedding BLOB,
                importance REAL DEFAULT 0.5,
                activation REAL DEFAULT 0.0,
                access_count INTEGER DEFAULT 0,
                last_accessed REAL,
                created_at REAL,
                half_life REAL DEFAULT 604800.0,
                metadata TEXT DEFAULT '{}',
                tags TEXT DEFAULT '[]',
                source TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS memory_edges (
                id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL REFERENCES memory_nodes(id) ON DELETE CASCADE,
                target_id TEXT NOT NULL REFERENCES memory_nodes(id) ON DELETE CASCADE,
                description TEXT NOT NULL DEFAULT '',
                edge_type TEXT NOT NULL DEFAULT 'relates_to',
                weight REAL DEFAULT 1.0,
                created_at REAL,
                updated_at REAL,
                access_count INTEGER DEFAULT 0,
                embedding BLOB,
                valid_from REAL,
                valid_to REAL,
                confidence REAL DEFAULT 1.0,
                metadata TEXT DEFAULT '{}'
            );

            CREATE INDEX IF NOT EXISTS idx_edges_source ON memory_edges(source_id);
            CREATE INDEX IF NOT EXISTS idx_edges_target ON memory_edges(target_id);
            CREATE INDEX IF NOT EXISTS idx_edges_type ON memory_edges(edge_type);
            CREATE INDEX IF NOT EXISTS idx_edges_valid ON memory_edges(valid_from, valid_to);
            CREATE INDEX IF NOT EXISTS idx_nodes_type ON memory_nodes(memory_type);
            CREATE INDEX IF NOT EXISTS idx_nodes_importance ON memory_nodes(importance DESC);
            CREATE INDEX IF NOT EXISTS idx_nodes_created ON memory_nodes(created_at DESC);
        """)
        conn.commit()

    @contextmanager
    def transaction(self):
        conn = self._get_conn()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    # --- Node CRUD ---
    def save_node(self, node: MemoryNode):
        conn = self._get_conn()
        emb_blob = np.array(node.embedding, dtype=np.float32).tobytes() if node.embedding else None
        conn.execute("""
            INSERT OR REPLACE INTO memory_nodes
            (id, content, memory_type, embedding, importance, activation,
             access_count, last_accessed, created_at, half_life, metadata, tags, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (node.id, node.content, node.memory_type.value, emb_blob,
              node.importance, node.activation, node.access_count,
              node.last_accessed, node.created_at, node.half_life,
              json.dumps(node.metadata, ensure_ascii=False),
              json.dumps(node.tags, ensure_ascii=False), node.source))

    def load_node(self, node_id: str) -> Optional[MemoryNode]:
        row = self._get_conn().execute("SELECT * FROM memory_nodes WHERE id = ?", (node_id,)).fetchone()
        return self._row_to_node(row) if row else None

    def delete_node(self, node_id: str):
        self._get_conn().execute("DELETE FROM memory_nodes WHERE id = ?", (node_id,))

    def get_all_nodes(self) -> list[MemoryNode]:
        rows = self._get_conn().execute("SELECT * FROM memory_nodes").fetchall()
        return [self._row_to_node(r) for r in rows]

    def get_nodes_by_type(self, mt: MemoryType) -> list[MemoryNode]:
        rows = self._get_conn().execute("SELECT * FROM memory_nodes WHERE memory_type = ?", (mt.value,)).fetchall()
        return [self._row_to_node(r) for r in rows]

    def node_count(self) -> int:
        return self._get_conn().execute("SELECT COUNT(*) FROM memory_nodes").fetchone()[0]

    # --- Edge CRUD (★ 语义化边) ---
    def save_edge(self, edge: MemoryEdge):
        conn = self._get_conn()
        emb_blob = np.array(edge.embedding, dtype=np.float32).tobytes() if edge.embedding else None
        conn.execute("""
            INSERT OR REPLACE INTO memory_edges
            (id, source_id, target_id, description, edge_type, weight,
             created_at, updated_at, access_count, embedding,
             valid_from, valid_to, confidence, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (edge.id, edge.source_id, edge.target_id, edge.description,
              edge.edge_type.value, edge.weight, edge.created_at, edge.updated_at,
              edge.access_count, emb_blob, edge.valid_from, edge.valid_to,
              edge.confidence, json.dumps(edge.metadata, ensure_ascii=False)))

    def load_edge(self, edge_id: str) -> Optional[MemoryEdge]:
        row = self._get_conn().execute("SELECT * FROM memory_edges WHERE id = ?", (edge_id,)).fetchone()
        return self._row_to_edge(row) if row else None

    def delete_edge(self, edge_id: str):
        self._get_conn().execute("DELETE FROM memory_edges WHERE id = ?", (edge_id,))

    def get_all_edges(self) -> list[MemoryEdge]:
        rows = self._get_conn().execute("SELECT * FROM memory_edges").fetchall()
        return [self._row_to_edge(r) for r in rows]

    def get_edges_from(self, node_id: str) -> list[MemoryEdge]:
        rows = self._get_conn().execute("SELECT * FROM memory_edges WHERE source_id = ?", (node_id,)).fetchall()
        return [self._row_to_edge(r) for r in rows]

    def get_edges_to(self, node_id: str) -> list[MemoryEdge]:
        rows = self._get_conn().execute("SELECT * FROM memory_edges WHERE target_id = ?", (node_id,)).fetchall()
        return [self._row_to_edge(r) for r in rows]

    def get_neighbors(self, node_id: str) -> list[tuple[MemoryEdge, str]]:
        rows = self._get_conn().execute("""
            SELECT *, 'out' as dir FROM memory_edges WHERE source_id = ?
            UNION ALL
            SELECT *, 'in' as dir FROM memory_edges WHERE target_id = ?
        """, (node_id, node_id)).fetchall()
        result = []
        for r in rows:
            edge = self._row_to_edge(r)
            neighbor_id = edge.target_id if edge.source_id == node_id else edge.source_id
            result.append((edge, neighbor_id))
        return result

    def get_active_edges(self, as_of: float = None) -> list[MemoryEdge]:
        """获取在指定时间点有效的边"""
        if as_of is None:
            as_of = time.time()
        rows = self._get_conn().execute("""
            SELECT * FROM memory_edges
            WHERE (valid_from IS NULL OR valid_from <= ?)
              AND (valid_to IS NULL OR valid_to >= ?)
        """, (as_of, as_of)).fetchall()
        return [self._row_to_edge(r) for r in rows]

    # --- 行转换 ---
    def _row_to_node(self, row) -> MemoryNode:
        emb = np.frombuffer(row["embedding"], dtype=np.float32).tolist() if row["embedding"] else None
        return MemoryNode(
            id=row["id"], content=row["content"], memory_type=MemoryType(row["memory_type"]),
            embedding=emb, importance=row["importance"], activation=row["activation"],
            access_count=row["access_count"], last_accessed=row["last_accessed"],
            created_at=row["created_at"], half_life=row["half_life"],
            metadata=json.loads(row["metadata"]), tags=json.loads(row["tags"]), source=row["source"])

    def _row_to_edge(self, row) -> MemoryEdge:
        emb = np.frombuffer(row["embedding"], dtype=np.float32).tolist() if row["embedding"] else None
        return MemoryEdge(
            id=row["id"], source_id=row["source_id"], target_id=row["target_id"],
            description=row["description"], edge_type=EdgeType(row["edge_type"]),
            weight=row["weight"], created_at=row["created_at"], updated_at=row["updated_at"],
            access_count=row["access_count"], embedding=emb,
            valid_from=row["valid_from"], valid_to=row["valid_to"],
            confidence=row["confidence"], metadata=json.loads(row["metadata"]))


# ============================================================
# 5. 核心算法模块
# ============================================================

class SpreadingActivation:
    """ACT-R 扩散激活: 模拟人类联想记忆"""

    def __init__(self, fan_factor=0.5, distance_decay=0.6, max_depth=4, threshold=0.01):
        self.fan_factor = fan_factor
        self.distance_decay = distance_decay
        self.max_depth = max_depth
        self.threshold = threshold

    def propagate(self, seed_ids: list[str], get_neighbors_fn: Callable,
                  seed_activation: float = 1.0) -> dict[str, float]:
        activations = {nid: seed_activation for nid in seed_ids}
        frontier = set(seed_ids)

        for depth in range(self.max_depth):
            if not frontier:
                break
            next_frontier = set()
            decay = self.distance_decay ** (depth + 1)

            for nid in frontier:
                act = activations.get(nid, 0.0)
                if act < self.threshold:
                    continue
                neighbors = get_neighbors_fn(nid)
                if not neighbors:
                    continue
                spread_factor = self.fan_factor / max(len(neighbors), 1)
                for edge, neighbor_id in neighbors:
                    spread = act * spread_factor * edge.weight * decay
                    if spread >= self.threshold:
                        activations[neighbor_id] = activations.get(neighbor_id, 0.0) + spread
                        if neighbor_id not in frontier:
                            next_frontier.add(neighbor_id)
            frontier = next_frontier
        return activations


class ForgettingCurve:
    """艾宾浩斯遗忘曲线 + SM-2 间隔重复"""

    @staticmethod
    def retention_score(last_accessed: float, half_life: float, current_time: float = None) -> float:
        if current_time is None:
            current_time = time.time()
        elapsed = max(current_time - last_accessed, 0.0)
        strength = half_life / math.log(2) if half_life > 0 else 1.0
        return math.exp(-elapsed / strength)

    @staticmethod
    def reinforce(node: MemoryNode, quality: float = 1.0) -> MemoryNode:
        reinforcement = 1.0 + 0.5 * quality
        node.half_life *= reinforcement
        node.half_life = min(node.half_life, 3600 * 24 * 365 * 10)
        node.access_count += 1
        node.last_accessed = time.time()
        return node


class PersonalizedPageRank:
    """Monte Carlo PPR: 局部重要性排序"""

    def __init__(self, damping=0.85, walk_length=50, num_walks=100):
        self.damping = damping
        self.walk_length = walk_length
        self.num_walks = num_walks

    def compute(self, seed_ids: list[str], get_neighbors_fn: Callable) -> dict[str, float]:
        if not seed_ids:
            return {}
        visit_counts: dict[str, int] = defaultdict(int)
        total = 0
        rng = np.random.RandomState(42)

        for _ in range(self.num_walks):
            current = rng.choice(seed_ids)
            visit_counts[current] += 1
            total += 1
            for _ in range(self.walk_length):
                if rng.random() > self.damping:
                    current = rng.choice(seed_ids)
                else:
                    neighbors = get_neighbors_fn(current)
                    if not neighbors:
                        current = rng.choice(seed_ids)
                    else:
                        weights = [e.weight for e, _ in neighbors]
                        tw = sum(weights)
                        if tw == 0:
                            _, current = neighbors[rng.randint(len(neighbors))]
                        else:
                            idx = rng.choice(len(neighbors), p=[w / tw for w in weights])
                            _, current = neighbors[idx]
                visit_counts[current] += 1
                total += 1
        return {nid: c / total for nid, c in visit_counts.items()}


class MemoryConsolidation:
    """记忆整合: 合并高度相似的记忆"""

    def __init__(self, similarity_threshold=0.92):
        self.similarity_threshold = similarity_threshold

    def find_duplicates(self, nodes: list[MemoryNode]) -> list[list[str]]:
        if len(nodes) < 2:
            return []
        visited = [False] * len(nodes)
        groups = []
        for i in range(len(nodes)):
            if visited[i] or not nodes[i].embedding:
                continue
            group = [nodes[i].id]
            for j in range(i + 1, len(nodes)):
                if visited[j] or not nodes[j].embedding:
                    continue
                sim = VectorOps.cosine_similarity(nodes[i].embedding, nodes[j].embedding)
                if sim >= self.similarity_threshold:
                    group.append(nodes[j].id)
                    visited[j] = True
            if len(group) > 1:
                groups.append(group)
                visited[i] = True
        return groups

    def merge_strategy(self, nodes: list[MemoryNode]) -> tuple[MemoryNode, list[str]]:
        if len(nodes) <= 1:
            return nodes[0] if nodes else None, []

        def score(n):
            return len(n.content) * 0.3 + n.access_count * 10 + n.importance * 5

        sorted_n = sorted(nodes, key=score, reverse=True)
        base = sorted_n[0]
        merged = MemoryNode(
            id=base.id, content=base.content, memory_type=base.memory_type,
            embedding=base.embedding,
            importance=max(n.importance for n in nodes),
            access_count=sum(n.access_count for n in nodes),
            last_accessed=max(n.last_accessed for n in nodes),
            created_at=min(n.created_at for n in nodes),
            half_life=max(n.half_life for n in nodes),
            tags=list(set(t for n in nodes for t in n.tags)),
            source=base.source,
            metadata={**base.metadata, "merged_from": [n.id for n in nodes], "merged_at": time.time()},
        )
        embeddings = [n.embedding for n in nodes if n.embedding]
        if embeddings:
            weights = [n.access_count + 1 for n in nodes if n.embedding]
            merged.embedding = VectorOps.weighted_average(embeddings, weights)
        return merged, [n.id for n in sorted_n[1:]]


# ============================================================
# 6. MemoryGraph 主类
# ============================================================

class MemoryGraph:
    def __init__(self, db_path=":memory:", embedding_provider: Optional[EmbeddingProvider] = None,
                 w_vector=0.30, w_bm25=0.15, w_recency=0.10, w_importance=0.10,
                 w_graph=0.15, w_edge=0.20,
                 spreading_decay=0.6, spreading_max_depth=4, consolidation_threshold=0.92):
        self.storage = StorageBackend(db_path)
        self.embedder = embedding_provider or HashEmbeddingProvider()
        self.node_bm25 = BM25Index()
        self.edge_bm25 = BM25Index()  # ★ 边描述专用BM25

        self.spreading = SpreadingActivation(distance_decay=spreading_decay, max_depth=spreading_max_depth)
        self.ppr = PersonalizedPageRank()
        self.consolidation = MemoryConsolidation(consolidation_threshold)

        # 检索权重归一化
        total = w_vector + w_bm25 + w_recency + w_importance + w_graph + w_edge
        self.w_vector = w_vector / total
        self.w_bm25 = w_bm25 / total
        self.w_recency = w_recency / total
        self.w_importance = w_importance / total
        self.w_graph = w_graph / total
        self.w_edge = w_edge / total

        self._node_cache: dict[str, MemoryNode] = {}
        self._rebuild_indices()

    def _rebuild_indices(self):
        self.node_bm25 = BM25Index()
        self.edge_bm25 = BM25Index()
        for node in self.storage.get_all_nodes():
            self.node_bm25.add_document(node.id, node.content)
        for edge in self.storage.get_all_edges():
            if edge.description:
                self.edge_bm25.add_document(edge.id, edge.description)

    # ==================== 写入操作 ====================

    def add(self, content: str, memory_type: MemoryType = MemoryType.SEMANTIC,
            importance: float = 0.5, tags: list = None, metadata: dict = None,
            source: str = "", embedding: list = None, auto_connect: bool = True) -> MemoryNode:
        if not content.strip():
            raise ValueError("记忆内容不能为空")
        if embedding is None:
            embedding = self.embedder.embed(content)

        node = MemoryNode(content=content, memory_type=memory_type, embedding=embedding,
                          importance=max(0.0, min(1.0, importance)),
                          tags=tags or [], metadata=metadata or {}, source=source)
        self.storage.save_node(node)
        self.node_bm25.add_document(node.id, content)
        self._node_cache[node.id] = node

        if auto_connect and embedding:
            self._auto_connect(node)
        logger.info(f"Added node [{node.id[:8]}]: {content[:50]}...")
        return node

    def _auto_connect(self, new_node: MemoryNode, top_k=5, threshold=0.7):
        if not new_node.embedding:
            return
        all_nodes = self.storage.get_all_nodes()
        sims = []
        for existing in all_nodes:
            if existing.id == new_node.id or not existing.embedding:
                continue
            sim = VectorOps.cosine_similarity(new_node.embedding, existing.embedding)
            if sim >= threshold:
                sims.append((existing.id, sim))
        sims.sort(key=lambda x: x[1], reverse=True)

        for neighbor_id, sim in sims[:top_k]:
            # ★ 自动生成边描述
            desc = f"与以下内容语义相关(相似度{sim:.2f}): {new_node.content[:50]}"
            edge = MemoryEdge(
                source_id=new_node.id, target_id=neighbor_id,
                description=desc,
                edge_type=EdgeType.CO_OCCURS if sim < 0.8 else EdgeType.RELATES_TO,
                weight=sim, embedding=self.embedder.embed(desc), confidence=sim)
            self.storage.save_edge(edge)
            self.edge_bm25.add_document(edge.id, desc)

    def connect(self, source_id: str, target_id: str, description: str,
                edge_type: EdgeType = EdgeType.RELATES_TO, weight: float = 1.0,
                valid_from: float = None, valid_to: float = None,
                confidence: float = 1.0, metadata: dict = None) -> MemoryEdge:
        """★ 创建语义化边 (description 必填)"""
        if not description.strip():
            raise ValueError("边描述不能为空, 请提供自然语言关系描述")

        edge = MemoryEdge(
            source_id=source_id, target_id=target_id, description=description,
            edge_type=edge_type, weight=max(0.0, min(1.0, weight)),
            embedding=self.embedder.embed(description),
            valid_from=valid_from, valid_to=valid_to,
            confidence=max(0.0, min(1.0, confidence)),
            metadata=metadata or {})
        self.storage.save_edge(edge)
        self.edge_bm25.add_document(edge.id, description)
        return edge

    def update(self, node_id: str, **kwargs) -> Optional[MemoryNode]:
        node = self.storage.load_node(node_id)
        if not node:
            return None
        for k, v in kwargs.items():
            if hasattr(node, k):
                setattr(node, k, v)
        if "content" in kwargs:
            node.embedding = self.embedder.embed(node.content)
            self.node_bm25.remove_document(node_id)
            self.node_bm25.add_document(node_id, node.content)
        self.storage.save_node(node)
        self._node_cache[node_id] = node
        return node

    def invalidate_edge(self, edge_id: str, valid_to: float = None):
        """使边失效 (时序推理用)"""
        edge = self.storage.load_edge(edge_id)
        if edge:
            edge.valid_to = valid_to or time.time()
            edge.updated_at = time.time()
            self.storage.save_edge(edge)

    def forget(self, node_id: str):
        self.node_bm25.remove_document(node_id)
        # 清理关联边的BM25索引
        for edge in self.storage.get_edges_from(node_id) + self.storage.get_edges_to(node_id):
            self.edge_bm25.remove_document(edge.id)
        self.storage.delete_node(node_id)
        self._node_cache.pop(node_id, None)

    # ==================== 混合检索 (5+1路融合) ====================

    def retrieve(self, query: str, top_k: int = 10, memory_types: list[MemoryType] = None,
                 min_score: float = 0.0, time_range: tuple = None, tags_filter: list = None,
                 include_graph_context: bool = True, include_edge_results: bool = True,
                 as_of: float = None) -> list[RetrievalResult]:
        """
        混合检索: 节点向量 + BM25 + 时序 + 重要性 + 图扩散 + ★边语义
        """
        now = time.time()
        all_nodes = self.storage.get_all_nodes()

        # 过滤
        if memory_types:
            ts = set(mt.value for mt in memory_types)
            all_nodes = [n for n in all_nodes if n.memory_type.value in ts]
        if time_range:
            all_nodes = [n for n in all_nodes if time_range[0] <= n.created_at <= time_range[1]]
        if tags_filter:
            tag_set = set(tags_filter)
            all_nodes = [n for n in all_nodes if tag_set.issubset(set(n.tags))]
        if not all_nodes:
            return []

        query_emb = self.embedder.embed(query)

        # 信号1: 节点向量
        vec_scores = {}
        for n in all_nodes:
            if n.embedding:
                vec_scores[n.id] = (VectorOps.cosine_similarity(query_emb, n.embedding) + 1.0) / 2.0

        # 信号2: 节点BM25
        bm25_raw = self.node_bm25.score(query, top_k=len(all_nodes))
        max_bm25 = max((s for _, s in bm25_raw), default=1.0)
        bm25_scores = {did: s / max_bm25 for did, s in bm25_raw} if max_bm25 > 0 else {}

        # 信号3: 时序衰减
        rec_scores = {n.id: ForgettingCurve.retention_score(n.last_accessed, n.half_life, now) for n in all_nodes}

        # 信号4: 重要性
        imp_scores = {n.id: n.importance for n in all_nodes}

        # 信号5: 图扩散
        graph_scores = {}
        if include_graph_context and vec_scores:
            seeds = sorted(vec_scores.items(), key=lambda x: x[1], reverse=True)[:5]
            seed_ids = [nid for nid, _ in seeds]
            if seed_ids:
                acts = self.spreading.propagate(seed_ids, self.storage.get_neighbors)
                if acts:
                    mx = max(acts.values())
                    graph_scores = {k: v / mx for k, v in acts.items()}

        # ★ 信号6: 边语义检索
        edge_scores = {}
        edge_result_map = {}  # edge_id -> RetrievalResult
        if include_edge_results:
            edge_results = self._retrieve_edges(query, query_emb, top_k=top_k * 2, as_of=as_of)
            for er in edge_results:
                edge_scores[er.edge_id] = er.score
                edge_result_map[er.edge_id] = er

        # 融合节点分数
        results = []
        for n in all_nodes:
            nid = n.id
            final = (self.w_vector * vec_scores.get(nid, 0.0)
                     + self.w_bm25 * bm25_scores.get(nid, 0.0)
                     + self.w_recency * rec_scores.get(nid, 0.0)
                     + self.w_importance * imp_scores.get(nid, 0.0)
                     + self.w_graph * graph_scores.get(nid, 0.0))
            if final >= min_score:
                results.append(RetrievalResult(
                    node=n, score=final,
                    score_breakdown={"vector": vec_scores.get(nid, 0.0), "bm25": bm25_scores.get(nid, 0.0),
                                     "recency": rec_scores.get(nid, 0.0), "importance": imp_scores.get(nid, 0.0),
                                     "graph": graph_scores.get(nid, 0.0)}))

        # ★ 加入边检索结果
        if include_edge_results:
            for er in edge_result_map.values():
                weighted_score = er.score * self.w_edge / max(self.w_edge, 0.01)
                if weighted_score >= min_score:
                    er.score = weighted_score
                    results.append(er)

        results.sort(key=lambda r: r.score, reverse=True)

        # 强化检索到的记忆
        for r in results[:top_k]:
            if not r.is_edge_result:
                ForgettingCurve.reinforce(r.node, quality=r.score)
                self.storage.save_node(r.node)

        return results[:top_k]

    def _retrieve_edges(self, query: str, query_emb: list, top_k: int = 20,
                        as_of: float = None) -> list[RetrievalResult]:
        """★ 边语义检索: 向量 + BM25 + 端点加成"""
        edges = self.storage.get_active_edges(as_of) if as_of else self.storage.get_all_edges()
        scored = []

        # 边BM25
        ebm25_raw = self.edge_bm25.score(query, top_k=len(edges))
        max_ebm25 = max((s for _, s in ebm25_raw), default=1.0)
        ebm25_scores = {eid: s / max_ebm25 for eid, s in ebm25_raw} if max_ebm25 > 0 else {}

        for edge in edges:
            if not edge.description:
                continue
            # 向量
            vs = 0.0
            if edge.embedding:
                vs = (VectorOps.cosine_similarity(query_emb, edge.embedding) + 1.0) / 2.0
            # BM25
            bs = ebm25_scores.get(edge.id, 0.0)
            # 端点加成
            bonus = 0.0
            for nid in [edge.source_id, edge.target_id]:
                cached = self._node_cache.get(nid) or self.storage.load_node(nid)
                if cached and cached.embedding:
                    bonus += VectorOps.cosine_similarity(query_emb, cached.embedding) * 0.05

            final = 0.5 * vs + 0.35 * bs + 0.15 * bonus
            if final > 0.01:
                edge_node = MemoryNode(
                    id=f"edge:{edge.id}",
                    content=f"[{edge.edge_type.value}] {edge.description}",
                    memory_type=MemoryType.SEMANTIC,
                    importance=edge.confidence,
                    created_at=edge.created_at,
                    last_accessed=edge.updated_at,
                    metadata={"is_edge": True, "edge_id": edge.id,
                              "source_id": edge.source_id, "target_id": edge.target_id})
                scored.append(RetrievalResult(
                    node=edge_node, score=final, is_edge_result=True, edge_id=edge.id,
                    score_breakdown={"edge_vector": vs, "edge_bm25": bs, "endpoint_bonus": bonus}))

        scored.sort(key=lambda r: r.score, reverse=True)
        return scored[:top_k]

    def retrieve_context(self, query: str, top_k: int = 5, max_chars: int = 3000) -> str:
        """生成LLM上下文"""
        results = self.retrieve(query, top_k=top_k * 2)
        parts = []
        seen = set()
        total = 0

        type_icons = {"episodic": "📝", "semantic": "🧠", "procedural": "⚙️"}

        for r in results:
            uid = r.edge_id if r.is_edge_result else r.node.id
            if uid in seen:
                continue
            if r.is_edge_result:
                entry = f"🔗 (score:{r.score:.3f}) {r.node.content}"
            else:
                icon = type_icons.get(r.node.memory_type.value, "💾")
                age_h = (time.time() - r.node.created_at) / 3600
                entry = (f"{icon} [{r.node.memory_type.value}] (score:{r.score:.3f})\n"
                         f"   {r.node.content}\n"
                         f"   age:{age_h:.1f}h | accessed:{r.node.access_count}x | imp:{r.node.importance:.2f}")
                if r.node.tags:
                    entry += f"\n   tags: {', '.join(r.node.tags)}"

            if total + len(entry) > max_chars:
                break
            parts.append(entry)
            seen.add(uid)
            total += len(entry)

            # 添加邻居上下文
            if not r.is_edge_result and len(parts) < top_k:
                for edge, nid in self.storage.get_neighbors(r.node.id)[:3]:
                    if nid not in seen and edge.description:
                        rel = f"  └─ [{edge.edge_type.value}] {edge.description[:100]}"
                        if total + len(rel) < max_chars:
                            parts.append(rel)
                            seen.add(nid)
                            total += len(rel)

            if len(parts) >= top_k:
                break

        return f"=== Agent Memory ({len(parts)} items) ===\n" + "\n".join(parts)

    # ==================== 维护操作 ====================

    def consolidate(self) -> dict:
        all_nodes = self.storage.get_all_nodes()
        groups = self.consolidation.find_duplicates(all_nodes)
        stats = {"groups_found": len(groups), "nodes_merged": 0, "nodes_deleted": 0}

        for group_ids in groups:
            nodes = [self.storage.load_node(nid) for nid in group_ids if self.storage.load_node(nid)]
            if len(nodes) < 2:
                continue
            merged, to_delete = self.consolidation.merge_strategy(nodes)
            for del_id in to_delete:
                for edge in self.storage.get_edges_from(del_id):
                    new_edge = MemoryEdge(source_id=merged.id, target_id=edge.target_id,
                                          description=edge.description, edge_type=edge.edge_type,
                                          weight=edge.weight, embedding=edge.embedding, confidence=edge.confidence)
                    self.storage.save_edge(new_edge)
                for edge in self.storage.get_edges_to(del_id):
                    if edge.source_id not in to_delete:
                        new_edge = MemoryEdge(source_id=edge.source_id, target_id=merged.id,
                                              description=edge.description, edge_type=edge.edge_type,
                                              weight=edge.weight, embedding=edge.embedding, confidence=edge.confidence)
                        self.storage.save_edge(new_edge)
                self.node_bm25.remove_document(del_id)
                self.storage.delete_node(del_id)
                self._node_cache.pop(del_id, None)
                stats["nodes_deleted"] += 1
            self.storage.save_node(merged)
            self._node_cache[merged.id] = merged
            stats["nodes_merged"] += 1
        return stats

    def prune(self, min_activation=0.01, max_age_days=None) -> int:
        now = time.time()
        deleted = 0
        for node in self.storage.get_all_nodes():
            ret = ForgettingCurve.retention_score(node.last_accessed, node.half_life, now)
            should = ret < min_activation and node.importance < 0.3
            if max_age_days and (now - node.created_at) / 86400 > max_age_days and ret < 0.1:
                should = True
            if should:
                self.forget(node.id)
                deleted += 1
        return deleted

    def compute_global_importance(self) -> dict[str, float]:
        all_nodes = self.storage.get_all_nodes()
        if not all_nodes:
            return {}
        all_ids = [n.id for n in all_nodes]
        ppr = self.ppr.compute(all_ids, self.storage.get_neighbors)
        for node in all_nodes:
            if node.id in ppr:
                node.importance = 0.6 * ppr[node.id] + 0.4 * node.importance
                self.storage.save_node(node)
        return ppr

    # ==================== 分析 & 导出 ====================

    def get_subgraph(self, center_id: str, depth: int = 2) -> dict:
        visited = set()
        nodes_data, edges_data = [], []
        frontier = {center_id}
        for d in range(depth + 1):
            nxt = set()
            for nid in frontier:
                if nid in visited:
                    continue
                visited.add(nid)
                node = self.storage.load_node(nid)
                if node:
                    nodes_data.append({"id": node.id, "content": node.content[:100],
                                       "type": node.memory_type.value, "importance": node.importance, "depth": d})
                    for edge, neighbor_id in self.storage.get_neighbors(nid):
                        edges_data.append({"source": edge.source_id, "target": edge.target_id,
                                           "type": edge.edge_type.value, "description": edge.description[:80],
                                           "weight": edge.weight})
                        if neighbor_id not in visited:
                            nxt.add(neighbor_id)
            frontier = nxt
        return {"nodes": nodes_data, "edges": edges_data}

    def stats(self) -> dict:
        nodes = self.storage.get_all_nodes()
        edges = self.storage.get_all_edges()
        tc = defaultdict(int)
        ti = 0.0
        for n in nodes:
            tc[n.memory_type.value] += 1
            ti += n.importance
        etc = defaultdict(int)
        for e in edges:
            etc[e.edge_type.value] += 1
        nn = len(nodes)
        return {"total_nodes": nn, "total_edges": len(edges), "node_types": dict(tc),
                "edge_types": dict(etc), "avg_importance": ti / nn if nn else 0,
                "density": len(edges) / (nn * (nn - 1) / 2) if nn > 1 else 0}

    def export_json(self, filepath: str = None) -> str:
        data = {"version": "2.0", "exported_at": datetime.now(timezone.utc).isoformat(),
                "nodes": [], "edges": []}
        for n in self.storage.get_all_nodes():
            nd = asdict(n)
            nd["memory_type"] = n.memory_type.value
            data["nodes"].append(nd)
        for e in self.storage.get_all_edges():
            ed = asdict(e)
            ed["edge_type"] = e.edge_type.value
            data["edges"].append(ed)
        s = json.dumps(data, ensure_ascii=False, indent=2)
        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(s)
        return s


# ============================================================
# 7. Agent 工具接口 (OpenAI Function Calling)
# ============================================================

class MemoryTools:
    TOOL_DEFINITIONS = [
        {"type": "function", "function": {
            "name": "memory_store",
            "description": "将重要信息存储到长期记忆中。用于存储用户偏好、事实、事件等。",
            "parameters": {"type": "object", "properties": {
                "content": {"type": "string", "description": "要记忆的内容"},
                "memory_type": {"type": "string", "enum": ["episodic", "semantic", "procedural"]},
                "importance": {"type": "number", "description": "重要性 0-1"},
                "tags": {"type": "array", "items": {"type": "string"}}},
                "required": ["content"]}}},
        {"type": "function", "function": {
            "name": "memory_recall",
            "description": "从长期记忆中检索相关信息。当需要回忆事实、偏好或过去事件时使用。",
            "parameters": {"type": "object", "properties": {
                "query": {"type": "string", "description": "检索查询"},
                "top_k": {"type": "integer", "description": "返回数量, 默认5"},
                "memory_type": {"type": "string", "enum": ["episodic", "semantic", "procedural"]}},
                "required": ["query"]}}},
        {"type": "function", "function": {
            "name": "memory_relate",
            "description": "在两条记忆之间建立带描述的语义关系。必须提供自然语言关系描述。",
            "parameters": {"type": "object", "properties": {
                "source_id": {"type": "string"}, "target_id": {"type": "string"},
                "description": {"type": "string", "description": "★ 自然语言关系描述, 如'张三在2024年指导李四入门Python'"},
                "relation": {"type": "string", "enum": ["causes", "relates_to", "contradicts", "supports", "sequence"]}},
                "required": ["source_id", "target_id", "description"]}}},
        {"type": "function", "function": {
            "name": "memory_forget",
            "description": "删除指定的记忆。",
            "parameters": {"type": "object", "properties": {
                "memory_id": {"type": "string"}}, "required": ["memory_id"]}}},
    ]

    def __init__(self, mg: MemoryGraph):
        self.mg = mg

    def memory_store(self, content: str, memory_type: str = "semantic",
                     importance: float = 0.5, tags: list = None) -> dict:
        node = self.mg.add(content=content, memory_type=MemoryType(memory_type),
                           importance=importance, tags=tags or [])
        return {"status": "stored", "memory_id": node.id, "preview": content[:100]}

    def memory_recall(self, query: str, top_k: int = 5, memory_type: str = None) -> dict:
        types = [MemoryType(memory_type)] if memory_type else None
        results = self.mg.retrieve(query, top_k=top_k, memory_types=types)
        return {"status": "recalled", "count": len(results), "memories": [
            {"id": r.edge_id if r.is_edge_result else r.node.id,
             "content": r.node.content, "type": "edge" if r.is_edge_result else r.node.memory_type.value,
             "score": round(r.score, 4), "is_relation": r.is_edge_result}
            for r in results]}

    def memory_relate(self, source_id: str, target_id: str, description: str,
                      relation: str = "relates_to") -> dict:
        edge = self.mg.connect(source_id, target_id, description=description, edge_type=EdgeType(relation))
        return {"status": "related", "edge_id": edge.id, "description": description}

    def memory_forget(self, memory_id: str) -> dict:
        node = self.mg.storage.load_node(memory_id)
        if not node:
            return {"status": "not_found"}
        self.mg.forget(memory_id)
        return {"status": "forgotten", "memory_id": memory_id}

    def dispatch(self, tool_name: str, arguments: dict) -> dict:
        methods = {"memory_store": self.memory_store, "memory_recall": self.memory_recall,
                   "memory_relate": self.memory_relate, "memory_forget": self.memory_forget}
        fn = methods.get(tool_name)
        if not fn:
            return {"error": f"Unknown tool: {tool_name}"}
        try:
            return fn(**arguments)
        except Exception as e:
            return {"error": str(e)}


# ============================================================
# 8. 完整演示
# ============================================================

def demo():
    print("=" * 60)
    print("MemoryGraph v2.0 Demo — 语义化边记忆图")
    print("=" * 60)

    mg = MemoryGraph(db_path=":memory:")

    # 添加记忆节点
    print("\n📝 添加记忆...")
    n1 = mg.add("张三是Python后端工程师, 主要使用FastAPI和Django",
                MemoryType.SEMANTIC, 0.8, ["user_profile", "python"])
    n2 = mg.add("张三偏好PostgreSQL而非MySQL, 因为JSON支持更好",
                MemoryType.SEMANTIC, 0.7, ["preference", "database"])
    n3 = mg.add("2024-03-15: 项目从Django迁移到FastAPI, 性能提升3倍",
                MemoryType.EPISODIC, 0.6, ["project", "migration"])
    n4 = mg.add("张三对微服务架构感兴趣, 正在学习Kubernetes",
                MemoryType.SEMANTIC, 0.5, ["interest", "k8s"])
    n5 = mg.add("部署流程: 1.运行测试 2.构建Docker镜像 3.推送Registry 4.K8s滚动更新",
                MemoryType.PROCEDURAL, 0.6, ["deployment"])

    # ★ 创建语义化边 (关键!)
    print("\n🔗 创建语义化边...")
    mg.connect(n1.id, n2.id,
               description="张三作为Python工程师, 在数据库选型上偏好PostgreSQL",
               edge_type=EdgeType.RELATES_TO, weight=0.9)
    mg.connect(n1.id, n3.id,
               description="张三在2024年3月将项目从Django迁移到了FastAPI框架",
               edge_type=EdgeType.SEQUENCE, weight=0.85)
    mg.connect(n2.id, n3.id,
               description="PostgreSQL的JSON支持是促使张三迁移到FastAPI的原因之一",
               edge_type=EdgeType.CAUSES, weight=0.7)
    mg.connect(n4.id, n5.id,
               description="张三学习Kubernetes是为了掌握微服务部署流程",
               edge_type=EdgeType.RELATES_TO, weight=0.8)

    # 检索测试
    print("\n🔍 检索: '张三的技术栈和偏好'")
    for i, r in enumerate(mg.retrieve("张三的技术栈和偏好", top_k=6)):
        tag = "🔗EDGE" if r.is_edge_result else "📦NODE"
        print(f"  [{i + 1}] {tag} score={r.score:.3f} | {r.node.content[:70]}")

    print("\n🔍 检索: '谁教了张三?' (关系型查询, 边检索优势)")
    for i, r in enumerate(mg.retrieve("数据库选择原因", top_k=5)):
        tag = "🔗EDGE" if r.is_edge_result else "📦NODE"
        print(f"  [{i + 1}] {tag} score={r.score:.3f} | {r.node.content[:70]}")

    # LLM上下文
    print("\n📋 LLM上下文:")
    print(mg.retrieve_context("张三的项目迁移", top_k=4))

    # Agent工具
    print("\n🤖 Agent工具调用:")
    tools = MemoryTools(mg)
    print(json.dumps(tools.memory_recall("Kubernetes部署"), ensure_ascii=False, indent=2)[:400])

    # 统计
    print("\n📊 统计:")
    import pprint
    pprint.pprint(mg.stats())

    # 子图
    print("\n🌐 以张三为中心的子图:")
    sg = mg.get_subgraph(n1.id, depth=2)
    print(f"  {len(sg['nodes'])} nodes, {len(sg['edges'])} edges")
    for e in sg["edges"]:
        print(f"    {e['source'][:8]}→{e['target'][:8]} [{e['type']}] {e['description']}")

    print("\n✅ Demo完成!")


if __name__ == "__main__":
    demo()
