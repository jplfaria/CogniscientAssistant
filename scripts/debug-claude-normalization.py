#!/usr/bin/env python3
"""
Debug script to understand why Claude normalization isn't working.
"""

import sys
sys.path.insert(0, 'temp/argo-proxy-fix/src')

from argoproxy.utils.input_handle import normalize_system_message_content, handle_option_2_input
from argoproxy.models import OPTION_2_INPUT_PATTERNS
import json

# Test data that BAML sends
test_data = {
    "model": "claudeopus4",
    "messages": [
        {
            "role": "system",
            "content": [{"type": "text", "text": "You are a helpful assistant"}]
        },
        {
            "role": "user",
            "content": "Hello"
        }
    ]
}

print("Original data:")
print(json.dumps(test_data, indent=2))

print("\nAfter normalize_system_message_content:")
normalized = normalize_system_message_content(test_data.copy())
print(json.dumps(normalized, indent=2))

print("\nOPTION_2_INPUT_PATTERNS:", OPTION_2_INPUT_PATTERNS)
print("Is Claude in option_2_input? No (patterns are empty)")

print("\nWhat happens if we call handle_option_2_input anyway:")
try:
    transformed = handle_option_2_input(normalized.copy())
    print(json.dumps(transformed, indent=2))
except Exception as e:
    print(f"Error: {e}")