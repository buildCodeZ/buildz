send: {
  qianwen: {
    extra_body.enable_thinking: think
  }
}
fetchs: {
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

