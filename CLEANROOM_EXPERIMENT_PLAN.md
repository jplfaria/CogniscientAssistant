# The CLEANROOM Specification Process for AI Co-Scientist

## Overview

This document explains the systematic approach we've taken to prepare for building CLEANROOM specifications of Google's AI Co-Scientist system using AI agents.

## The Challenge

We want to recreate Google's AI Co-Scientist - a sophisticated multi-agent system for scientific hypothesis generation. However, we need to:
1. Understand the system completely from published materials
2. Create implementation-free specifications (CLEANROOM approach)
3. Ensure our implementation can be validated against the paper's results
4. Use AI agents effectively to help create these specifications

## Our Approach

### 1. Source Material Preparation

We gathered comprehensive source materials in `specs-source/`:
- **Research Paper** (`ai-coscientist-paper.md`): Detailed technical documentation
- **Blog Post** (`ai-coscientist-blog.md`): High-level overview and context
- **Figures** (11 PNG files): Visual representations of system architecture and results
- **Reference Materials** (in `references/`): 12-factor agent principles, BAML patterns, etc.

### 2. Framework Creation

We created four key files to guide the specification process:

#### SPECS_PLAN.md
A systematic 8-phase plan breaking down the AI Co-Scientist into manageable specification tasks:
- Phase 1: Core System Architecture
- Phase 2: Agent Specifications (7 agents)
- Phase 3: Interaction and Interface Specifications
- Phase 4: Core Functionality
- Phase 5: Storage and Persistence
- Phase 6: Quality and Safety
- Phase 7: Documentation Planning
- Phase 8: Validation Framework

#### guidelines.md
Comprehensive guidelines capturing:
- CLEANROOM principles (WHAT not HOW)
- Multi-agent research patterns for using AI to create specs
- Technology decisions (Python, BAML, Argo Gateway)
- AI Co-Scientist specific patterns
- Validation framework based on paper's successes

#### CLAUDE.md
A focused guide for AI agents (or humans) writing specifications:
- Emphasizes complete reading of source materials
- Simplified 5-step TODO process
- Clear separation of what to include/exclude
- Quality checklist for each specification

#### specs-prompt.md
The iterative prompt for creating specifications:
- Process for finding next task in SPECS_PLAN.md
- Clear requirements and format guidelines
- Contextual guidance for different types of specs

### 3. Key Design Decisions

#### CLEANROOM Approach
We're creating behavioral specifications that describe WHAT the system does, not HOW it's implemented. This allows:
- Freedom in implementation choices
- Focus on interfaces and contracts
- Clear success criteria

#### Multi-Agent Research Pattern
We're using AI agents (like Claude) to help create specifications by:
- Spawning parallel agents to research different aspects
- Synthesizing findings after all complete
- Following a systematic process for each specification

#### Validation Framework
We included the paper's three successful validations as test cases:
1. Drug Repurposing: KIRA6 for AML (IC50 13 nM)
2. Liver Fibrosis: 4 epigenetic targets
3. AMR Discovery: cf-PICI mechanism (2 days)

### 4. The Process Flow

1. **Human Setup**: We created the framework files and gathered source materials
2. **AI Agent Execution**: Agents will read sources and create specs following the plan
3. **Iterative Development**: Each spec is created, reviewed, and marked complete
4. **Validation**: Implementation will be tested against paper's results

### 5. Why This Approach Works

#### Systematic
- 44 specific specification tasks across 8 phases
- Clear dependencies and order
- Measurable progress

#### Scalable
- Multiple agents can work on different specs
- Consistent format and guidelines
- Built-in quality checks

#### Verifiable
- CLEANROOM specs can be independently implemented
- Validation framework ensures correctness
- Based on proven results from the paper

## Expected Outcomes

When complete, we'll have:
1. **Comprehensive Specifications**: ~44 detailed specs covering every aspect of the AI Co-Scientist
2. **Clear Implementation Guide**: Behavioral contracts that any developer can follow
3. **Validation Suite**: Test cases to verify our implementation matches the paper
4. **Documentation Framework**: Plans for user guides, API docs, and tutorials

## The Power of Preparation

By investing time in creating this framework, we've:
- Reduced ambiguity for AI agents creating specs
- Ensured consistency across all specifications
- Created a repeatable process for complex system specification
- Built in validation from the start

## Current Experiment: Empty vs Hybrid Approaches

### The Two-Branch Strategy

We're now testing two different approaches to see how AI agents create specifications:

#### 1. Empty Approach (spec-loop-empty branch)
- **Uses**: SPECS_PLAN.md (contains only "Nothing here yet")
- **Goal**: Let the AI agent read all source materials and create its own plan from scratch
- **Benefits**: 
  - Tests if the agent truly understands the system
  - Might discover novel organization patterns
  - Reveals what the agent considers most important
  - No human bias in the structure

#### 2. Hybrid Approach (spec-loop-hybrid branch)
- **Uses**: SPECS_PLAN_hybrid.md (contains our 8-phase plan with flexibility note)
- **specs-prompt.md modified**: Points to SPECS_PLAN_hybrid.md instead of SPECS_PLAN.md
- **Goal**: Provide guidance while allowing flexibility
- **Benefits**:
  - Ensures critical specs aren't missed
  - Provides proven structure
  - Still allows agent creativity
  - Faster to complete

### Branch File Differences
- **main branch**: Contains both SPECS_PLAN.md and SPECS_PLAN_hybrid.md for reference
- **spec-loop-empty**: Uses SPECS_PLAN.md (empty version)
- **spec-loop-hybrid**: Uses SPECS_PLAN_hybrid.md (all references updated to use this file)

### The Experiment Process

1. **First Run - Empty Branch**:
   - Agent reads all sources
   - Creates its own specification plan
   - Executes that plan in subsequent runs
   
2. **Second Run - Hybrid Branch**:
   - Agent uses our plan as guidance
   - Can modify/enhance as needed
   - Follows general structure

3. **Comparison**:
   - Compare the specs from both approaches
   - Identify strengths of each method
   - Determine best practices for future projects

### Running the Loop

We created `run-spec-loop.sh` to manage the iterative process:
- Handles the two-step process (plan creation, then spec creation)
- Pauses between iterations for human review
- Color-coded output for clarity
- Automatic completion detection

### Why This Matters

This experiment will reveal:
- How well AI agents understand complex systems from documentation
- Whether human-guided or AI-generated plans produce better specs
- The optimal balance between structure and autonomy
- Best practices for future CLEANROOM specification projects

This preparation phase, combined with our experimental approach, transforms the daunting task of recreating a complex AI system into a systematic, manageable process where we can discover the most effective ways for AI agents to contribute to specification development.