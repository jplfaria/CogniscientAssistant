#!/usr/bin/env python3
"""
Debug script to trace exactly what happens with normalization
"""

import sys
import json
sys.path.insert(0, 'temp/argo-proxy-fix/src')

from argoproxy.utils.input_handle import scrutinize_message_entries, normalize_system_message_content
from argoproxy.endpoints.chat import prepare_chat_request_data
from argoproxy.config import ArgoConfig
from argoproxy.models import ModelRegistry

# Mock config and registry
class MockConfig:
    user = "testuser"
    verbose = False

class MockRegistry:
    option_2_input_models = []
    no_sys_msg_models = []
    
    def resolve_model_name(self, name, model_type):
        return name

# Test what BAML sends
baml_data = {
    "model": "claudeopus4",
    "temperature": 0.7,
    "max_tokens": 4000,
    "timeout_seconds": 60,
    "messages": [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": "You are a helpful assistant"
                }
            ]
        }
    ]
}

print("=== Testing normalization flow ===\n")

print("1. Original BAML data:")
print(json.dumps(baml_data, indent=2))

print("\n2. After scrutinize_message_entries:")
scrutinized = scrutinize_message_entries(baml_data.copy())
print(json.dumps(scrutinized, indent=2))

print("\n3. After prepare_chat_request_data:")
prepared = prepare_chat_request_data(
    baml_data.copy(), 
    MockConfig(), 
    MockRegistry(),
    enable_tools=True  # This is what BAML uses
)
print(json.dumps(prepared, indent=2))

print("\n4. Testing normalize_system_message_content directly:")
messages = baml_data["messages"].copy()
normalized = normalize_system_message_content(messages)
print("Normalized messages:", json.dumps(normalized, indent=2))

print("\n=== Key findings ===")
print("1. Does scrutinize_message_entries normalize? ", 
      "YES" if isinstance(scrutinized["messages"][0]["content"], str) else "NO")
print("2. What is the final content type? ", 
      type(prepared.get("messages", [{}])[0].get("content", "N/A")) if "messages" in prepared else "messages removed")
print("3. Are messages still present after prepare_chat_request_data?", 
      "messages" in prepared)