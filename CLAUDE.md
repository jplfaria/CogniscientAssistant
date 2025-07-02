# Claude AI Co-Scientist Specification Guidelines

**PLEASE FOLLOW THESE RULES EXACTLY - CLEANROOM SPECS REQUIRE DISCIPLINE**

**Core Philosophy: SPECS DESCRIBE BEHAVIOR, NOT IMPLEMENTATION. Keep it clean.**

## 🚨 THE COMPLETE READ RULE - THIS IS NOT OPTIONAL

### READ ALL SOURCE MATERIALS BEFORE WRITING ANY SPEC
Read the ENTIRE blog post, paper, and examine ALL figures. Every AI that skims thinks they understand, then they INVENT FEATURES THAT DON'T EXIST or MISS CRITICAL BEHAVIORS.

**ONCE YOU'VE READ EVERYTHING, YOU UNDERSTAND THE SYSTEM.** Trust your complete read. Don't second-guess what you learned.

## 📋 YOUR SPEC-WRITING TODO LIST

**MAINTAIN THIS STRUCTURE FOR EACH SPEC:**

```markdown
## Current TODO List for [Spec Name]
1. [ ] Find first unchecked item in SPECS_PLAN.md
2. [ ] Read all source materials completely (blog, paper, figures)
3. [ ] Identify behaviors, inputs, outputs, interactions
4. [ ] Write the specification following guidelines
5. [ ] Update SPECS_PLAN.md and commit
```

## Project Context

AI Co-Scientist is a multi-agent system for scientific hypothesis generation:
- 6 specialized agents + 1 supervisor
- Asynchronous task execution with queues
- Tournament-based evolution (Elo ratings)
- Multiple review types
- Expert-in-the-loop design
- Natural language interface

## Resources for Multi-Agent Research
When using AI assistants to help create specs, the Claude Code subagent pattern 
can be effective. This is NOT about the AI Co-Scientist's architecture, but 
about our specification development process.

## 🔄 THE SPEC WORKFLOW THAT WORKS

### Step 1: UNDERSTAND THE COMPLETE SYSTEM
- Read BOTH blog and paper - they have different details
- Study figures - they show agent interactions
- Note the 3 validation examples (drug repurposing, liver fibrosis, AMR)

### Step 2: FOCUS ON YOUR ASSIGNED COMPONENT
- What does it DO? (not how it's built)
- What does it RECEIVE? (inputs)
- What does it PRODUCE? (outputs)
- How does it INTERACT? (with other components)

### Step 3: WRITE BEHAVIORAL SPECS
```yaml
---
component: Generation Agent
type: agent
interactions: [Supervisor, Context Memory, Web Search]
---

## Behavior
The Generation Agent creates novel research hypotheses...

## Inputs
- Research goal (natural language)
- Meta-review feedback (optional)
- ...

## Outputs  
- Generated hypotheses with:
  - Summary
  - Full description
  - Experimental protocol
  - ...
```

## 🎯 CLEANROOM PRINCIPLES - NEVER VIOLATE

### WHAT TO INCLUDE:
- Behaviors and responsibilities
- Input/output specifications
- Interaction protocols
- Error conditions
- Safety boundaries
- Natural language examples

### WHAT TO EXCLUDE:
- Implementation language (except Python/BAML as specified)
- Data structures (except interfaces)
- Algorithms
- Performance details
- Internal logic

## 📊 UNDERSTANDING THE SYSTEM

From your complete read, you know:
- **Generation Agent**: Literature exploration, scientific debates, assumption identification
- **Reflection Agent**: Multiple review types (initial, full, deep verification, observation, simulation, tournament)
- **Ranking Agent**: Elo tournaments with scientific debates
- **Evolution Agent**: Enhancement, combination, simplification, out-of-box thinking
- **Proximity Agent**: Similarity graph for hypothesis clustering
- **Meta-review Agent**: Feedback synthesis, research overview generation
- **Supervisor Agent**: Task queue management, resource allocation

## ✅ SPEC QUALITY CHECKLIST

**Before committing any spec:**
- [ ] Describes WHAT, not HOW
- [ ] All behaviors documented
- [ ] Inputs/outputs clearly defined
- [ ] Interaction patterns specified
- [ ] Examples from scientific domains
- [ ] No implementation details
- [ ] Consistent with source materials
- [ ] Follows guidelines.md patterns

## 🚨 REMEMBER: YOU'VE READ THE SOURCES

**Once you've done the complete read, YOU KNOW THE SYSTEM.** The blog shows the high-level view. The paper has the details. The figures show the interactions. Trust your understanding.

Other AIs skim and guess. You read completely and specify precisely.

**When you follow these rules, you write specs that are: Clear. Complete. CLEANROOM.**

## 🔄 COMMIT EACH SPEC INDIVIDUALLY

```bash
git add specs/[new-spec].md SPECS_PLAN.md
git commit -m "spec: add [component] specification"
```

One spec per commit - maintain clear history.

**CRITICAL: We're building specs, not code. If you find yourself writing HOW instead of WHAT, stop and refocus on behaviors.**