# Specification Development Artifacts

This directory contains all files related to the specification development phase of the AI Co-Scientist project. These files are kept for historical reference but are not needed during implementation.

## Files

### Process Files
- `CLEANROOM_EXPERIMENT_PLAN.md` - Original plan for cleanroom spec development
- `run-spec-loop.sh` - Original spec generation script
- `run-spec-loop-improved.sh` - Improved spec generation script with better UI
- `specs-prompt.md` - Prompt used for spec generation
- `SPECS_CLAUDE.md` - Guidelines for spec writing

### Planning and Tracking
- `SPECS_PLAN.md` - Tracking document for all 28 specifications (all completed)
- `SPECIFICATION_COMPLETENESS_REPORT.md` - Final report confirming 100% spec completion

### Assessment
- `specs_assessment.md` - Gap analysis that led to specs 026-028

## Note

These files document the successful specification phase but should not be referenced during implementation. The implementation phase uses:
- `/specs/*` - The actual specifications (source of truth)
- `/CLAUDE.md` - Implementation guidelines
- `/prompt.md` - Implementation prompt
- `/IMPLEMENTATION_PLAN.md` - Current implementation tracking
- `/run-implementation-loop-improved.sh` - Implementation automation script
- `/BAML_SCHEMAS.md` - BAML templates for implementation