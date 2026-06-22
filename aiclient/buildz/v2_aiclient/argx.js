sends: {
  // 右边是接口输入，左边是调用内部openai/ollama接口传入的实际字段
  qianwen: {
    extra_body.enable_thinking: think
  }
}
fetchs: {
  // 右边是openai/ollama返回的字段，左边是接口转化后的输出字段
  openai: {
    role: role
    content: content
    think: reasoning
    tool_calls: tool_calls
  }
  qianwen: {
    role: role
    content: content
    think: reasoning_content
    tool_calls: tool_calls
  }
  ollama: {
    role: role
    content: content
    think: thinking
    tool_calls: tool_calls
  }
}

