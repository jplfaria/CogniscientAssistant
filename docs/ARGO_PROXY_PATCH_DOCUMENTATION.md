# Argo Proxy Local Patch Documentation

## Overview

We have applied a local patch to argo-proxy v2.7.6 to enable Claude model compatibility with BAML's array content format. This is a **TEMPORARY** solution until the official argo-proxy is updated.

## The Problem

1. **BAML generates array format** for all messages:
   ```json
   {"role": "system", "content": [{"type": "text", "text": "You are helpful"}]}
   ```

2. **Claude requires string format** for system messages through Argo API:
   ```json
   {"role": "system", "content": "You are helpful"}
   ```

3. **Result**: Claude models fail with error: `expected string or bytes-like object, got 'dict'`

## The Solution

We patched `/argoproxy/utils/input_handle.py` in the `handle_option_2_input` function to:
- Detect array format in system messages
- Extract text content from the array structure  
- Convert to plain string for Claude compatibility

## Files Modified

1. **Patched Copy**: `/Users/jplfaria/repos/CogniscientAssistant/patched_argoproxy/`
   - Modified file: `utils/input_handle.py`
   - Function: `handle_option_2_input` (lines 50-65)

2. **Launch Script**: `/Users/jplfaria/repos/CogniscientAssistant/scripts/argo-proxy-patched.py`
   - Uses patched version instead of installed version

## Usage

### Starting the Patched Proxy

```bash
# Instead of:
argo-proxy --config argo-config.yaml

# Use:
python scripts/argo-proxy-patched.py --config argo-config.yaml

# Or update the start script:
./scripts/argo-proxy.sh start  # Will use patched version
```

### Verification

To verify the patch is working:
1. Start the patched proxy
2. Test Claude models with BAML
3. Should no longer get "expected string" errors

## Important Notes

1. **This is TEMPORARY** - Remove when official fix is released
2. **Check for updates** - Run `pip index versions argo-proxy` periodically
3. **Email sent to maintainer** - Peng Ding (argo-proxy developer) on [DATE]
4. **Expected fix timeline** - Unknown, but actively maintained project

## Reverting to Official Version

When the official fix is released:

```bash
# 1. Update argo-proxy
pip install --upgrade argo-proxy

# 2. Test if fix is included
python scripts/test-claude-compatibility.py

# 3. If working, remove patched files
rm -rf patched_argoproxy/
rm scripts/argo-proxy-patched.py

# 4. Update start scripts to use official version
```

## Technical Details of Patch

The patch modifies system message handling:

```python
# BEFORE (original):
system_messages = [
    msg["content"]  # Takes content as-is
    for msg in data["messages"]
    if msg["role"] in ("system", "developer")
]

# AFTER (patched):
system_messages = []
for msg in data["messages"]:
    if msg["role"] in ("system", "developer"):
        content = msg["content"]
        if isinstance(content, list):
            # Extract text from array format
            text_parts = []
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    text_parts.append(part.get("text", "").strip())
            system_messages.append(" ".join(text_parts))
        else:
            system_messages.append(content)
```

## Impact on Testing

With this patch:
- ✅ Claude models should work with BAML
- ✅ OpenAI models continue working (backward compatible)
- ✅ Can now include Claude in comprehensive testing
- ⚠️  Must document this dependency in test results

## References

- Issue discovered: January 21, 2025
- Argo team contact: Matt Dearing confirmed this is Argo API requirement
- Patch author: AI Co-Scientist team
- Related PR: (will be created when official fix is available)