"""
memory_graph.py — AI Agent 记忆图工具
======================================
核心算法：
  1. 时序知识图谱（Temporal Knowledge Graph）
  2. Ebbinghaus 遗忘曲线 + 复习增强
  3. Personalized PageRank 重要性评分
  4. 向量语义检索（余弦相似度）
  5. 混合排序（Hybrid Retrieval）
  6. Louvain 社区发现
  7. 记忆合并去重
  8. JSON 持久化

依赖：pip install numpy
可选（提升嵌入质量）：pip install sentence-transformers
可选（LLM嵌入）：pip install openai
"""

import math
import json
import uuid
import heapq
import hashlib
import time as _time
from dataclasses import dataclass, field, asdict
from typing import Optional, Any
from collections import defaultdict
from enum import Enum

import numpy as np


# ════════════════════════════════════════════════════════════════
# 第一部分：数据模型
# ════════════════════════════════════════════════════════════════

class NodeKind(Enum):
    ENTITY = "entity"       # 实体（人、物、概念）
    EVENT = "event"         # 事件（发生了什么）
    FACT = "fact"           # 事实性陈述
    EPISODE = "episode"     # 对话/经历片段


@dataclass
class MemoryNode:
    """记忆图的顶点"""
    id: str                              # 唯一标识
    text: str                            # 顶点携带的文字内容
    kind: str = NodeKind.FACT.value      # 顶点类型
    embedding: Optional[list] = None     # 语义嵌入向量
    created_at: float = 0.0              # 创建时间戳（秒）
    last_accessed: float = 0.0           # 最后一次被访问/强化的时间
    access_count: int = 0                # 被访问次数（用于计算记忆强度）
    importance: float = 1.0              # 初始重要性
    metadata: dict = field(default_factory=dict)  # 扩展元数据
    is_active: bool = True               # 是否仍然有效（用于时序失效）

    def __post_init__(self):
        if self.created_at == 0.0:
            self.created_at = _time.time()
        if self.last_accessed == 0.0:
            self.last_accessed = self.created_at


@dataclass
class MemoryEdge:
    """记忆图的边（有向）"""
    id: str                                # 唯一标识
    source: str                            # 源顶点 id
    target: str                            # 目标顶点 id
    text: str                              # 边上的文字（关系描述）
    weight: float = 1.0                    # 边权重
    embedding: Optional[list] = None       # 关系语义嵌入
    created_at: float = 0.0                # 创建时间
    valid_from: float = 0.0                # 该关系从何时起有效
    valid_until: Optional[float] = None    # 该关系何时失效（None=仍有效）
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.created_at == 0.0:
            self.created_at = _time.time()
        if self.valid_from == 0.0:
            self.valid_from = self.created_at

    @property
    def is_active(self) -> bool:
        if self.valid_until is not None and _time.time() > self.valid_until:
            return False
        return True


# ════════════════════════════════════════════════════════════════
# 第二部分：嵌入器（Embedding Provider）
# ════════════════════════════════════════════════════════════════

class EmbeddingProvider:
    """嵌入器基类"""

    def embed(self, text: str) -> list[float]:
        raise NotImplementedError

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(t) for t in texts]


class HashEmbedder(EmbeddingProvider):
    """
    基于哈希的轻量嵌入（无需外部依赖）。
    将文本映射到固定维度向量。适用于离线/无 API 环境。
    使用多哈希 + 字符 n-gram 生成伪嵌入。
    """

    def __init__(self, dim: int = 128):
        self.dim = dim

    def embed(self, text: str) -> list[float]:
        vec = np.zeros(self.dim, dtype=np.float32)
        # 使用字符级 bigram + trigram 哈希
        text_lower = text.lower().strip()
        for n in (2, 3):
            for i in range(len(text_lower) - n + 1):
                ngram = text_lower[i:i + n]
                h = int(hashlib.md5(ngram.encode()).hexdigest(), 16)
                idx = h % self.dim
                sign = 1.0 if (h // self.dim) % 2 == 0 else -1.0
                vec[idx] += sign * (1.0 / math.sqrt(n))
        # L2 归一化
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()


class SentenceTransformerEmbedder(EmbeddingProvider):
    """使用 sentence-transformers 的高质量本地嵌入"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "请安装 sentence-transformers: pip install sentence-transformers"
            )
        self.model = SentenceTransformer(model_name)

    def embed(self, text: str) -> list[float]:
        vec = self.model.encode(text, normalize_embeddings=True)
        return vec.tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        vecs = self.model.encode(texts, normalize_embeddings=True)
        return [v.tolist() for v in vecs]


class OpenAIEmbedder(EmbeddingProvider):
    """使用 OpenAI API 的嵌入"""

    def __init__(self, model: str = "text-embedding-3-small", api_key: str = None):
        try:
            import openai
        except ImportError:
            raise ImportError("请安装 openai: pip install openai")
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model

    def embed(self, text: str) -> list[float]:
        resp = self.client.embeddings.create(input=text, model=self.model)
        return resp.data[0].embedding

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        resp = self.client.embeddings.create(input=texts, model=self.model)
        return [d.embedding for d in resp.data]


# ════════════════════════════════════════════════════════════════
# 第三部分：记忆图核心
# ════════════════════════════════════════════════════════════════

class MemoryGraph:
    """
    AI Agent 记忆图
    
    核心设计：
    - 顶点 = 记忆节点（带文字 + 嵌入 + 时间戳）
    - 边   = 关系边（带文字描述 + 时序有效性）
    - 检索 = 语义相似 × 图重要性 × 时间衰减 混合排序
    """

    def __init__(
        self,
        embedder: Optional[EmbeddingProvider] = None,
        # Ebbinghaus 遗忘曲线参数
        half_life_seconds: float = 86400.0,   # 默认半衰期 1 天
        review_boost: float = 1.5,            # 每次复习的增强因子
        max_review_multiplier: float = 10.0,  # 复习增强上限
        # PageRank 参数
        pagerank_damping: float = 0.85,
        pagerank_iterations: int = 50,
        pagerank_tolerance: float = 1e-6,
        # 混合检索权重
        semantic_weight: float = 0.4,
        pagerank_weight: float = 0.3,
        recency_weight: float = 0.3,
    ):
        self.embedder = embedder or HashEmbedder(dim=128)

        # 遗忘曲线参数
        self.half_life = half_life_seconds
        self.review_boost = review_boost
        self.max_review_multiplier = max_review_multiplier

        # PageRank 参数
        self.pr_damping = pagerank_damping
        self.pr_iterations = pagerank_iterations
        self.pr_tolerance = pagerank_tolerance

        # 检索权重
        self.semantic_weight = semantic_weight
        self.pagerank_weight = pagerank_weight
        self.recency_weight = recency_weight

        # 图数据结构
        self._nodes: dict[str, MemoryNode] = {}
        self._edges: dict[str, MemoryEdge] = {}
        self._adj: dict[str, list[str]] = defaultdict(list)       # 出边邻接表
        self._radj: dict[str, list[str]] = defaultdict(list)      # 入边邻接表

        # 缓存
        self._pagerank_cache: Optional[dict[str, float]] = None
        self._communities_cache: Optional[dict[str, int]] = None

    # ────────────────────────────────────────────────────────────
    # 基础 CRUD
    # ────────────────────────────────────────────────────────────

    def add_node(
        self,
        text: str,
        kind: str = NodeKind.FACT.value,
        node_id: Optional[str] = None,
        importance: float = 1.0,
        metadata: Optional[dict] = None,
    ) -> MemoryNode:
        """添加记忆顶点（自动计算语义嵌入）"""
        nid = node_id or str(uuid.uuid4())[:12]
        if nid in self._nodes:
            raise ValueError(f"节点 {nid} 已存在，请使用 update_node 更新")

        embedding = self.embedder.embed(text)
        node = MemoryNode(
            id=nid,
            text=text,
            kind=kind,
            embedding=embedding,
            importance=importance,
            metadata=metadata or {},
        )
        self._nodes[nid] = node
        self._invalidate_cache()
        return node

    def add_edge(
        self,
        source: str,
        target: str,
        text: str,
        edge_id: Optional[str] = None,
        weight: float = 1.0,
        valid_from: Optional[float] = None,
        valid_until: Optional[float] = None,
        metadata: Optional[dict] = None,
    ) -> MemoryEdge:
        """添加关系边（自动计算语义嵌入）"""
        if source not in self._nodes:
            raise ValueError(f"源节点 {source} 不存在")
        if target not in self._nodes:
            raise ValueError(f"目标节点 {target} 不存在")

        eid = edge_id or str(uuid.uuid4())[:12]
        embedding = self.embedder.embed(text)

        now = _time.time()
        edge = MemoryEdge(
            id=eid,
            source=source,
            target=target,
            text=text,
            weight=weight,
            embedding=embedding,
            created_at=now,
            valid_from=valid_from or now,
            valid_until=valid_until,
            metadata=metadata or {},
        )
        self._edges[eid] = edge
        self._adj[source].append(eid)
        self._radj[target].append(eid)
        self._invalidate_cache()
        return edge

    def update_node(self, node_id: str, text: Optional[str] = None,
                    importance: Optional[float] = None,
                    metadata: Optional[dict] = None) -> MemoryNode:
        """更新节点（若文字变化则重新计算嵌入）"""
        node = self._nodes.get(node_id)
        if not node:
            raise ValueError(f"节点 {node_id} 不存在")
        if text is not None and text != node.text:
            node.text = text
            node.embedding = self.embedder.embed(text)
        if importance is not None:
            node.importance = importance
        if metadata is not None:
            node.metadata.update(metadata)
        self._invalidate_cache()
        return node

    def invalidate_edge(self, edge_id: str, valid_until: Optional[float] = None):
        """使一条边失效（时序知识图谱核心操作）"""
        edge = self._edges.get(edge_id)
        if not edge:
            raise ValueError(f"边 {edge_id} 不存在")
        edge.valid_until = valid_until or _time.time()
        self._invalidate_cache()

    def invalidate_node(self, node_id: str):
        """使一个节点失效（软删除）"""
        node = self._nodes.get(node_id)
        if not node:
            raise ValueError(f"节点 {node_id} 不存在")
        node.is_active = False

    def get_node(self, node_id: str) -> Optional[MemoryNode]:
        return self._nodes.get(node_id)

    def get_edge(self, edge_id: str) -> Optional[MemoryEdge]:
        return self._edges.get(edge_id)

    def get_neighbors(self, node_id: str, direction: str = "both",
                      active_only: bool = True) -> list[tuple[MemoryEdge, MemoryNode]]:
        """获取邻居节点及其关系边"""
        result = []
        if direction in ("out", "both"):
            for eid in self._adj.get(node_id, []):
                edge = self._edges[eid]
                if active_only and not edge.is_active:
                    continue
                target = self._nodes.get(edge.target)
                if target and (not active_only or target.is_active):
                    result.append((edge, target))
        if direction in ("in", "both"):
            for eid in self._radj.get(node_id, []):
                edge = self._edges[eid]
                if active_only and not edge.is_active:
                    continue
                source = self._nodes.get(edge.source)
                if source and (not active_only or source.is_active):
                    result.append((edge, source))
        return result

    @property
    def node_count(self) -> int:
        return sum(1 for n in self._nodes.values() if n.is_active)

    @property
    def edge_count(self) -> int:
        return sum(1 for e in self._edges.values() if e.is_active)

    # ────────────────────────────────────────────────────────────
    # 记忆强度计算（Ebbinghaus 遗忘曲线）
    # ────────────────────────────────────────────────────────────

    def memory_strength(self, node: MemoryNode, now: Optional[float] = None) -> float:
        """
        基于 Ebbinghaus 遗忘曲线计算记忆强度。
        
        公式: S(t) = base_strength * exp(-λ * t)
        其中:
          - base_strength 随复习次数指数增长
          - λ = ln(2) / half_life
          - t = 距上次访问的时间差
          - 复习使半衰期增长（间隔重复效应）
        """
        now = now or _time.time()
        elapsed = max(0, now - node.last_accessed)

        # 复习增强：每复习一次，半衰期乘以 boost（有上限）
        review_mult = min(
            self.review_boost ** node.access_count,
            self.max_review_multiplier,
        )
        effective_half_life = self.half_life * review_mult

        # 遗忘衰减
        decay_rate = math.log(2) / effective_half_life
        strength = math.exp(-decay_rate * elapsed)

        return strength

    def touch_node(self, node_id: str):
        """
        复习/强化一个记忆节点。
        增加访问计数，更新最后访问时间，相当于"复习"。
        """
        node = self._nodes.get(node_id)
        if not node:
            raise ValueError(f"节点 {node_id} 不存在")
        node.last_accessed = _time.time()
        node.access_count += 1

    # ────────────────────────────────────────────────────────────
    # PageRank 重要性评分
    # ────────────────────────────────────────────────────────────

    def compute_pagerank(self, personalization: Optional[dict[str, float]] = None
                         ) -> dict[str, float]:
        """
        计算（个性化）PageRank。
        
        若提供 personalization（节点id -> 偏好权重），则计算
        Personalized PageRank，使与查询相关的节点获得更高分。
        
        算法：迭代法（幂迭代），支持悬挂节点处理。
        """
        active_nodes = [nid for nid, n in self._nodes.items() if n.is_active]
        n = len(active_nodes)
        if n == 0:
            return {}

        node_idx = {nid: i for i, nid in enumerate(active_nodes)}
        d = self.pr_damping

        # 构建转移概率矩阵（稀疏表示）
        # out_weight[i] = 从 i 出发的所有边权重之和
        out_weight = np.zeros(n, dtype=np.float64)
        transitions: list[tuple[int, int, float]] = []

        for eid, edge in self._edges.items():
            if not edge.is_active:
                continue
            if edge.source not in node_idx or edge.target not in node_idx:
                continue
            si = node_idx[edge.source]
            ti = node_idx[edge.target]
            w = edge.weight
            transitions.append((si, ti, w))
            out_weight[si] += w

        # 偏好向量
        if personalization:
            pv = np.zeros(n, dtype=np.float64)
            for nid, weight in personalization.items():
                if nid in node_idx:
                    pv[node_idx[nid]] = weight
            pv_sum = pv.sum()
            if pv_sum > 0:
                pv = pv / pv_sum
            else:
                pv = np.ones(n, dtype=np.float64) / n
        else:
            pv = np.ones(n, dtype=np.float64) / n

        # 幂迭代
        pr = np.ones(n, dtype=np.float64) / n
        for _ in range(self.pr_iterations):
            pr_new = np.zeros(n, dtype=np.float64)

            # 传播
            for si, ti, w in transitions:
                if out_weight[si] > 0:
                    pr_new[ti] += d * pr[si] * (w / out_weight[si])

            # 悬挂节点（无出边）的概率均匀分配
            dangling_sum = sum(pr[i] for i in range(n) if out_weight[i] == 0)
            dangling_contrib = d * dangling_sum / n

            # 随机跳转
            pr_new = pr_new + dangling_contrib + (1 - d) * pv

            # 归一化
            pr_sum = pr_new.sum()
            if pr_sum > 0:
                pr_new = pr_new / pr_sum

            # 收敛检查
            diff = np.abs(pr_new - pr).sum()
            pr = pr_new
            if diff < self.pr_tolerance:
                break

        result = {}
        for nid, i in node_idx.items():
            result[nid] = float(pr[i])
        return result

    def _invalidate_cache(self):
        self._pagerank_cache = None
        self._communities_cache = None

    def _ensure_pagerank(self):
        if self._pagerank_cache is None:
            self._pagerank_cache = self.compute_pagerank()

    # ────────────────────────────────────────────────────────────
    # 社区发现（简化版 Louvain）
    # ────────────────────────────────────────────────────────────

    def detect_communities(self) -> dict[str, int]:
        """
        基于标签传播的社区发现算法（近似 Louvain 效果，实现更简洁）。
        
        每个节点被赋予一个社区 id，相同社区 id 的节点属于同一簇。
        用于记忆聚类、主题提取。
        """
        active_nodes = [nid for nid, n in self._nodes.items() if n.is_active]
        if not active_nodes:
            return {}

        # 初始化：每个节点一个独立社区
        community = {nid: i for i, nid in enumerate(active_nodes)}

        # 构建无向加权邻接（用于标签传播）
        neighbors: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        for eid, edge in self._edges.items():
            if not edge.is_active:
                continue
            if edge.source in community and edge.target in community:
                neighbors[edge.source][edge.target] += edge.weight
                neighbors[edge.target][edge.source] += edge.weight

        # 迭代标签传播
        max_iters = 100
        for _ in range(max_iters):
            changed = False
            # 随机顺序（使用固定种子保证可复现）
            import random
            order = active_nodes[:]
            random.shuffle(order)

            for nid in order:
                if not neighbors[nid]:
                    continue
                # 统计邻居社区权重
                community_weights: dict[int, float] = defaultdict(float)
                for neighbor_id, w in neighbors[nid].items():
                    comm = community[neighbor_id]
                    community_weights[comm] += w

                if not community_weights:
                    continue

                # 选择权重最大的社区
                best_comm = max(community_weights, key=community_weights.get)
                if community[nid] != best_comm:
                    community[nid] = best_comm
                    changed = True

            if not changed:
                break

        # 重新编号社区（连续整数）
        unique_comms = {}
        next_id = 0
        result = {}
        for nid, comm in community.items():
            if comm not in unique_comms:
                unique_comms[comm] = next_id
                next_id += 1
            result[nid] = unique_comms[comm]

        self._communities_cache = result
        return result

    def get_community_nodes(self) -> dict[int, list[str]]:
        """获取社区 -> 节点列表的映射"""
        communities = self._communities_cache or self.detect_communities()
        result: dict[int, list[str]] = defaultdict(list)
        for nid, comm in communities.items():
            result[comm].append(nid)
        return dict(result)

    # ────────────────────────────────────────────────────────────
    # 语义检索
    # ────────────────────────────────────────────────────────────

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        """余弦相似度"""
        va = np.array(a, dtype=np.float32)
        vb = np.array(b, dtype=np.float32)
        dot = float(np.dot(va, vb))
        norm_a = float(np.linalg.norm(va))
        norm_b = float(np.linalg.norm(vb))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def semantic_search_nodes(self, query: str, top_k: int = 10
                              ) -> list[tuple[MemoryNode, float]]:
        """基于语义相似度搜索节点"""
        query_emb = self.embedder.embed(query)
        scores = []
        for node in self._nodes.values():
            if not node.is_active or node.embedding is None:
                continue
            sim = self._cosine_similarity(query_emb, node.embedding)
            scores.append((node, sim))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    def semantic_search_edges(self, query: str, top_k: int = 10
                              ) -> list[tuple[MemoryEdge, float]]:
        """基于语义相似度搜索边"""
        query_emb = self.embedder.embed(query)
        scores = []
        for edge in self._edges.values():
            if not edge.is_active or edge.embedding is None:
                continue
            sim = self._cosine_similarity(query_emb, edge.embedding)
            scores.append((edge, sim))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    # ────────────────────────────────────────────────────────────
    # 图遍历
    # ────────────────────────────────────────────────────────────

    def bfs_traverse(self, start_id: str, max_depth: int = 3,
                     max_nodes: int = 50) -> list[MemoryNode]:
        """广度优先遍历，返回可达节点"""
        visited = set()
        result = []
        queue = [(start_id, 0)]
        visited.add(start_id)

        while queue and len(result) < max_nodes:
            nid, depth = queue.pop(0)
            node = self._nodes.get(nid)
            if node and node.is_active:
                result.append(node)
            if depth >= max_depth:
                continue
            for edge, neighbor in self.get_neighbors(nid, active_only=True):
                if neighbor.id not in visited:
                    visited.add(neighbor.id)
                    queue.append((neighbor.id, depth + 1))

        return result

    def find_shortest_path(self, start_id: str, end_id: str,
                           max_hops: int = 10) -> Optional[list[str]]:
        """BFS 最短路径（返回节点 id 列表）"""
        if start_id == end_id:
            return [start_id]

        visited = {start_id}
        queue = [(start_id, [start_id])]

        while queue:
            nid, path = queue.pop(0)
            if len(path) > max_hops:
                continue
            for edge, neighbor in self.get_neighbors(nid, active_only=True):
                if neighbor.id in visited:
                    continue
                new_path = path + [neighbor.id]
                if neighbor.id == end_id:
                    return new_path
                visited.add(neighbor.id)
                queue.append((neighbor.id, new_path))

        return None

    # ────────────────────────────────────────────────────────────
    # 混合检索（Hybrid Retrieval）— 核心算法
    # ────────────────────────────────────────────────────────────

    def search(self, query: str, top_k: int = 10,
               include_edges: bool = True,
               min_strength: float = 0.0,
               expand_neighbors: bool = True,
               max_expand_depth: int = 1) -> dict:
        """
        混合检索：综合语义相似度 + PageRank 重要性 + 时间衰减。
        
        返回格式:
        {
            "nodes": [{"node": MemoryNode, "score": float, "breakdown": {...}}, ...],
            "edges": [{"edge": MemoryEdge, "score": float}, ...],
            "context": str   # 可直接喂给 LLM 的文本摘要
        }
        
        算法：
          final_score = w_sem * semantic_sim
                      + w_pr  * normalized_pagerank
                      + w_rec * recency_score
        
        recency_score = memory_strength(node)  # Ebbinghaus
        """
        now = _time.time()

        # 1. 语义检索
        semantic_results = self.semantic_search_nodes(query, top_k=top_k * 3)

        # 2. PageRank（如果有语义匹配的节点，做个性化 PageRank）
        if semantic_results:
            top_node_ids = {n.id: s for n, s in semantic_results[:5]}
            personalization = top_node_ids
        else:
            personalization = None
        pagerank = self.compute_pagerank(personalization)

        # 归一化 PageRank
        pr_values = list(pagerank.values())
        pr_max = max(pr_values) if pr_values else 1.0
        pr_min = min(pr_values) if pr_values else 0.0
        pr_range = pr_max - pr_min if pr_max > pr_min else 1.0

        # 3. 计算最终分数
        scored_nodes = []
        for node, sem_sim in semantic_results:
            # 记忆强度（时间衰减）
            strength = self.memory_strength(node, now)
            if strength < min_strength:
                continue

            # 归一化 PageRank
            pr_score = (pagerank.get(node.id, 0) - pr_min) / pr_range

            # 综合得分
            final = (
                self.semantic_weight * sem_sim +
                self.pagerank_weight * pr_score +
                self.recency_weight * strength
            )

            scored_nodes.append({
                "node": node,
                "score": final,
                "breakdown": {
                    "semantic": sem_sim,
                    "pagerank": pr_score,
                    "strength": strength,
                },
            })

        scored_nodes.sort(key=lambda x: x["score"], reverse=True)
        top_nodes = scored_nodes[:top_k]

        # 4. 复习被检索到的节点
        for item in top_nodes:
            self.touch_node(item["node"].id)

        # 5. 邻居扩展（收集上下文）
        expanded_nodes = set(item["node"].id for item in top_nodes)
        context_edges: list[tuple[MemoryEdge, MemoryNode, str]] = []

        if expand_neighbors:
            for item in top_nodes:
                nid = item["node"].id
                depth = 0
                frontier = [nid]
                visited_expand = {nid}
                while frontier and depth < max_expand_depth:
                    next_frontier = []
                    for fnid in frontier:
                        for edge, neighbor in self.get_neighbors(fnid, active_only=True):
                            if neighbor.id not in visited_expand:
                                visited_expand.add(neighbor.id)
                                expanded_nodes.add(neighbor.id)
                                context_edges.append((edge, neighbor, fnid))
                                next_frontier.append(neighbor.id)
                    frontier = next_frontier
                    depth += 1

        # 6. 边检索
        edge_results = []
        if include_edges:
            edge_results = self.semantic_search_edges(query, top_k=top_k)

        # 7. 生成上下文文本
        context = self._build_context(top_nodes, context_edges)

        return {
            "nodes": top_nodes,
            "edges": [{"edge": e, "score": s} for e, s in edge_results],
            "context": context,
        }

    def _build_context(self, top_nodes: list[dict],
                       context_edges: list[tuple[MemoryEdge, MemoryNode, str]]) -> str:
        """将检索结果格式化为 LLM 可用的上下文文本"""
        lines = ["=== 检索到的记忆 ==="]

        for i, item in enumerate(top_nodes, 1):
            node = item["node"]
            score = item["score"]
            lines.append(
                f"[{i}] ({node.kind}, score={score:.3f}) "
                f"[{node.id}] {node.text}"
            )

        if context_edges:
            lines.append("\n=== 关联上下文 ===")
            for edge, neighbor, from_id in context_edges:
                from_node = self._nodes.get(from_id)
                from_text = from_node.text[:30] if from_node else from_id
                lines.append(
                    f"  {from_text} --[{edge.text}]--> "
                    f"[{neighbor.id}] {neighbor.text}"
                )

        return "\n".join(lines)

    # ────────────────────────────────────────────────────────────
    # 记忆合并去重
    # ────────────────────────────────────────────────────────────

    def merge_similar_nodes(self, threshold: float = 0.92) -> list[tuple[str, str]]:
        """
        合并语义高度相似的节点。
        
        算法：
        1. 计算所有活跃节点对的余弦相似度
        2. 超过阈值的节点对进行合并
        3. 保留创建时间更早的节点，将较新节点的边迁移过去
        4. 新节点标记为失效
        
        返回: [(merged_from_id, merged_into_id), ...]
        """
        active = [(nid, n) for nid, n in self._nodes.items()
                  if n.is_active and n.embedding is not None]
        merged = []
        removed = set()

        for i in range(len(active)):
            if active[i][0] in removed:
                continue
            nid_a, node_a = active[i]
            for j in range(i + 1, len(active)):
                if active[j][0] in removed:
                    continue
                nid_b, node_b = active[j]
                sim = self._cosine_similarity(node_a.embedding, node_b.embedding)
                if sim >= threshold:
                    # 保留更早创建的节点
                    if node_a.created_at <= node_b.created_at:
                        keep, remove = nid_a, nid_b
                    else:
                        keep, remove = nid_b, nid_a

                    self._merge_into(keep, remove)
                    removed.add(remove)
                    merged.append((remove, keep))

        return merged

    def _merge_into(self, keep_id: str, remove_id: str):
        """将 remove_id 的边和访问统计合并到 keep_id"""
        keep_node = self._nodes[keep_id]
        remove_node = self._nodes[remove_id]

        # 合并访问统计
        keep_node.access_count += remove_node.access_count
        keep_node.last_accessed = max(keep_node.last_accessed, remove_node.last_accessed)
        keep_node.importance = max(keep_node.importance, remove_node.importance)

        # 迁移边
        for eid in list(self._adj.get(remove_id, [])):
            edge = self._edges[eid]
            if edge.is_active:
                edge.source = keep_id
                # 重新挂载邻接表
                self._adj[remove_id].remove(eid)
                self._adj[keep_id].append(eid)

        for eid in list(self._radj.get(remove_id, [])):
            edge = self._edges[eid]
            if edge.is_active:
                edge.target = keep_id
                self._radj[remove_id].remove(eid)
                self._radj[keep_id].append(eid)

        # 标记为失效
        remove_node.is_active = False
        self._invalidate_cache()

    # ────────────────────────────────────────────────────────────
    # 记忆整合（睡眠巩固）
    # ────────────────────────────────────────────────────────────

    def consolidate(self, similarity_threshold: float = 0.92,
                    min_strength: float = 0.05) -> dict:
        """
        记忆整合操作（类似人类睡眠期的记忆巩固）。
        
        执行以下操作：
        1. 合并高度相似的节点（去重）
        2. 清理低于最小强度的衰老记忆
        3. 重新计算社区结构
        4. 重新计算 PageRank
        
        建议定期调用（如每 N 次对话后）。
        """
        now = _time.time()

        # 1. 合并相似节点
        merged = self.merge_similar_nodes(threshold=similarity_threshold)

        # 2. 清理衰老记忆
        pruned = []
        for nid, node in list(self._nodes.items()):
            if not node.is_active:
                continue
            strength = self.memory_strength(node, now)
            if strength < min_strength and node.access_count < 2:
                node.is_active = False
                pruned.append(nid)

        # 3. 重新计算社区
        communities = self.detect_communities()

        # 4. 重新计算 PageRank
        pagerank = self.compute_pagerank()
        self._pagerank_cache = pagerank

        return {
            "merged_count": len(merged),
            "merged_pairs": merged,
            "pruned_count": len(pruned),
            "pruned_ids": pruned,
            "community_count": len(set(communities.values())),
            "active_nodes": self.node_count,
            "active_edges": self.edge_count,
        }

    # ────────────────────────────────────────────────────────────
    # 子图提取
    # ────────────────────────────────────────────────────────────

    def extract_subgraph(self, node_ids: list[str], max_hops: int = 2
                         ) -> dict:
        """
        以给定节点为中心，提取局部子图。
        返回子图的节点、边和文本描述。
        """
        collected_nodes = set()
        collected_edges = set()

        for nid in node_ids:
            collected_nodes.add(nid)
            frontier = [nid]
            visited = {nid}
            for depth in range(max_hops):
                next_frontier = []
                for fnid in frontier:
                    for edge, neighbor in self.get_neighbors(fnid, active_only=True):
                        collected_edges.add(edge.id)
                        collected_nodes.add(neighbor.id)
                        if neighbor.id not in visited:
                            visited.add(neighbor.id)
                            next_frontier.append(neighbor.id)
                frontier = next_frontier
                if not frontier:
                    break

        nodes = [self._nodes[nid] for nid in collected_nodes if nid in self._nodes]
        edges = [self._edges[eid] for eid in collected_edges if eid in self._edges]

        return {
            "nodes": nodes,
            "edges": edges,
            "node_count": len(nodes),
            "edge_count": len(edges),
        }

    # ────────────────────────────────────────────────────────────
    # 持久化
    # ────────────────────────────────────────────────────────────

    def save(self, filepath: str):
        """保存记忆图到 JSON 文件"""
        data = {
            "nodes": [],
            "edges": [],
            "config": {
                "half_life": self.half_life,
                "review_boost": self.review_boost,
                "max_review_multiplier": self.max_review_multiplier,
                "pr_damping": self.pr_damping,
                "semantic_weight": self.semantic_weight,
                "pagerank_weight": self.pagerank_weight,
                "recency_weight": self.recency_weight,
            },
        }
        for node in self._nodes.values():
            nd = asdict(node)
            data["nodes"].append(nd)
        for edge in self._edges.values():
            ed = asdict(edge)
            data["edges"].append(ed)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self, filepath: str):
        """从 JSON 文件加载记忆图"""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        self._nodes.clear()
        self._edges.clear()
        self._adj.clear()
        self._radj.clear()
        self._invalidate_cache()

        for nd in data.get("nodes", []):
            node = MemoryNode(**nd)
            self._nodes[node.id] = node

        for ed in data.get("edges", []):
            edge = MemoryEdge(**ed)
            self._edges[edge.id] = edge
            self._adj[edge.source].append(edge.id)
            self._radj[edge.target].append(edge.id)

    # ────────────────────────────────────────────────────────────
    # 统计与调试
    # ────────────────────────────────────────────────────────────

    def stats(self) -> dict:
        """返回记忆图的统计信息"""
        active_nodes = [n for n in self._nodes.values() if n.is_active]
        active_edges = [e for e in self._edges.values() if e.is_active]
        inactive_nodes = [n for n in self._nodes.values() if not n.is_active]
        inactive_edges = [e for e in self._edges.values() if not e.is_active]

        kind_counts = defaultdict(int)
        for n in active_nodes:
            kind_counts[n.kind] += 1

        now = _time.time()
        strengths = [self.memory_strength(n, now) for n in active_nodes]
        avg_strength = sum(strengths) / len(strengths) if strengths else 0

        return {
            "total_nodes": len(self._nodes),
            "active_nodes": len(active_nodes),
            "inactive_nodes": len(inactive_nodes),
            "total_edges": len(self._edges),
            "active_edges": len(active_edges),
            "inactive_edges": len(inactive_edges),
            "node_kinds": dict(kind_counts),
            "avg_memory_strength": round(avg_strength, 4),
            "avg_access_count": round(
                sum(n.access_count for n in active_nodes) / len(active_nodes), 2
            ) if active_nodes else 0,
        }

    def to_dot(self) -> str:
        """导出 Graphviz DOT 格式（用于可视化）"""
        lines = ["digraph MemoryGraph {", '  rankdir=LR;', '  node [shape=box];']
        for nid, node in self._nodes.items():
            if not node.is_active:
                continue
            label = node.text[:40].replace('"', '\\"').replace('\n', '\\n')
            style = "" if node.is_active else ', style=dashed'
            color = {
                "entity": "#4CAF50",
                "event": "#2196F3",
                "fact": "#FF9800",
                "episode": "#9C27B0",
            }.get(node.kind, "#607D8B")
            lines.append(
                f'  "{nid}" [label="{label}"{style}, '
                f'style=filled, fillcolor="{color}"];'
            )
        for eid, edge in self._edges.items():
            if not edge.is_active:
                continue
            label = edge.text[:30].replace('"', '\\"')
            style = "" if edge.is_active else ", style=dashed"
            lines.append(
                f'  "{edge.source}" -> "{edge.target}" '
                f'[label="{label}"{style}];'
            )
        lines.append("}")
        return "\n".join(lines)

    def __repr__(self):
        return (
            f"MemoryGraph(nodes={self.node_count}, edges={self.edge_count}, "
            f"embedder={self.embedder.__class__.__name__})"
        )


# ════════════════════════════════════════════════════════════════
# 第四部分：便捷接口（给 AI Agent 用的 Tool 接口）
# ════════════════════════════════════════════════════════════════

class MemoryTool:
    """
    为 AI Agent 提供的记忆工具封装。
    可直接集成到 ReAct / Function Calling 框架中。
    """

    def __init__(self, graph: Optional[MemoryGraph] = None,
                 embedder: Optional[EmbeddingProvider] = None):
        self.graph = graph or MemoryGraph(embedder=embedder)

    def remember(self, content: str, kind: str = "fact",
                 importance: float = 1.0) -> str:
        """记住一条信息"""
        node = self.graph.add_node(content, kind=kind, importance=importance)
        return f"已记住 [{node.id}]: {content}"

    def connect(self, from_id: str, to_id: str, relation: str,
                weight: float = 1.0) -> str:
        """连接两条记忆"""
        edge = self.graph.add_edge(from_id, to_id, relation, weight=weight)
        return f"已连接: {from_id} --[{relation}]--> {to_id}"

    def recall(self, query: str, top_k: int = 5) -> str:
        """回忆与查询相关的记忆"""
        result = self.graph.search(query, top_k=top_k)
        return result["context"]

    def forget(self, node_id: str) -> str:
        """遗忘一条记忆"""
        self.graph.invalidate_node(node_id)
        return f"已遗忘: {node_id}"

    def strengthen(self, node_id: str) -> str:
        """强化一条记忆（复习）"""
        self.graph.touch_node(node_id)
        node = self.graph.get_node(node_id)
        strength = self.graph.memory_strength(node)
        return f"已强化 [{node_id}], 当前强度: {strength:.3f}"

    def sleep(self) -> str:
        """执行记忆整合（建议定期调用）"""
        result = self.graph.consolidate()
        return (
            f"记忆整合完成: 合并 {result['merged_count']} 对, "
            f"清理 {result['pruned_count']} 条, "
            f"活跃节点: {result['active_nodes']}"
        )

    def explore(self, node_id: str, depth: int = 2) -> str:
        """探索一个记忆节点的关联网络"""
        node = self.graph.get_node(node_id)
        if not node:
            return f"节点 {node_id} 不存在"

        lines = [f"=== 探索: [{node_id}] {node.text} ==="]
        neighbors = self.graph.get_neighbors(node_id)
        for edge, neighbor in neighbors:
            arrow = "→" if edge.source == node_id else "←"
            lines.append(f"  {arrow} [{edge.text}] [{neighbor.id}] {neighbor.text}")
        return "\n".join(lines)

    def stats(self) -> str:
        """查看记忆图统计"""
        s = self.graph.stats()
        return (
            f"记忆图统计:\n"
            f"  活跃节点: {s['active_nodes']}\n"
            f"  活跃边: {s['active_edges']}\n"
            f"  节点类型: {s['node_kinds']}\n"
            f"  平均记忆强度: {s['avg_memory_strength']}\n"
            f"  平均复习次数: {s['avg_access_count']}"
        )

    def save(self, filepath: str) -> str:
        self.graph.save(filepath)
        return f"记忆已保存到 {filepath}"

    def load(self, filepath: str) -> str:
        self.graph.load(filepath)
        return f"记忆已从 {filepath} 加载"


# ════════════════════════════════════════════════════════════════
# 第五部分：使用示例
# ════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("MemoryGraph — AI Agent 记忆图工具演示")
    print("=" * 60)

    # 创建记忆工具
    mem = MemoryTool()
    g = mem.graph

    # ── 1. 添加记忆 ──
    print("\n--- 添加记忆 ---")
    n1 = g.add_node("张三是ABC公司的CEO", kind="fact", importance=1.5)
    n2 = g.add_node("ABC公司是一家AI初创企业", kind="fact", importance=1.2)
    n3 = g.add_node("张三", kind="entity", importance=1.3)
    n4 = g.add_node("ABC公司", kind="entity", importance=1.2)
    n5 = g.add_node("李四是ABC公司的CTO", kind="fact", importance=1.0)
    n6 = g.add_node("李四", kind="entity", importance=1.0)
    n7 = g.add_node("ABC公司获得了A轮融资", kind="event", importance=1.5)
    n8 = g.add_node("融资金额为5000万美元", kind="fact", importance=1.3)
    n9 = g.add_node("投资方是红杉资本", kind="fact", importance=1.0)
    n10 = g.add_node("张三曾在Google工作5年", kind="fact", importance=0.8)
    n11 = g.add_node("Google", kind="entity", importance=0.5)
    n12 = g.add_node("ABC公司的产品是AI客服机器人", kind="fact", importance=1.2)

    # ── 2. 建立关系 ──
    print("--- 建立关系 ---")
    g.add_edge(n3.id, n4.id, "是CEO")
    g.add_edge(n3.id, n4.id, "创始人")
    g.add_edge(n6.id, n4.id, "是CTO")
    g.add_edge(n1.id, n3.id, "主语是")
    g.add_edge(n1.id, n4.id, "关于")
    g.add_edge(n2.id, n4.id, "关于")
    g.add_edge(n5.id, n6.id, "主语是")
    g.add_edge(n5.id, n4.id, "关于")
    g.add_edge(n7.id, n4.id, "事件主体")
    g.add_edge(n7.id, n8.id, "包含细节")
    g.add_edge(n7.id, n9.id, "投资方")
    g.add_edge(n3.id, n11.id, "曾就职于")
    g.add_edge(n10.id, n3.id, "关于")
    g.add_edge(n10.id, n11.id, "涉及")
    g.add_edge(n12.id, n4.id, "关于")

    print(f"\n{g}")
    print(f"统计: {g.stats()}")

    # ── 3. 混合检索 ──
    print("\n--- 混合检索 ---")
    print("\n查询: 'ABC公司的管理层是谁？'")
    result = g.search("ABC公司的管理层是谁？", top_k=5)
    print(result["context"])

    print("\n查询: 'ABC公司融资情况'")
    result = g.search("ABC公司融资情况", top_k=5)
    print(result["context"])

    print("\n查询: '张三的工作经历'")
    result = g.search("张三的工作经历", top_k=5)
    print(result["context"])

    # ── 4. 时序失效 ──
    print("\n--- 时序失效 ---")
    # 假设 ABC 公司换了新 CEO
    old_ceo_edge = None
    for eid, edge in g._edges.items():
        if edge.text == "是CEO" and edge.source == n3.id:
            old_ceo_edge = edge
            break
    if old_ceo_edge:
        g.invalidate_edge(old_ceo_edge.id)
        print(f"已使边失效: {old_ceo_edge.text}")

    n13 = g.add_node("王五", kind="entity", importance=1.0)
    g.add_edge(n13.id, n4.id, "新任CEO")
    print(f"添加新 CEO: 王五")

    print("\n查询: 'ABC公司的CEO'")
    result = g.search("ABC公司的CEO", top_k=5)
    print(result["context"])

    # ── 5. 记忆强化 ──
    print("\n--- 记忆强化 ---")
    for _ in range(5):
        g.touch_node(n7.id)  # 反复复习融资事件
    strength = g.memory_strength(n7)
    print(f"融资事件复习 5 次后强度: {strength:.4f}")

    # ── 6. 社区发现 ──
    print("\n--- 社区发现 ---")
    communities = g.get_community_nodes()
    for comm_id, node_ids in communities.items():
        texts = [g._nodes[nid].text[:25] for nid in node_ids if nid in g._nodes]
        print(f"  社区 {comm_id}: {texts}")

    # ── 7. 最短路径 ──
    print("\n--- 最短路径 ---")
    path = g.find_shortest_path(n3.id, n9.id)
    if path:
        path_texts = [g._nodes[nid].text[:15] for nid in path]
        print(f"张三 → 红杉资本 的路径: {' → '.join(path_texts)}")

    # ── 8. BFS 遍历 ──
    print("\n--- BFS 遍历（从张三出发）---")
    bfs_nodes = g.bfs_traverse(n3.id, max_depth=2)
    for bn in bfs_nodes:
        print(f"  [{bn.kind}] {bn.text}")

    # ── 9. 记忆整合 ──
    print("\n--- 记忆整合 ---")
    # 添加一些相似节点测试合并
    g.add_node("张三是ABC公司的CEO", kind="fact")  # 重复
    g.add_node("ABC公司做AI客服机器人", kind="fact")  # 与 n12 相似
    consolidation = g.consolidate()
    print(f"整合结果: {consolidation}")

    # ── 10. 持久化 ──
    print("\n--- 持久化 ---")
    g.save("/tmp/memory_graph_demo.json")
    print("已保存到 /tmp/memory_graph_demo.json")

    g2 = MemoryGraph()
    g2.load("/tmp/memory_graph_demo.json")
    print(f"加载后: {g2}")

    # ── 11. Graphviz 导出 ──
    print("\n--- Graphviz DOT (前10行) ---")
    dot = g.to_dot()
    for line in dot.split("\n")[:10]:
        print(f"  {line}")
    print("  ...")

    # ── 12. MemoryTool 接口 ──
    print("\n--- MemoryTool 便捷接口 ---")
    tool = MemoryTool()
    print(tool.remember("Python是最好的编程语言", kind="fact"))
    print(tool.remember("Guido创造了Python", kind="fact"))
    print(tool.recall("Python编程", top_k=3))
    print(tool.stats())

    print("\n✅ 演示完成！")
