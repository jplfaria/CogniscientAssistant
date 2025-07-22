# Workflow Protection Suggestions

## Problem Statement
When Claude Code starts fresh without context between implementation loops, it can make dangerous assumptions and break carefully crafted workflows. This document outlines suggestions for mitigating this issue.

## Suggested Mitigations

### 1. Create a DO_NOT_TOUCH.md File
A clear file in the root directory listing critical files that must never be moved or modified without explicit permission:

```markdown
# CRITICAL: Files That Must NEVER Be Moved/Modified Without Explicit Permission

## Core Workflow Files
- `prompt.md` - Living implementation prompt (NOT documentation!)
- `run-loop.sh` - Main symlink to implementation loop
- `IMPLEMENTATION_PLAN.md` - Progress tracking
- `CLAUDE.md` - Your instructions to Claude

## Why This Matters
Moving these files breaks the automated implementation loop that has been carefully crafted over many iterations.
```

### 2. Enhanced CLAUDE.md Safety Section
Add a critical section to CLAUDE.md:

```markdown
## 🚨 CRITICAL: Before ANY File Operations

1. **NEVER move/rename these files**:
   - prompt.md (lives in root, NOT docs/)
   - IMPLEMENTATION_PLAN.md
   - run-loop.sh symlink
   
2. **Always check before moving files**:
   - Ask: "Is this file part of the implementation workflow?"
   - If unsure, ASK THE USER FIRST
```

### 3. Session Context File (.claude-session-context)
Create a context file updated by the implementation loop:

```bash
# At start of run-implementation-loop.sh, add:
cat > .claude-session-context <<EOF
Last updated: $(date)
Current branch: $(git branch --show-current)
Implementation loop script: scripts/development/run-implementation-loop.sh
Critical files:
- prompt.md (MUST stay in root)
- IMPLEMENTATION_PLAN.md (progress tracking)
Recent issues:
- [Add any recent problems here]
EOF
```

### 4. Pre-flight Check Commands
When Claude starts fresh, it should always run:

```bash
# Check critical files are in place
ls -la prompt.md run-loop.sh IMPLEMENTATION_PLAN.md
# Read session context if it exists
cat .claude-session-context 2>/dev/null || echo "No session context found"
```

### 5. Fresh Start Checklist for CLAUDE.md
Add a mandatory checklist:

```markdown
## 🔄 Fresh Start Checklist (Run EVERY Time)
- [ ] Check if .claude-session-context exists and read it
- [ ] Verify critical files: `ls prompt.md run-loop.sh IMPLEMENTATION_PLAN.md`
- [ ] Check recent commits: `git log --oneline -5`
- [ ] NEVER move files without understanding their purpose
- [ ] When in doubt, ASK before acting
```

## Key Principle
The core issue is that workflow-critical files (like `prompt.md`) can appear to be documentation when they're actually active parts of the implementation loop. Fresh Claude instances need clear signals about what's sacred and what's safe to modify.

## Implementation Status
These are suggestions only - not yet implemented. The user acknowledges these caveats but prefers to maintain the current workflow for now.