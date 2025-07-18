# Archived Specifications

This directory contains specifications that have been superseded or modified significantly.

## Archived Files

### 020-safety-mechanisms-original.md
- **Archived Date**: 2025-01-18
- **Reason**: The original heavy-handed safety specification was triggering API safety filters during implementation due to specific examples of dangerous research scenarios. 
- **Replacement**: `specs/020-safety-mechanisms-lightweight.md` - A monitoring-focused lightweight safety system
- **Decision Record**: See `/docs/architecture/decisions/ADR-001-lightweight-safety-system.md`

## Restoration Instructions

To restore any archived specification:
1. Review the decision record to understand why it was archived
2. Copy the file back to the specs directory
3. Update any dependent specifications
4. Update the implementation plan accordingly
5. Document the restoration in a new ADR