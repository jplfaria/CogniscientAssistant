# Next Steps Action Plan

## 1. Immediate Actions (Before Implementation Loop Continues)

### A. Update CLAUDE.md with BAML Requirements
Add a new section documenting:
- All BAML prompts MUST use both system and user roles
- Claude and Gemini require at least one user message
- Example template for correct BAML prompt structure
- Validation requirements for BAML functions

### B. Create BAML Template
Create `baml_src/TEMPLATE.baml` with:
```baml
// Template for all BAML functions to ensure model compatibility
function ExampleFunction(
  param1: string @description("Description"),
  param2: string[] @description("Description")
) -> ReturnType {
  client ProductionClient
  
  prompt #"
    {{ _.role("system") }}
    You are an expert at [specific task].
    [General instructions about your capabilities]
    
    {{ _.role("user") }}
    [Specific request with parameters]
    
    Parameter 1: {{ param1 }}
    Parameter 2: {{ param2 }}
    
    [Detailed instructions for this specific request]
  "#
}
```

### C. Add BAML Validation Tests
Create `tests/unit/test_baml_prompt_structure.py`:
- Verify all BAML functions have both system and user roles
- Check that prompts don't use system-only pattern
- Validate against model requirements

## 2. Comprehensive Model Testing (3-4 hours)

### Hour 1: Compatibility Testing
- [ ] Test o3 with max_tokens to verify it's ignored
- [ ] Test o3 with max_completion_tokens to verify it works
- [ ] Test all models with correct parameters
- [ ] Verify Claude/Gemini work with new prompt structure

### Hour 2: Performance Testing
- [ ] Run 5 iterations per model
- [ ] Measure response times
- [ ] Test with complex scientific prompts
- [ ] Compare quality scores

### Hour 3: Edge Cases
- [ ] Long context handling
- [ ] Complex JSON schemas
- [ ] Error recovery
- [ ] Concurrent requests

### Hour 4: Documentation & Decision
- [ ] Update model recommendations
- [ ] Create quick reference guide
- [ ] Select default models per agent type
- [ ] Document in `.env.example`

## 3. Cleanup Plan

### A. Scripts Directory Consolidation
```bash
# Create organized structure
scripts/
├── core/              # Essential scripts
│   ├── setup-argo-service.sh
│   └── run-real-llm-tests.sh
├── development/       # Keep as-is
├── testing/          # Consolidate test scripts
│   └── comprehensive-model-test.py
└── archive/          # Move exploratory scripts
```

### B. Documentation Cleanup
1. Merge related docs:
   - BAML_AND_MODEL_INTEGRATION_LEARNINGS.md → MODEL_REQUIREMENTS_AND_FINDINGS.md
   - ARGO_PROXY_PATCH_DOCUMENTATION.md → MODEL_REQUIREMENTS_AND_FINDINGS.md

2. Archive outdated docs:
   - Move spec-development/ to archive/
   - Keep only current, relevant documentation

### C. Remove Temporary Files
- [ ] Remove debug scripts (after extracting useful parts)
- [ ] Clean up patched_argoproxy/ (document changes first)
- [ ] Remove test logs and temporary outputs

## 4. Before Restarting Implementation Loop

### A. Update Key Files
1. **CLAUDE.md**: Add BAML requirements section
2. **IMPLEMENTATION_PLAN.md**: Note BAML template requirement
3. **test_expectations.json**: Update with new test requirements
4. **.env.example**: Add model recommendations

### B. Create Safeguards
1. **Pre-commit hook**: Check BAML prompt structure
2. **Test template**: For future BAML functions
3. **Validation script**: Ensure model compatibility

### C. Git Checkpoint
```bash
# After all updates and cleanup
git add -A
git commit -m "feat: complete model integration with BAML compatibility

- Updated all BAML prompts to use system+user roles
- Documented model-specific requirements
- Added comprehensive testing plan
- Cleaned up exploratory scripts
- Ready for implementation loop continuation"
```

## 5. Implementation Loop Continuation Strategy

When the loop resumes:
1. Phase 9+ agents will use the BAML template
2. Each new BAML function gets validated
3. Real LLM tests verify behavior
4. Model-specific configs are applied

## 6. Critical Reminders

1. **Argo-proxy**: Currently using fix/system_message branch - update when official release
2. **Model Parameters**: o3 uses max_completion_tokens, not max_tokens
3. **Message Requirements**: Claude/Gemini need user messages
4. **BAML Structure**: Always use {{ _.role() }} pattern

## Summary

Before continuing:
1. ✅ Run comprehensive model tests (3-4 hours)
2. ✅ Update documentation with requirements
3. ✅ Clean up exploratory code
4. ✅ Create templates and safeguards
5. ✅ Git checkpoint with everything ready

This ensures the implementation loop can continue smoothly with proper model support!