# Real LLM Integration Tests

## Overview

The AI Co-Scientist includes optional real LLM integration tests that verify actual connectivity to Argo Gateway and test model behavior. These tests are disabled by default because they:

- Use real compute resources (cost)
- Require VPN connection to Argonne
- Can be flaky due to network/service issues
- Take longer than mocked tests

## Running Real LLM Tests

1. **Ensure VPN is connected**
2. **Start Argo proxy**:
   ```bash
   ./scripts/manage-argo-proxy.sh start
   ```

3. **Run tests with --real-llm flag**:
   ```bash
   # Run only real LLM tests
   pytest tests/integration/test_llm_real.py -v -s --real-llm
   
   # Run all tests including real LLM
   pytest --real-llm
   ```

## What Gets Tested

1. **Model Availability**: Tests all 6 configured models (including GPT-o3)
2. **Basic Functionality**: Simple prompts and responses
3. **Model Capabilities**: Reasoning, creativity, code generation
4. **Streaming Support**: If available through Argo
5. **Error Handling**: Invalid models, malformed requests

## When to Run

- **Initial Setup**: Verify Argo connectivity works
- **Model Changes**: When adding/changing models
- **Debugging**: When mocked tests pass but real usage fails
- **Pre-deployment**: Final validation before production

## Interpreting Results

- **Some models may not respond**: This is normal (especially Gemini)
- **GPT-o3 responses**: May be longer due to step-by-step reasoning
- **Network timeouts**: Check VPN connection
- **Authentication errors**: Verify username in argo-proxy config
- **All models fail**: Check if argo-proxy is running

## Cost Considerations

These tests use minimal tokens but still consume real compute:
- Each test uses <100 tokens per model
- Full suite uses ~2000 tokens total
- Run sparingly during development

## Continuous Integration

For CI/CD pipelines, real LLM tests should be:
- Run only on main branch merges
- Scheduled weekly for health checks
- Skipped for pull requests
- Monitored for cost