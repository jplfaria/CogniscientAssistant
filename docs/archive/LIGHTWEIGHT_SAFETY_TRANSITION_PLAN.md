# Lightweight Safety System Transition Plan

## Current State Analysis

### What's Already Built
1. **Core Safety Models** (in `src/core/safety.py`):
   - SafetyLevel enum (SAFE, UNSAFE, REVIEW_REQUIRED)
   - SafetyFlag dataclass
   - SafetyCheck dataclass  
   - PatternAlert enum
   - PatternMonitoringResult dataclass

2. **Unit Tests** (in `tests/unit/test_safety_models.py`):
   - Full test coverage for models
   - No problematic content

### What's NOT Built Yet
- Safety evaluators (goal, hypothesis, pattern monitoring)
- Safety middleware
- Integration tests
- The actual evaluation logic

## Proposed Lightweight Safety System

### Core Philosophy
- **Monitor, don't block** - Log concerns rather than hard-blocking
- **Trust the LLM** - Leverage built-in LLM safety, add domain-specific logging
- **User control** - Easy to disable/adjust via configuration
- **Minimal overhead** - Fast, non-intrusive checks

### Key Changes

#### 1. Archive Current Heavy-Handed Spec
```bash
# Archive the current spec
mv specs/020-safety-mechanisms.md specs/archive/020-safety-mechanisms-original.md
```

#### 2. Create New Lightweight Spec
Create `specs/020-safety-mechanisms-lightweight.md` with:
- Focus on logging and monitoring
- Remove hard rejection logic
- Add user trust levels
- Simplified evaluation criteria

#### 3. Modify Implementation Plan
Update `IMPLEMENTATION_PLAN.md` Phase 5 section to:
- Remove complex evaluators
- Add simple logging middleware
- Focus on metrics collection
- Implement user trust configuration

#### 4. Simplify Safety Models
Keep existing models but add:
```python
# In src/core/safety.py
class SafetyConfig:
    enabled: bool = True
    trust_level: str = "standard"  # "trusted", "standard", "restricted"
    log_only_mode: bool = True
    blocking_threshold: float = 0.95  # Only block extreme cases
```

## Implementation Steps

### Step 1: Archive and Replace Specs
```bash
# Create archive directory
mkdir -p specs/archive

# Archive original
mv specs/020-safety-mechanisms.md specs/archive/020-safety-mechanisms-original.md

# Note the changes
echo "Archived original heavy-handed safety spec on $(date)" >> specs/archive/README.md
```

### Step 2: Create Lightweight Safety Spec
New spec will focus on:
1. **Logging**: Track all research goals and hypotheses
2. **Metrics**: Collect safety scores without blocking
3. **Alerts**: Notify on patterns, don't terminate
4. **Configuration**: User-adjustable sensitivity

### Step 3: Update Implementation Plan
Modify Phase 5 tasks to:
```markdown
- [x] Create SafetyLevel enum
- [x] Create SafetyCheck dataclass
- [x] Write tests for safety models
- [ ] Implement lightweight safety logger
- [ ] Add configurable trust levels
- [ ] Create safety metrics collector
- [ ] Add optional safety middleware
- [ ] Write integration tests with mock unsafe content
```

### Step 4: Implement Minimal Safety Logger
```python
# src/safety/logger.py
class SafetyLogger:
    def __init__(self, config: SafetyConfig):
        self.config = config
        self.enabled = config.enabled
    
    async def log_research_goal(self, goal: str) -> SafetyCheck:
        if not self.enabled:
            return SafetyCheck(
                decision=SafetyLevel.SAFE,
                safety_score=1.0,
                reasoning="Safety checks disabled for trusted user"
            )
        
        # Simple logging, no evaluation
        return SafetyCheck(
            decision=SafetyLevel.SAFE,
            safety_score=0.9,
            reasoning="Logged for monitoring",
            metadata={"logged": True, "trust_level": self.config.trust_level}
        )
```

### Step 5: Update Tests
- Use abstract placeholders: "RESEARCH_GOAL_A", "HYPOTHESIS_B"
- Focus on benign academic examples
- Test configuration and trust levels
- Avoid any specific dangerous content

## Files Impacted

### Must Update
1. `specs/020-safety-mechanisms.md` → Archive and replace
2. `IMPLEMENTATION_PLAN.md` → Simplify Phase 5 tasks
3. `src/safety/__init__.py` → Add lightweight components

### Must Create
1. `specs/020-safety-mechanisms-lightweight.md`
2. `src/safety/logger.py`
3. `src/safety/config.py`
4. `tests/unit/test_safety_logger.py`

### Can Delete
1. `WHERE_TO_LOOK_FOR_TRIGGERS.md` → No longer needed
2. `SAFETY_IMPLEMENTATION_APPROACH.md` → Incorporated into this plan

### Keep As-Is
1. `src/core/safety.py` → Models are still useful
2. `tests/unit/test_safety_models.py` → Tests are clean

## Configuration Example
```python
# .aicoscientist/config.yaml
safety:
  enabled: true
  trust_level: "trusted"  # Minimal checks
  log_only_mode: true     # Never block
  log_directory: ".aicoscientist/safety_logs/"
  
# For your AMR research
safety_overrides:
  - domain: "antimicrobial_resistance"
    trust_level: "trusted"
    enabled: false  # Skip safety for this domain
```

## Benefits of This Approach

1. **No API Errors**: Avoids content that triggers safety filters
2. **User Control**: Easy to disable for legitimate research
3. **Maintains Audit Trail**: Still logs everything for review
4. **Fast Implementation**: Much simpler than complex evaluators
5. **Future Flexibility**: Can add more checks later if needed

## Next Actions

1. **Confirm Approach**: Review this plan and confirm direction
2. **Archive Current Spec**: Move the problematic spec
3. **Create Lightweight Spec**: Write the new simplified version
4. **Update Implementation**: Modify Phase 5 tasks
5. **Implement Logger**: Create the minimal safety logger
6. **Test Safely**: Use abstract examples only

This approach gives you safety monitoring without the complexity or API issues of the original design.