// Argo Gateway clients for BAML
// This file provides two approaches to connect to Argo

// Approach 1: Using the fixed argo-proxy (official tool with bug fix)
client<llm> ArgoProxyFixed {
  provider openai-generic
  options {
    base_url "http://localhost:8000/v1"
    model "gpt4o"
    api_key ""
    headers {
      "x-argo-user" env.ARGO_USER
    }
  }
}

// Approach 2: Using our custom proxy (CONCORDIA-style)
client<llm> ArgoCustomProxy {
  provider openai-generic
  options {
    base_url "http://localhost:8000/v1"
    model "gpt4o"
    api_key ""
  }
}

// Default Argo client (points to whichever is configured)
client<llm> ArgoDefault {
  provider openai-generic
  options {
    base_url env.ARGO_PROXY_URL
    model env.DEFAULT_MODEL
    api_key ""
  }
}

// Model-specific clients for testing
client<llm> ArgoGPT4 {
  provider openai-generic
  options {
    base_url env.ARGO_PROXY_URL
    model "gpt4o"
    api_key ""
  }
}

client<llm> ArgoClaude {
  provider openai-generic
  options {
    base_url env.ARGO_PROXY_URL
    model "claudeopus4"
    api_key ""
  }
}

client<llm> ArgoGemini {
  provider openai-generic
  options {
    base_url env.ARGO_PROXY_URL
    model "gemini25pro"
    api_key ""
  }
}