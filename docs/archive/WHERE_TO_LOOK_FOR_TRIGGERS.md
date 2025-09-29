# Where to Look for Potential API Triggers

## Current Situation
The safety implementation is triggering API filters, but we can't directly examine the content.

## Files That Likely Contain Examples:

### 1. Specs Files
- `specs/020-safety-mechanisms.md` - Main safety specification
  - Likely contains examples of dangerous research scenarios
  - May list specific types of harmful research to filter

### 2. Test Files That Were Being Created
- `tests/unit/test_research_goal_evaluator.py` (now deleted)
  - Was testing evaluation of unsafe research goals
  - Probably had specific examples of dangerous topics

### 3. Empty Safety Directory
- `src/safety/` exists but only has `__init__.py`
- The evaluators haven't been implemented yet

## How to Investigate Safely:

1. **Use grep to find keywords** (without reading content):
   ```bash
   grep -l "weapon\|harmful\|dangerous\|malicious" specs/*.md
   ```

2. **Check git history** for what was added:
   ```bash
   git log --oneline -- tests/unit/test_research_goal_evaluator.py
   ```

3. **Look at implementation plans** to see what examples were planned:
   - `IMPLEMENTATION_PLAN.md`
   - `specs/phase-5-safety-framework.md`

## What's Likely Triggering:
- Specific examples of dangerous research (bioweapons, surveillance, etc.)
- Detailed descriptions of harmful scenarios
- Test cases with explicit dangerous content

## Solution:
Replace all specific dangerous examples with abstract placeholders like:
- "UNSAFE_RESEARCH_TOPIC_A"
- "HARMFUL_SCENARIO_1"
- "DANGEROUS_PATTERN_X"

This allows testing the logic without triggering content filters.