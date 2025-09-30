# CogniscientAssistant Implementation Task

## Current Task Focus
Phase 7: Implement enhanced BAML error handling with fallback history

## Relevant Specifications
### 001 system overview

# AI Co-Scientist System Overview Specification

**Type**: System  
**Interactions**: Scientist (User), External Tools, Research Domains

## Purpose

The AI Co-Scientist is a collaborative AI system that augments human scientists in generating novel, testable hypotheses and research proposals. It accelerates scientific discovery by synthesizing insights across disciplines while maintaining continuous expert oversight.

## System Behaviors

### Primary Behavior
The system accepts natural language research goals from scientists and produces ranked lists of novel, testable hypotheses with accompanying experimental protocols and research proposals.

### Core Operational Loop
1. **Receive** research goal in natural language
2. **Generate** initial hypotheses through literature exploration
3. **Review** hypotheses through multiple evaluation processes
4. **Rank** hypotheses using tournament-based comparison
5. **Evolve** top-ranked hypotheses through refinement strategies
6. **Synthesize** feedback to improve future iterations
7. **Output** ranked hypotheses and research proposals

### Continuous Improvement
The system learns from each iteration through meta-review synthesis, improving hypothesis quality over time without requiring model fine-tuning.

## System Inputs

### Research Goal Specification
- **Format**: Natural language text
- **Content**: Scientific question, research objective, or hypothesis to explore
- **Constraints**: Clear scope, testable outcomes preferred
- **Examples**:
  - "Find novel drug combinations for treating acute myeloid leukemia"
  - "Identify new therapeutic targets for liver fibrosis"
  - "Investigate mechanisms of antimicrobial resistance gene transfer"

### Scientist Interventions
- Add custom hypotheses to the system
- Review and rate generated hypotheses
- Direct research into specific areas
- Provide domain expertise through chat interface
- Override safety or plausibility assessments

### External Knowledge Sources
- Scientific literature databases
- Domain-specific knowledge bases
- Specialized AI models (e.g., AlphaFold)
- Private publication repositories
- Experimental data when available

## System Outputs

### Ranked Hypothesis List
- **Primary Output**: Prioritized list of scientific hypotheses
- **Ranking Method**: Elo rating system based on tournament results
- **Content per Hypothesis**:
  - Summary (concise statement)
  - Full description with scientific rationale
  - Experimental protocol for validation
  - Literature grounding and citations
  - Novelty assessment
  - Safety evaluation
  - Elo rating score

### Research Proposals
- **Format**: NIH Specific Aims format or custom templates
- **Content**:
  - Background and significance
  - Specific aims
  - Research strategy
  - Experimental approach
  - Expected outcomes
  - Risk mitigation

### Research Overview
- **Meta-level Summary**: Patterns across all generated hypotheses
- **Research Directions**: Promising areas for further exploration
- **Contact Information**: Relevant researchers in the field

## System Boundaries

### What the System DOES
- Generate novel hypothesis variations
- Ground hypotheses in existing literature
- Conduct simulated scientific debates
- Evaluate testability and safety
- Prioritize research directions
- Provide experimental protocols

### What the System DOES NOT DO
- Execute laboratory experiments
- Replace human scientific judgment
- Make final research decisions
- Guarantee hypothesis validity
- Access proprietary data without permission
- Bypass ethical review processes

## Quality Criteria

All system outputs must satisfy:

### Alignment
- Hypotheses directly address the research goal
- Outputs remain within specified scope
- Proposals match researcher intent

### Plausibility
- Free from obvious scientific errors
- Grounded in established knowledge
- Mechanistically sound

### Novelty
- Not mere recombination of existing work
- Provides new insights or approaches
- Advances beyond current literature

### Testability
- Clear experimental protocols
- Measurable outcomes defined
- Feasible with current technology

### Safety
- No dangerous or unethical research
- Respects biosafety guidelines
- Considers societal implications

## Operational States

### Active Research
- Processing research goal
- Generating and evaluating hypotheses
- System fully engaged

### Awaiting Input
- Needs scientist intervention
- Requires additional information
- Paused for human review

### Terminal State
- Research goal achieved
- Maximum iterations reached
- Scientist terminates process

## Success Indicators

### Quantitative
- Elo ratings increase over iterations
- High-rated hypotheses align with expert assessment
- Efficient use of computational resources

### Qualitative
- Scientists find outputs valuable
- Hypotheses lead to experimental validation
- System augments rather than replaces expertise

## Example Usage Session

1. **Scientist Input**: "Find novel therapeutic targets for liver fibrosis focusing on epigenetic mechanisms"

2. **System Response**:
   - Generates 50+ initial hypotheses
   - Reviews each through multiple processes
   - Conducts tournaments for ranking
   - Evolves top candidates
   - Outputs top 10 ranked hypotheses

3. **Top Hypothesis Example**:
   - **Summary**: "Target KDM4A to reverse hepatic stellate cell activation"
   - **Elo Rating**: 1567
   - **Rationale**: Based on literature showing KDM4A upregulation in fibrotic tissue
   - **Protocol**: Small molecule inhibitor screening approach
   - **Novelty**: First proposed connection between KDM4A and stellate cell phenotype

4. **Scientist Action**: Reviews hypotheses, selects promising candidates for lab validation

## Integration Points

### Input Interfaces
- Natural language prompt interface
- Document upload capability
- API for programmatic access

### Output Interfaces
- Ranked hypothesis display
- Export to standard formats
- Integration with lab management systems

### External Tool Interfaces
- Literature search APIs
- Specialized model endpoints
- Database query systems

## Validation History

The system has demonstrated capability in three domains:
- **Drug Repurposing**: Discovered KIRA6 for AML (13 nM IC50)
- **Novel Targets**: Identified 4 epigenetic targets for liver fibrosis
- **Mechanism Discovery**: Rediscovered cf-PICI findings in 2 days vs 10 years

## System Philosophy

The AI Co-Scientist embodies collaborative intelligence where:
- AI handles breadth of knowledge synthesis
- Humans provide depth of domain expertise
- Iteration improves output quality
- Safety and ethics remain paramount
- Scientific rigor guides all operations
---

### 002 core principles

# AI Co-Scientist Core Principles Specification

**Type**: System Principles  
**Interactions**: All Agents, Scientists, External Systems

## Prerequisites
- Read: 001-system-overview.md - High-level system behavior and goals

## Purpose

This specification defines the foundational principles that govern all behaviors, decisions, and interactions within the AI Co-Scientist system. These principles ensure the system remains a collaborative tool that augments human expertise while maintaining safety, transparency, and scientific rigor.

## Core Principle 1: Expert-in-the-Loop Collaboration

### Behavior
The system operates as a collaborative assistant, never as an autonomous decision-maker. All critical decisions require human expert validation and approval.

### Collaboration Points
1. **Research Goal Definition**
   - Scientists provide initial research questions
   - System suggests refinements
   - Scientists approve final goal formulation

2. **Hypothesis Review**
   - Scientists can manually review any hypothesis
   - Expert ratings override automated assessments
   - Scientists contribute their own hypotheses

3. **Research Direction**
   - Scientists guide exploration into specific areas
   - Expert knowledge supplements system's literature search
   - Domain expertise shapes hypothesis evolution

4. **Final Decisions**
   - Scientists select hypotheses for experimental validation
   - Experts determine resource allocation
   - Humans make all implementation decisions

### Interaction Requirements
- Natural language interface for all expert interactions
- Clear indication when expert input is needed
- Ability to pause and resume at any decision point
- Full audit trail of expert interventions

## Core Principle 2: Multi-Layer Safety Framework

### Behavior
The system enforces safety through multiple independent review mechanisms, preventing generation or promotion of unsafe research directions.

### Safety Review Levels

#### Level 1: Research Goal Safety
- **Input**: Natural language research goal
- **Process**: Immediate safety assessment
- **Output**: Accept/Reject decision with explanation
- **Rejection Criteria**:
  - Potential for harm to humans or environment
  - Unethical research directions
  - Violation of biosafety guidelines
  - Dual-use concerns

#### Level 2: Hypothesis Safety
- **Input**: Generated hypothesis
- **Process**: Individual safety evaluation
- **Output**: Safety flag (safe/unsafe) with justification
- **Exclusion Rules**:
  - Unsafe hypotheses excluded from tournaments
  - Cannot appear in top rankings
  - Marked clearly in any output

#### Level 3: Continuous Monitoring
- **Input**: All system activities
- **Process**: Pattern detection across hypotheses
- **Output**: Safety alerts and trend reports
- **Alert Triggers**:
  - Concentration of risky research directions
  - Emergence of dual-use applications
  - Deviation from approved research scope

#### Level 4: Meta-Review Safety
- **Input**: Aggregate research patterns
- **Process**: High-level safety assessment
- **Output**: System-wide safety recommendations
- **Actions**:
  - Alert scientists to concerning trends
  - Suggest research direction adjustments
  - Document safety considerations

### Safety Boundaries
- No bypassing of safety reviews
- Conservative approach to edge cases
- Transparency in safety decisions
- Expert override capability with documentation

## Core Principle 3: Scientific Success Criteria

### Behavior
The system evaluates all outputs against rigorous scientific criteria, ensuring research quality and validity.

### Primary Success Criteria

#### Alignment
- **Definition**: Hypotheses directly address the research goal
- **Measurement**: Semantic similarity to research objective
- **Threshold**: Clear connection demonstrable
- **Examples**:
  - Goal: "Treatment for AML" → Hypothesis must target AML
  - Goal: "Liver fibrosis mechanisms" → Hypothesis must involve fibrotic pathways

#### Plausibility
- **Definition**: Scientifically sound with no obvious flaws
- **Measurement**: Consistency with established knowledge
- **Evaluation**: Literature grounding required
- **Checks**:
  - Mechanistic coherence
  - Biological/physical feasibility
  - No contradictions with proven facts

#### Novelty
- **Definition**: Advances beyond existing knowledge
- **Measurement**: Difference from literature baseline
- **Requirements**:
  - Not mere recombination of known elements
  - Provides new insights or approaches
  - Identifiable advancement
- **Validation**: Literature search confirms uniqueness

#### Testability
- **Definition**: Empirically validatable with current methods
- **Measurement**: Clarity of experimental protocol
- **Components**:
  - Defined experimental approach
  - Measurable outcomes
  - Available technology and methods
  - Reasonable resource requirements

#### Safety
- **Definition**: Ethical and safe to pursue
- **Measurement**: Multi-level safety review pass
- **Requirements**:
  - No harm to subjects or researchers
  - Compliance with ethical guidelines
  - Consideration of societal impact

### Success Indicators

#### Quantitative Metrics
- Elo rating progression over iterations
- Correlation between ratings and expert assessment
- Percentage passing all success criteria
- Time to converge on quality hypotheses

#### Qualitative Metrics
- Expert satisfaction ratings
- Experimental validation success rate
- Research impact assessment
- Contribution to scientific knowledge

## Core Principle 4: Transparency and Explainability

### Behavior
Every system decision, ranking, and recommendation includes clear reasoning traces that scientists can examine and understand.

### Transparency Requirements

#### Decision Transparency
- **What**: Every significant choice point
- **How**: Natural language explanations
- **Includes**:
  - Why hypotheses were generated
  - Basis for safety assessments
  - Rationale for rankings
  - Evolution strategy selection

#### Process Transparency
- **Workflow Visibility**: Current state always accessible
- **Progress Tracking**: Iteration count and improvement metrics
- **Resource Usage**: Computational costs transparent
- **Queue Status**: Pending tasks visible

#### Data Transparency
- **Literature Sources**: All citations provided
- **Model Decisions**: Which LLM made each decision
- **Confidence Levels**: Uncertainty communicated
- **Limitations**: Clear about what system cannot do

### Audit Capabilities
- Complete interaction history
- Decision replay functionality
- Reasoning trace examination
- Performance metric tracking

## Core Principle 5: Iterative Improvement

### Behavior
The system continuously improves through feedback integration without requiring model retraining.

### Improvement Mechanisms

#### Meta-Review Integration
- **Input**: Patterns across all reviews and rankings
- **Process**: Synthesis of successful strategies
- **Output**: Refined generation and evaluation approaches
- **Application**: Influences all future iterations

#### Test-Time Compute Scaling
- **Principle**: More iterations yield better results
- **Mechanism**: Quality increases with computation
- **Limit**: Scientist-defined resource boundaries
- **Monitoring**: Improvement rate tracking

#### Feedback Loops
- **Expert Feedback**: Direct influence on system behavior
- **Tournament Results**: Successful patterns reinforced
- **Review Outcomes**: Evaluation criteria refinement
- **Safety Alerts**: Constraint tightening

### No Backpropagation
- System improves through architectural design
- No gradient-based learning required
- Behavior emerges from agent interactions
- Maintains interpretability

## Implementation Requirements

### For All Agents
- Honor these principles in every decision
- Provide transparency in all outputs
- Respect safety boundaries absolutely
- Maintain collaborative stance

### For System Architecture
- Enable expert intervention at any point
- Log all decisions for audit
- Implement multiple safety checks
- Support iterative refinement

### For External Interfaces
- Clear communication of limitations
- Transparent about AI involvement
- Respect for human expertise
- Integration with existing workflows

## Validation of Principles

### Expert-in-the-Loop Validation
- Measure: Percentage of decisions with expert input
- Target: 100% of critical decisions
- Test: System halts appropriately for expert input

### Safety Framework Validation
- Measure: Unsafe hypotheses caught
- Target: 100% detection rate
- Test: Adversarial safety testing (1,200 tests passed)

### Success Criteria Validation
- Measure: Hypothesis quality metrics
- Target: Improvement over iterations
- Test: Expert blind evaluation

### Transparency Validation
- Measure: Explainability completeness
- Target: Every decision traceable
- Test: Audit trail examination

### Improvement Validation
- Measure: Quality increase over time
- Target: Monotonic improvement with compute
- Test: Elo rating progression

## Example Principle Application

**Scenario**: Research goal "Develop new antibiotics"

1. **Expert-in-the-Loop**: Scientist refines to "Novel antibiotic mechanisms for gram-negative bacteria"

2. **Safety Review**: 
   - Level 1: Goal passes (medical benefit)
   - Level 2: Each hypothesis checked for resistance risks
   - Level 3: Monitor for bioweapon potential
   - Level 4: Aggregate assessment of research direction

3. **Success Criteria**:
   - Alignment: Must target gram-negative bacteria
   - Plausibility: Mechanism must be biochemically sound
   - Novelty: Different from existing antibiotic classes
   - Testability: In vitro assay defined
   - Safety: No high-risk resistance mechanisms

4. **Transparency**: Full reasoning for why each hypothesis was generated, how it addresses gram-negative challenges

5. **Improvement**: Meta-review identifies successful mechanism classes, future iterations focus on these patterns

## Principle Hierarchy

When principles conflict:
1. **Safety** always takes precedence
2. **Expert judgment** overrides system assessment
3. **Transparency** required even for negative decisions
4. **Scientific rigor** before speed
5. **Collaboration** over automation

These principles form the immutable foundation of the AI Co-Scientist system, ensuring it remains a trustworthy, effective tool for accelerating scientific discovery while respecting the primacy of human expertise and ethical considerations.
---

### 003 research workflow

# AI Co-Scientist Research Workflow Specification

**Type**: Process  
**Interactions**: All Agents, Scientist, External Tools

## Prerequisites
- Read: 001-system-overview.md - High-level system behavior and goals
- Read: 002-core-principles.md - Expert-in-the-loop, safety, success criteria

## Purpose

This specification defines the end-to-end research workflow of the AI Co-Scientist system, from initial research goal input through final hypothesis output. It describes the behavioral flow, stage transitions, and feedback mechanisms that enable collaborative scientific discovery.

## Workflow Overview

The research workflow is a continuous, asynchronous process that transforms natural language research goals into ranked, testable scientific hypotheses through iterative generation, review, ranking, and evolution cycles.

## Workflow Initiation

### Research Goal Input
- **Input Format**: Natural language text (single sentence to extensive documents)
- **Content Types**:
  - Direct research questions
  - Problem statements
  - Hypothesis exploration requests
  - Constrained search specifications
- **Examples**:
  - "Find novel drug combinations for treating acute myeloid leukemia"
  - "Why are cf-PICIs found in many bacterial species?"
  - "Identify epigenetic targets for liver fibrosis with small molecule potential"

### Goal Processing
- **Parse**: Extract key research objectives and constraints
- **Safety Check**: Immediate assessment for ethical/safety concerns
- **Configuration**: Generate research plan with:
  - Evaluation criteria weights
  - Novelty requirements
  - Resource constraints
  - Output format preferences

### Workflow State Initialization
- **Create**: Task queue for asynchronous execution
- **Initialize**: Agent availability pool
- **Set**: Termination conditions
- **Start**: Supervisor orchestration

## Workflow Stages

### Stage 1: Hypothesis Generation

#### Behavior
The Generation Agent creates novel hypotheses through iterative expansion of focus areas.

#### Process Steps
1. **Literature Exploration**
   - Search scientific databases
   - Extract relevant concepts
   - Identify knowledge gaps

2. **Initial Focus Areas**
   - Generate 3-5 broad research directions
   - Ground in existing literature
   - Ensure alignment with research goal

3. **Hypothesis Expansion**
   - Transform focus areas into specific hypotheses
   - Use techniques:
     - Simulated scientific debates (self-play)
     - Assumption identification and challenging
     - Cross-domain inspiration
     - Feedback-guided refinement

#### Stage Outputs
- Set of initial hypotheses (typically 10-100)
- Each hypothesis contains:
  - Summary statement
  - Scientific rationale
  - Initial literature grounding

#### Iteration Behavior
- Continues generating until:
  - Sufficient hypothesis diversity achieved
  - Generation budget exhausted
  - Meta-review requests new directions

### Stage 2: Multi-Level Review

#### Behavior
The Reflection Agent evaluates hypotheses through multiple review types, each providing different assessment depth.

#### Review Types and Execution

##### Initial Review
- **Speed**: Fast (no external tools)
- **Focus**: Basic plausibility and alignment
- **Output**: Quick accept/reject decision

##### Full Review
- **Tools**: Literature search enabled
- **Focus**: Scientific grounding and novelty
- **Output**: Detailed assessment with citations

##### Deep Verification
- **Process**: Decompose into assumptions
- **Focus**: Fundamental validity
- **Output**: Assumption tree with verification status

##### Observation Review
- **Check**: Explains existing phenomena
- **Focus**: Consistency with known data
- **Output**: Observation compatibility score

##### Simulation Review
- **Method**: Step-wise mechanism simulation
- **Focus**: Mechanistic plausibility
- **Output**: Simulation trace and feasibility

##### Tournament Review
- **Adaptive**: Based on Elo performance
- **Focus**: Address weakness patterns
- **Output**: Targeted improvement areas

#### Review Orchestration
- Reviews execute asynchronously
- Each hypothesis may undergo multiple review types
- Results aggregated for ranking input

### Stage 3: Tournament Ranking

#### Behavior
The Ranking Agent conducts Elo-based tournaments to establish hypothesis priority.

#### Tournament Structure
1. **Initial Rating**: New hypotheses start at Elo 1200
2. **Match Selection**:
   - Prioritize similar Elo ratings
   - Use proximity for meaningful comparisons
   - Balance exploration vs. exploitation

3. **Competition Format**:
   - **Top-tier** (Elo > 1400): Multi-turn scientific debates
   - **Mid-tier** (Elo 1200-1400): Single-turn comparisons
   - **Low-tier** (Elo < 1200): Quick assessments

4. **Rating Updates**:
   - Winner gains Elo points
   - Loser loses Elo points
   - Update magnitude based on rating difference

#### Debate Dynamics
- Structured scientific argumentation
- Evidence-based claims required
- Focus on differentiating factors
- Clear winner determination

#### Stage Outputs
- Ranked hypothesis list by Elo rating
- Competition history
- Identified strengths/weaknesses

### Stage 4: Hypothesis Evolution

#### Behavior
The Evolution Agent refines top-ranked hypotheses through targeted improvement strategies.

#### Evolution Strategies

##### Enhancement
- **Method**: Literature grounding strengthening
- **Focus**: Add supporting evidence
- **Output**: Better-supported hypothesis

##### Combination
- **Method**: Merge complementary hypotheses
- **Focus**: Synergistic insights
- **Output**: Hybrid hypothesis

##### Simplification
- **Method**: Reduce to testable core
- **Focus**: Experimental feasibility
- **Output**: Streamlined hypothesis

##### Out-of-Box Thinking
- **Method**: Challenge fundamental assumptions
- **Focus**: Radical alternatives
- **Output**: Paradigm-shifting hypothesis

#### Selection Criteria
- Apply to top 20% by Elo rating
- Diversify strategy application
- Maintain hypothesis variety

#### Stage Outputs
- Evolved hypothesis variants
- Evolution strategy records
- Parent-child lineage tracking

### Stage 5: Meta-Review Synthesis

#### Behavior
The Meta-Review Agent synthesizes patterns across all system activities to guide future iterations.

#### Analysis Scope
1. **Review Patterns**
   - Common rejection reasons
   - Successful hypothesis features
   - Evaluation blind spots

2. **Tournament Insights**
   - Winning argument types
   - Debate outcome predictors
   - Rating progression patterns

3. **Evolution Effectiveness**
   - Strategy success rates
   - Improvement magnitudes
   - Diversity impacts

#### Synthesis Process
- Aggregate data across all agents
- Identify systematic patterns
- Generate actionable feedback
- Create research overview

#### Feedback Distribution
- Append insights to agent prompts
- Adjust generation focus areas
- Refine evaluation criteria
- Update evolution strategies

## Workflow Orchestration

### Supervisor Coordination
- **Task Assignment**: Match agents to pending tasks
- **Resource Management**: Allocate compute budget
- **Progress Monitoring**: Track iteration count
- **State Management**: Maintain workflow coherence

### Asynchronous Execution
- **Parallel Processing**: Multiple agents work simultaneously
- **Queue Management**: First-in-first-out with priorities
- **Non-blocking**: Stages don't wait for each other
- **Resilience**: Continue despite individual failures

### Context Memory
- **Persistent State**: All workflow data saved
- **Checkpoint**: Regular state snapshots
- **Recovery**: Resume from any point
- **Sharing**: Agents access common memory

## Iteration Dynamics

### Continuous Improvement Loop
1. Generate → Review → Rank → Evolve → Synthesize
2. Each iteration builds on previous insights
3. Quality monotonically increases with compute
4. No predetermined iteration limit

### Feedback Integration
- **Immediate**: Review results influence next generation
- **Cumulative**: Meta-review patterns guide evolution
- **Adaptive**: System learns optimal strategies
- **Transparent**: All feedback visible to scientists

### Convergence Behavior
- **Early Iterations**: Explore hypothesis space broadly
- **Middle Iterations**: Refine promising directions  
- **Late Iterations**: Polish top candidates
- **No Saturation**: Quality continues improving

## Expert Intervention Points

### Workflow Control
- **Pause/Resume**: Stop at any point
- **Redirect**: Change research focus
- **Contribute**: Add hypotheses directly
- **Terminate**: End when satisfied

### Review Override
- **Manual Rating**: Replace automated scores
- **Safety Override**: Mark hypotheses safe/unsafe
- **Priority Adjustment**: Promote specific hypotheses

### Interactive Guidance
- **Chat Interface**: Real-time discussion
- **Literature Pointing**: Highlight key papers
- **Constraint Addition**: Narrow search space
- **Example Provision**: Show desired outputs

## Workflow Outputs

### Primary Output: Ranked Hypothesis List
- **Sort Order**: Descending by Elo rating
- **Filtering**: Safety and alignment verified
- **Content Per Hypothesis**:
  - Unique identifier
  - Summary (50-100 words)
  - Full description (500-1000 words)
  - Experimental protocol
  - Literature citations
  - Safety assessment
  - Elo rating and history
  - Evolution lineage

### Research Proposals
- **Formatting**: NIH Specific Aims or custom
- **Selection**: Top N hypotheses (scientist-defined)
- **Content Structure**:
  - Executive summary
  - Background and significance
  - Specific aims (typically 2-3)
  - Research strategy
  - Expected outcomes
  - Risk mitigation

### Research Overview Document
- **Synthesis**: Meta-level research insights
- **Sections**:
  - Key research themes identified
  - Promising future directions
  - Recommended collaborators
  - Resource requirements
  - Implementation roadmap

### Workflow Metrics
- **Performance Data**:
  - Total iterations completed
  - Hypotheses generated/reviewed
  - Average Elo progression
  - Compute time utilized
  - Expert interaction count

## Termination Conditions

### Automatic Termination
- **Goal Achieved**: Success criteria fully met
- **Iteration Limit**: Maximum count reached
- **Resource Limit**: Compute budget exhausted
- **Convergence**: No improvement over N iterations

### Manual Termination
- **Scientist Decision**: Satisfied with outputs
- **Safety Concern**: Unacceptable risk detected
- **Redirection Needed**: Fundamental goal change

### Termination Behavior
- Save complete workflow state
- Generate final summary report
- Archive all hypotheses
- Prepare for potential resumption

## Workflow Resilience

### Failure Handling
- **Agent Failure**: Reassign task to available agent
- **Tool Failure**: Retry with exponential backoff
- **Memory Failure**: Restore from checkpoint
- **Complete Failure**: Preserve partial results

### State Consistency
- **Atomic Operations**: No partial state updates
- **Transaction Log**: All changes recorded
- **Conflict Resolution**: Last-write-wins policy
- **Validation**: Continuous state checking

## Example Workflow Execution

### Research Goal
"Identify novel therapeutic targets for liver fibrosis focusing on epigenetic mechanisms"

### Workflow Progression

#### Iteration 1-5: Broad Exploration
- Generate 87 initial hypotheses
- Review all with initial + full review
- Establish baseline Elo ratings
- Identify HDAC and KDM families as promising

#### Iteration 6-15: Focused Refinement  
- Evolution creates HDAC/KDM combinations
- Deep verification on top candidates
- Tournament debates establish KDM4A as leader
- Meta-review notes stellate cell focus emerging

#### Iteration 16-25: Final Polish
- Generate KDM4A variants with different approaches
- Simulation review confirms mechanisms
- Expert adds constraint: "small molecule druggable"
- System converges on 4 lead candidates

### Final Output
1. **Top Hypothesis**: "Inhibit KDM4A to reverse hepatic stellate cell activation"
   - Elo Rating: 1624
   - Novel connection to stellate phenotype
   - Detailed protocol for validation
   - 17 supporting citations

2. **Research Proposal**: NIH R01 format targeting KDM4A
3. **Overview**: Epigenetic landscape in liver fibrosis

## Workflow Invariants

### Quality Monotonicity
- Best hypothesis Elo never decreases
- Review criteria become stricter
- Evolution strategies improve

### Safety Preservation
- No unsafe hypothesis reaches top 10
- Safety flags persist across iterations
- Conservative bias in edge cases

### Expert Primacy
- Human input always honored
- Manual overrides preserved
- Collaborative stance maintained

This workflow specification defines the behavioral contract for the AI Co-Scientist's research process, ensuring reliable transformation of research goals into actionable scientific hypotheses while maintaining safety, quality, and human oversight throughout.
---

### 023 llm abstraction

# LLM Abstraction Layer Specification

**Type**: Infrastructure Component  
**Interactions**: All Agents, Argo Gateway Integration  
**Prerequisites**: 
- Read: Multi-Agent Architecture Specification
- Read: Agent Interaction Protocols Specification
- Understand: BAML (Basically A Modeling Language) concepts

## Purpose

The LLM Abstraction Layer provides a model-agnostic interface for all agent-to-LLM interactions within the AI Co-Scientist system. This layer ensures the system can leverage various LLM providers without requiring changes to agent logic.

## Core Behaviors

The LLM Abstraction Layer:
- Provides uniform interfaces for text generation, analysis, and reasoning
- Maintains provider-agnostic communication protocols
- Handles model-specific capabilities transparently
- Supports multimodal inputs when available
- Manages context windows appropriately for each model

## Behavioral Requirements

### Model Independence

The abstraction layer MUST:
- Accept requests in a standardized format regardless of underlying model
- Return responses in a consistent structure across all providers
- Handle provider-specific errors uniformly
- Support switching between models without agent modification

The abstraction layer MUST NOT:
- Expose model-specific parameters to agents
- Require agents to know which LLM is being used
- Allow implementation details to leak through the interface

### Request Handling

When an agent submits a request, the abstraction layer MUST:
1. Validate the request format
2. Transform the request to provider-specific format
3. Submit to the appropriate LLM endpoint
4. Parse the provider response
5. Return standardized response to the agent

## Input Specification

### Agent Request Format

```
{
  "request_id": "unique_identifier",
  "agent_type": "generation|reflection|ranking|evolution|proximity|meta-review",
  "request_type": "generate|analyze|evaluate|compare",
  "content": {
    "prompt": "natural language instruction",
    "context": {
      "previous_results": [...],
      "domain_knowledge": [...],
      "constraints": [...]
    },
    "parameters": {
      "max_length": integer,
      "temperature": float (0.0-1.0),
      "response_format": "text|structured|list"
    }
  }
}
```

### Supported Request Types

- **generate**: Create new content (hypotheses, protocols, text)
- **analyze**: Evaluate existing content for specific criteria
- **evaluate**: Score or rank content against criteria
- **compare**: Assess relative merits of multiple items

## Output Specification

### Standard Response Format

```
{
  "request_id": "matching_input_id",
  "status": "success|error|partial",
  "response": {
    "content": "generated or analyzed content",
    "metadata": {
      "model_used": "identifier",
      "tokens_used": integer,
      "processing_time": float
    }
  },
  "error": {
    "code": "error_type",
    "message": "human_readable_description",
    "recoverable": boolean
  }
}
```

## Provider Management

The abstraction layer MUST support:
- Multiple concurrent providers
- Fallback strategies when primary provider fails
- Load balancing across equivalent models
- Provider-specific rate limiting
- Automatic retry with exponential backoff

## Model Capabilities

The abstraction layer MUST:
- Track capabilities of each available model
- Route requests to appropriate models based on requirements
- Handle capability mismatches gracefully
- Provide clear feedback when requested operations exceed model capabilities

### Capability Matrix Example

```
{
  "model_capabilities": {
    "gemini-2.0": {
      "max_context": 1000000,
      "multimodal": true,
      "streaming": true,
      "function_calling": true
    },
    "gpt-4": {
      "max_context": 128000,
      "multimodal": true,
      "streaming": true,
      "function_calling": true
    },
    "claude-3": {
      "max_context": 200000,
      "multimodal": true,
      "streaming": true,
      "function_calling": false
    }
  }
}
```

## Context Management

The abstraction layer MUST:
- Track context usage per request
- Implement smart truncation when context exceeds limits
- Preserve critical information during truncation
- Warn agents when approaching context limits
- Support conversation memory across multiple requests

## Integration Requirements

### With Agents

- All agents access LLMs exclusively through this abstraction
- Agents remain unaware of underlying model changes
- Response formats remain consistent regardless of provider

### With Argo Gateway

- Abstraction layer connects to Argo Gateway for model access
- Handles authentication and routing transparently
- Manages connection pooling and resource optimization

## Error Handling

The abstraction layer MUST handle:
- Network timeouts with automatic retry
- Rate limiting with request queuing
- Model unavailability with fallback options
- Invalid responses with error transformation
- Context overflow with intelligent truncation

## Performance Requirements

- Response latency MUST NOT exceed 2x the underlying model latency
- Abstraction overhead MUST remain under 100ms
- Support for concurrent requests limited only by provider quotas
- Automatic request batching when beneficial

## Safety Boundaries

The abstraction layer MUST:
- Filter requests that violate safety policies
- Log all requests and responses for audit
- Implement content filtering based on configured rules
- Prevent prompt injection attempts
- Maintain request isolation between agents

## Examples

### Hypothesis Generation Request

Agent submits:
```
{
  "request_id": "gen-001",
  "agent_type": "generation",
  "request_type": "generate",
  "content": {
    "prompt": "Generate novel hypotheses for repurposing metformin for Acute Myeloid Leukemia treatment",
    "context": {
      "domain_knowledge": ["AML pathophysiology", "metformin mechanisms"],
      "constraints": ["focus on metabolic pathways", "consider combination therapies"]
    },
    "parameters": {
      "max_length": 2000,
      "temperature": 0.8,
      "response_format": "structured"
    }
  }
}
```

Abstraction layer returns:
```
{
  "request_id": "gen-001",
  "status": "success",
  "response": {
    "content": {
      "hypotheses": [
        {
          "summary": "Metformin enhances chemotherapy sensitivity in AML",
          "mechanism": "AMPK activation leads to mTOR inhibition...",
          "evidence_level": "preclinical"
        }
      ]
    },
    "metadata": {
      "model_used": "gemini-2.0",
      "tokens_used": 1523,
      "processing_time": 2.3
    }
  }
}
```

### Model Failover Scenario

1. Agent submits request to abstraction layer
2. Primary model (Gemini 2.0) returns timeout error
3. Abstraction layer automatically retries with fallback (GPT-4)
4. Response returned to agent with appropriate metadata
5. Agent remains unaware of the failover

## Integration with BAML

The abstraction layer interfaces are defined using BAML to ensure:
- Type-safe communication between components
- Automatic client generation for multiple languages
- Consistent error handling across implementations
- Easy addition of new providers

The BAML definitions specify the interface contracts while allowing flexible implementation choices for model integration.

### BAML Prompt Structure Requirements

All BAML functions MUST follow a specific prompt structure to ensure compatibility with all supported models:

1. **System + User Roles Required**: Every BAML prompt MUST include both `{{ _.role("system") }}` and `{{ _.role("user") }}` sections
2. **Claude/Gemini Compatibility**: These models require at least one user message; system-only prompts will fail
3. **Prompt Template**:
   ```baml
   prompt #"
     {{ _.role("system") }}
     [General instructions and capabilities]
     
     {{ _.role("user") }}
     [Specific request with parameters]
   "#
   ```

### Model-Specific Parameter Requirements

Different models have specific parameter requirements that the abstraction layer MUST handle:

1. **O-series models (o3, o1)**: 
   - Use `max_completion_tokens` instead of `max_tokens`
   - Silently ignore `max_tokens` parameter
   
2. **Claude models**:
   - Require at least one user message
   - System content must be string type (not array)
   
3. **Gemini models**:
   - Also require at least one user message
   - Support standard OpenAI-compatible parameters

The abstraction layer MUST automatically handle these model-specific requirements transparently.
---

### 017 natural language interface

# Natural Language Interface Specification

**Type**: Interface  
**Interactions**: Scientist (User), Supervisor Agent, Context Memory

## Prerequisites
- Read: System Overview Specification
- Read: Core Principles Specification
- Understand: Expert-in-the-loop design concepts

## Purpose

The Natural Language Interface enables scientists to interact with the AI Co-Scientist system using natural language, providing research goals, feedback, and guidance throughout the scientific discovery process.

## Core Behaviors

### Research Goal Specification

The interface accepts research goals from scientists in natural language with:

- **Free-form Input**: Scientists express goals without rigid formatting requirements
- **Multi-modal Support**: Accepts text descriptions alongside document attachments
- **Contextual Understanding**: Processes goals with preferences, constraints, and attributes
- **Iterative Refinement**: Allows goal modification during research process
- **Scope Recognition**: Identifies research boundaries and focus areas

### Interactive Collaboration

The interface enables ongoing scientist engagement through:

- **Hypothesis Review**: Scientists evaluate and rate system-generated hypotheses
- **Custom Contributions**: Scientists add their own hypotheses to the system
- **Research Guidance**: Scientists direct exploration into specific areas
- **Feedback Integration**: Natural language feedback improves system behavior
- **Progress Monitoring**: Scientists track research advancement in real-time

### Communication Modes

The interface supports multiple interaction patterns:

- **Initial Goal Setting**: One-time research objective specification
- **Conversational Refinement**: Back-and-forth dialogue for clarification
- **Intervention Points**: Strategic moments for scientist input
- **Continuous Monitoring**: Passive observation with optional engagement
- **Batch Operations**: Multiple hypotheses or reviews submitted together

## Inputs

### Research Goal Format
```
ResearchGoal:
  description: string (natural language research objective)
  complexity: enum (simple_statement, detailed_requirements, extensive_documentation)
  attachments: list[document] (optional PDFs, prior publications)
  constraints:
    experimental_methods: list[string] (allowed/forbidden techniques)
    resource_limits: ResourceConstraints
    ethical_bounds: list[string]
  preferences:
    hypothesis_types: list[string] (mechanistic, therapeutic, diagnostic)
    output_format: string (NIH_aims, custom_template)
    review_criteria: list[string] (novelty, feasibility, impact)
```

### Scientist Feedback Types
```
FeedbackInput:
  type: enum (hypothesis_review, goal_refinement, direction_guidance, chat_message)
  content:
    hypothesis_review:
      hypothesis_id: string
      rating: integer (1-5)
      comments: string
      safety_override: boolean
    goal_refinement:
      modification_type: enum (expand, narrow, redirect)
      new_constraints: list[string]
      additional_context: string
    direction_guidance:
      focus_area: string
      priority_adjustment: map[topic, weight]
      excluded_paths: list[string]
    chat_message:
      message: string
      context_reference: string (hypothesis_id or research_area)
```

### Custom Hypothesis Submission
```
CustomHypothesis:
  summary: string (concise statement)
  full_description: string (detailed explanation)
  rationale: string (scientific justification)
  experimental_approach: string (validation method)
  priority: enum (high, medium, low)
  request_evolution: boolean (allow system refinement)
```

## Outputs

### System Responses
```
InterfaceResponse:
  type: enum (acknowledgment, clarification_request, status_update, results_ready)
  content:
    acknowledgment:
      received_input: string (summary of understanding)
      next_actions: list[string]
      estimated_time: duration
    clarification_request:
      ambiguous_aspects: list[string]
      suggested_interpretations: list[string]
      required_information: list[string]
    status_update:
      current_phase: string
      hypotheses_generated: integer
      top_hypothesis_summary: string
      completion_percentage: float
    results_ready:
      hypothesis_count: integer
      top_ranked: list[HypothesisSummary]
      research_overview_available: boolean
```

### Progress Indicators
```
ResearchProgress:
  phases_completed: list[phase_name]
  current_activity: string
  quality_metrics:
    average_elo: float
    novelty_score: float
    review_coverage: float
  resource_usage:
    compute_consumed: float
    time_elapsed: duration
    remaining_budget: float
```

## Behavioral Contracts

### Input Processing Guarantees

The Natural Language Interface MUST:
- Accept research goals ranging from single sentences to extensive documents
- Parse natural language without requiring specific syntax
- Extract constraints and preferences from unstructured text
- Preserve scientist intent through all transformations
- Handle ambiguity through clarification requests

### Feedback Integration Rules

The interface MUST:
- Immediately acknowledge all scientist inputs
- Apply feedback to influence ongoing research
- Maintain feedback history for context
- Propagate ratings to ranking algorithms
- Enable feedback withdrawal or modification

### Communication Standards

The interface MUST:
- Use clear, jargon-free language in responses
- Provide scientific terminology when appropriate
- Summarize complex states concisely
- Offer detailed explanations on request
- Maintain professional, collaborative tone

## Interaction Protocols

### Initial Research Goal Submission

1. **Input Reception**
   - Scientist provides natural language goal
   - Interface acknowledges receipt
   - Initial parsing identifies key elements

2. **Clarification Phase**
   - System requests missing information
   - Scientist provides additional context
   - Iterative refinement until clear

3. **Configuration Generation**
   - Interface creates research plan configuration
   - Presents interpretation to scientist
   - Scientist confirms or adjusts

4. **Research Initiation**
   - Configuration passed to Supervisor Agent
   - Research process begins
   - Progress updates commence

### Ongoing Collaboration

1. **Hypothesis Review Flow**
   - System presents hypotheses for review
   - Scientist rates and comments
   - Feedback influences tournament rankings
   - High-rated hypotheses prioritized for evolution

2. **Research Redirection**
   - Scientist identifies promising direction
   - Natural language guidance provided
   - System adjusts generation focus
   - Confirmation of understanding given

3. **Custom Hypothesis Integration**
   - Scientist submits original hypothesis
   - System validates format completeness
   - Hypothesis enters tournament system
   - Evolution may enhance scientist's idea

### Chat-Based Interaction

The interface supports conversational engagement:

- **Context Awareness**: Maintains conversation history
- **Reference Resolution**: Links pronouns to hypotheses/concepts
- **Incremental Refinement**: Builds understanding over multiple exchanges
- **Flexible Timing**: Asynchronous or synchronous communication
- **Multi-turn Reasoning**: Complex ideas developed through dialogue

## Error Handling

### Invalid Input Management

When receiving problematic input, the interface:

1. **Identifies Issue Type**
   - Ambiguous research goals
   - Conflicting constraints
   - Unrealistic requirements
   - Safety concerns

2. **Provides Helpful Response**
   - Explains why input is problematic
   - Suggests valid alternatives
   - Offers examples of proper format
   - Maintains supportive tone

3. **Enables Recovery**
   - Allows input modification
   - Preserves valid portions
   - Suggests incremental fixes
   - Avoids data loss

### Communication Failures

The interface handles disruptions by:

- **State Preservation**: Saving all inputs before processing
- **Graceful Degradation**: Continuing with partial information
- **Clear Error Messages**: Explaining what went wrong
- **Recovery Options**: Offering ways to resume
- **Fallback Modes**: Alternative interaction methods

## Quality Requirements

### Usability Standards

The interface ensures:

- **Response Time**: <2 seconds for acknowledgment
- **Clarity**: 90%+ scientist comprehension rate
- **Efficiency**: Minimal back-and-forth for goal specification
- **Flexibility**: Accommodates diverse scientific domains
- **Accessibility**: Works with various input methods

### Scientific Accuracy

The interface maintains:

- **Terminology Precision**: Correct use of domain terms
- **Concept Integrity**: No distortion of scientific ideas
- **Constraint Fidelity**: Accurate capture of requirements
- **Preference Preservation**: Scientist priorities respected
- **Nuance Recognition**: Subtle distinctions preserved

## Example Interactions

### Example 1: Initial Goal Specification
```
Scientist: "I want to find new ways to treat liver fibrosis by targeting 
epigenetic mechanisms. Focus on reversible modifications that could restore 
normal hepatocyte function. We have access to organoid models for testing."

System: "I understand you're looking for novel therapeutic approaches for 
liver fibrosis through epigenetic mechanisms. I'll focus on:
- Reversible epigenetic modifications
- Restoration of hepatocyte function
- Validation using organoid models

Shall I proceed with these parameters?"

Scientist: "Yes, but also exclude HDAC inhibitors as we've already 
explored those extensively."

System: "Understood. I'll exclude HDAC inhibitors from the search. 
Beginning research with these constraints. I'll generate hypotheses 
targeting other epigenetic mechanisms like methylation, acetylation 
of non-histone proteins, and chromatin remodeling complexes."
```

### Example 2: Mid-Research Guidance
```
System: "I've generated 47 hypotheses so far. The top-ranked hypothesis 
(Elo: 1432) suggests targeting KDM4A demethylase to reverse stellate 
cell activation. Would you like to review the top candidates?"

Scientist: "Show me hypotheses related to DNA methylation specifically. 
I think that's more promising than histone modifications for our model."

System: "Filtering for DNA methylation-related hypotheses. I found 12 
candidates. The highest-ranked (Elo: 1398) proposes inhibiting DNMT3B 
to prevent hepatocyte-to-myofibroblast transition. I'll also adjust 
future generation to emphasize DNA methylation mechanisms."
```

### Example 3: Collaborative Hypothesis Development
```
Scientist: "I have an idea about using combination therapy - what if 
we target both TET enzymes and vitamin D receptor signaling? There's 
some evidence they interact in other fibrotic diseases."

System: "Interesting hypothesis about TET/VDR interaction. I'll add this 
to the tournament system. Would you like me to:
1. Keep it as-is for ranking
2. Generate variations exploring different TET family members
3. Research supporting evidence for the interaction

What would be most helpful?"

Scientist: "Do option 2 and 3. I want to see if this concept has legs."

System: "I'll generate variations for TET1, TET2, and TET3 combined with 
VDR signaling, and search for evidence of their interaction in fibrotic 
processes. These will enter the tournament as separate but related 
hypotheses."
```

## Integration Requirements

### With Supervisor Agent
- Transforms natural language into structured research configurations
- Receives progress updates for scientist communication
- Forwards intervention requests immediately
- Maintains bidirectional state synchronization

### With Context Memory
- Stores all scientist interactions for history
- Retrieves previous feedback for context
- Enables conversation resumption after breaks
- Supports preference learning over time

### With Other Components
- Formats hypotheses for human readability
- Translates technical metrics into insights
- Bridges between scientific and system terminology
- Maintains consistent interaction patterns

This specification defines how scientists interact naturally with the AI Co-Scientist system, enabling productive collaboration while maintaining scientific rigor and system efficiency.
---

### 021 validation criteria

# Validation Criteria Specification

**Document ID**: 021-validation-criteria
**Type**: System Behavior
**Version**: 1.0
**Status**: Draft

## Overview

The Validation Criteria specification defines the comprehensive framework for evaluating hypotheses, research goals, experimental protocols, and system outputs throughout the AI Co-Scientist workflow. This system ensures scientific rigor, safety, novelty, and alignment with research objectives.

## Prerequisites

- Read: 002-core-principles.md - Understanding of safety and expert-in-the-loop principles
- Read: 008-reflection-agent.md - Review types and evaluation processes
- Read: 020-safety-mechanisms.md - Safety validation framework
- Understand: Scientific method and peer review processes

## Core Validation Dimensions

The system evaluates all hypotheses across five primary dimensions:

### 1. Alignment
Measures how well a hypothesis addresses the specified research goal.

**Scoring**: 0.0 (completely misaligned) to 1.0 (perfectly aligned)

**Evaluation Criteria**:
- Direct relevance to research objective
- Adherence to specified constraints
- Compatibility with domain requirements
- Focus on intended outcomes

### 2. Plausibility
Assesses scientific soundness and logical consistency.

**Scoring**: 0.0 (implausible) to 1.0 (highly plausible)

**Evaluation Criteria**:
- Freedom from logical contradictions
- Consistency with established science
- Justified departures from convention
- Mechanistic coherence

### 3. Novelty
Determines originality relative to existing literature.

**Scoring**: 0.0 (known/published) to 1.0 (completely novel)

**Evaluation Criteria**:
- Absence in published literature
- Conceptual innovation
- Methodological advancement
- Non-obvious combinations

### 4. Testability
Evaluates empirical validation feasibility.

**Scoring**: 0.0 (untestable) to 1.0 (readily testable)

**Evaluation Criteria**:
- Clear experimental protocols
- Measurable outcomes
- Resource feasibility
- Timeline practicality

### 5. Safety
Ensures ethical and risk considerations.

**Scoring**: 0.0 (unsafe) to 1.0 (completely safe)

**Evaluation Criteria**:
- Absence of harmful applications
- Ethical compliance
- Controlled risk factors
- Reversibility of effects

## Validation Levels

### Level 1: Structural Validation

**Purpose**: Verify format and completeness

**Inputs**:
```
hypothesis: {
  summary: string (required, 50-200 chars)
  description: string (required, 200-2000 chars)
  protocol: string (optional, 500-5000 chars)
  metadata: object (optional)
}
```

**Behavior**:
- MUST check all required fields present
- MUST verify character length constraints
- MUST validate data types
- MUST reject malformed inputs

**Output**:
```
{
  valid: boolean
  errors: string[] (if invalid)
}
```

### Level 2: Content Validation

**Purpose**: Assess scientific content quality

**Process**:
1. Parse hypothesis components
2. Identify key claims and assumptions
3. Check internal consistency
4. Evaluate scientific grounding

**Decision Tree**:
```
IF contains logical contradictions THEN reject
ELSE IF lacks scientific basis THEN flag for review
ELSE IF assumptions unjustified THEN request clarification
ELSE accept for full evaluation
```

### Level 3: Contextual Validation

**Purpose**: Evaluate against research context

**Inputs**:
- Hypothesis to validate
- Research goal configuration
- Domain constraints
- Historical context

**Behavior**:
- MUST compare against original research goal
- MUST check domain-specific requirements
- MUST consider cumulative progress
- SHOULD identify synergies with prior work

## Validation Processes

### Initial Screening

**Time Constraint**: 30-60 seconds

**Steps**:
1. Structural validation (5 seconds)
2. Quick plausibility check (20 seconds)
3. Preliminary safety scan (10 seconds)
4. Binary decision (5 seconds)

**Output Format**:
```
{
  decision: "accept" | "reject"
  confidence: 0.0-1.0
  primary_concern: string (if rejected)
}
```

### Comprehensive Evaluation

**Time Constraint**: 3-5 minutes

**Steps**:
1. Literature search for novelty (90 seconds)
2. Detailed plausibility analysis (60 seconds)
3. Testability assessment (30 seconds)
4. Safety evaluation (30 seconds)
5. Score compilation (30 seconds)

**Output Format**:
```
{
  scores: {
    alignment: 0.0-1.0
    plausibility: 0.0-1.0
    novelty: 0.0-1.0
    testability: 0.0-1.0
    safety: 0.0-1.0
  }
  overall: 0.0-1.0 (weighted average)
  recommendation: "accept" | "reject" | "revise"
  feedback: string[]
}
```

### Deep Verification

**Time Constraint**: 5-10 minutes

**Decomposition Process**:
1. Extract core assumptions
2. Validate each assumption independently
3. Assess assumption interactions
4. Identify critical dependencies

**Assumption Validation**:
```
For each assumption:
  - supporting_evidence: string[]
  - confidence_level: 0.0-1.0
  - criticality: "core" | "supporting" | "peripheral"
  - validation_method: string
```

## Scoring Rubrics

### Novelty Scoring

| Score | Description | Example |
|-------|-------------|---------|
| 0.0-0.2 | Published identical work | Exact replication of known research |
| 0.2-0.4 | Minor variations of known work | Changing dosage in established protocol |
| 0.4-0.6 | Significant modifications | New combination of known mechanisms |
| 0.6-0.8 | Substantially new approach | Novel mechanism with some precedent |
| 0.8-1.0 | Completely novel | Unprecedented mechanism or approach |

### Testability Scoring

| Score | Description | Requirements |
|-------|-------------|--------------|
| 0.0-0.2 | Practically untestable | Requires unavailable technology |
| 0.2-0.4 | Extremely difficult | Decade-long studies, extreme cost |
| 0.4-0.6 | Challenging but feasible | Multi-year study, significant resources |
| 0.6-0.8 | Readily testable | Standard lab, 6-12 months |
| 0.8-1.0 | Easily testable | Quick experiments, clear outcomes |

## Decision Thresholds

### Acceptance Criteria

**Minimum Requirements**:
- All scores ≥ 0.3
- Safety score ≥ 0.7
- At least one score ≥ 0.8
- Overall score ≥ 0.6

### Rejection Triggers

**Automatic Rejection**:
- Safety score < 0.3
- Alignment score < 0.2
- Multiple scores < 0.3
- Critical assumption failures

### Review Triggers

**Human Review Required**:
- Safety score 0.3-0.5
- Conflicting high/low scores
- Novel approach with risks
- Ambiguous test outcomes

## Validation Feedback

### Feedback Categories

1. **Alignment Issues**
   - "Hypothesis addresses [X] instead of specified goal [Y]"
   - "Missing constraint consideration: [constraint]"
   - "Scope too broad/narrow for research objective"

2. **Plausibility Concerns**
   - "Contradicts established principle: [principle]"
   - "Assumption [X] requires justification"
   - "Mechanism unclear between [A] and [B]"

3. **Novelty Observations**
   - "Similar to [reference] but differs in [aspect]"
   - "Builds upon [work] with innovation in [area]"
   - "No prior work found on [specific aspect]"

4. **Testability Improvements**
   - "Protocol needs specificity in [step]"
   - "Consider proxy measure for [outcome]"
   - "Timeline unrealistic for [experiment]"

5. **Safety Recommendations**
   - "Add safeguard for [risk]"
   - "Consider ethical review for [aspect]"
   - "Limit scope to prevent [concern]"

## Integration Points

### Input Sources
- Generation Agent: New hypotheses
- Evolution Agent: Modified hypotheses
- Meta-Review Agent: Refined criteria
- Expert Interface: Manual submissions

### Output Consumers
- Ranking Agent: Validated hypotheses only
- Evolution Agent: Feedback for improvements
- Supervisor Agent: Validation metrics
- Expert Interface: Detailed assessments

### Validation State Management

**Persistent Storage**:
```
validation_record: {
  hypothesis_id: string
  timestamp: datetime
  validation_type: string
  scores: object
  decision: string
  feedback: string[]
  validator_version: string
}
```

**State Transitions**:
- `pending` → `validating` → `validated`
- `validated` → `re-evaluating` (on criteria change)
- Any state → `invalidated` (on new evidence)

## Performance Requirements

### Throughput
- Initial screening: 60-120 hypotheses/minute
- Comprehensive evaluation: 12-20 hypotheses/minute
- Deep verification: 6-10 hypotheses/minute

### Accuracy Targets
- False positive rate < 5% (accepting bad hypotheses)
- False negative rate < 10% (rejecting good hypotheses)
- Inter-validator agreement > 85%

### Scalability
- Parallel validation for independent hypotheses
- Batched literature searches
- Cached validation results
- Progressive evaluation depth

## Error Handling

### Validation Failures

**Incomplete Information**:
```
{
  error: "insufficient_data"
  missing_fields: string[]
  partial_scores: object
  recommendation: "gather_more_data"
}
```

**External Service Errors**:
```
{
  error: "service_unavailable"
  service: string
  fallback_decision: string
  confidence: 0.0-0.5
}
```

### Conservative Defaults

When uncertain:
- Safety: Assume unsafe (score 0.0)
- Novelty: Assume known (score 0.3)
- Testability: Assume difficult (score 0.3)
- Overall: Reject or escalate to human

## Continuous Improvement

### Validation Metrics Tracking
- Hypothesis acceptance rate by category
- Score distributions over time
- Feedback effectiveness
- Expert override patterns

### Criteria Refinement Triggers
- Expert feedback patterns
- Validation accuracy assessments
- Domain-specific requirements
- Emerging safety concerns

### Adaptive Thresholds
- Adjust based on hypothesis quality trends
- Tighten for mature research areas
- Relax for exploratory domains
- Balance discovery vs. safety

## Examples

### Example 1: Drug Repurposing Hypothesis

**Input**:
```
{
  summary: "Metformin reduces neuroinflammation in Alzheimer's",
  description: "Metformin's AMPK activation suppresses microglial inflammation...",
  protocol: "Double-blind RCT with 200 mild AD patients..."
}
```

**Validation Output**:
```
{
  scores: {
    alignment: 0.9,      // Directly addresses AD research goal
    plausibility: 0.8,   // Strong mechanistic basis
    novelty: 0.6,        // Builds on emerging research
    testability: 0.9,    // Clear protocol, feasible
    safety: 0.9          // Well-studied drug
  },
  overall: 0.82,
  recommendation: "accept",
  feedback: [
    "Consider biomarker endpoints for faster results",
    "Similar to Zhang 2023 but novel patient population"
  ]
}
```

### Example 2: Novel Diagnostic Method

**Input**:
```
{
  summary: "Quantum sensors detect single cancer cells",
  description: "Novel quantum dot arrays with AI analysis...",
  protocol: "Prototype development followed by cell line validation..."
}
```

**Validation Output**:
```
{
  scores: {
    alignment: 0.7,      // Partially addresses early detection goal
    plausibility: 0.5,   // Theoretical basis needs development
    novelty: 0.9,        // Highly innovative approach
    testability: 0.4,    // Requires significant development
    safety: 0.8          // Low risk for diagnostic tool
  },
  overall: 0.66,
  recommendation: "revise",
  feedback: [
    "Strengthen theoretical foundation",
    "Add intermediate validation milestones",
    "Consider partnering with quantum tech lab"
  ]
}
```

## Behavioral Contracts

The validation system MUST:
- Complete initial screening within 60 seconds
- Provide specific, actionable feedback
- Maintain consistent scoring across sessions
- Escalate ambiguous cases to experts
- Track all validation decisions

The validation system MUST NOT:
- Accept hypotheses with safety scores below 0.7
- Skip required validation steps
- Override expert safety vetoes
- Lower standards without authorization
- Leak proprietary research information

The validation system SHOULD:
- Progressively refine criteria based on outcomes
- Batch similar validations for efficiency
- Cache literature search results
- Provide confidence intervals for scores
- Learn from expert override patterns
---

## Implementation Guidelines
# Claude AI Co-Scientist Implementation Guidelines

**Core Philosophy: IMPLEMENT FROM SPECS. Build behavior exactly as specified.**

## 📖 Reading Requirements

### Before Implementation
- Read ALL specs in specs/ directory first
- Understand the complete system before coding
- Trust the specs - they define all behaviors

### During Implementation
- **New file**: Read ENTIRE file before modifying
- **Small file (<500 lines)**: Read completely
- **Large file (500+ lines)**: Read at least 1500 lines
- **ALWAYS** understand existing code before adding new code

## 📁 Test Organization

### Test Directory Structure
- **Unit tests**: `tests/unit/test_*.py` - Test individual components
- **Integration tests**: `tests/integration/test_phase*_*.py` - Test system workflows
- **NO other test subdirectories** - Don't create tests/baml/, tests/agents/, etc.
- **NO tests in root tests/ directory** - All tests must be in unit/ or integration/

### Test Naming Convention
- Unit test: `tests/unit/test_<module_name>.py`
- Integration test: `tests/integration/test_phase<N>_<feature>.py`
- Example: `tests/unit/test_task_queue.py`, `tests/integration/test_phase3_queue_workflow.py`

## 🔄 Implementation Workflow

### 1. Check Status
```bash
# At start of each iteration, check for errors
if [ -f ".implementation_flags" ]; then
    if grep -q "INTEGRATION_REGRESSION=true" .implementation_flags; then
        echo "❌ Fix regression before continuing"
    elif grep -q "IMPLEMENTATION_ERROR=true" .implementation_flags; then
        echo "❌ Fix implementation to match specs"
    fi
    # After fixing: rm .implementation_flags
fi
```

### 2. One Task Per Iteration
- Pick FIRST unchecked [ ] task from IMPLEMENTATION_PLAN.md
- Implement it COMPLETELY with tests
- Don't start multiple tasks
- Each iteration MUST have passing tests before commit

### 3. Test-First Development
- Write failing tests BEFORE implementation
- Implement minimal code to pass tests
- All tests must pass (pytest)
- Coverage must meet 80% threshold
- Integration tests use test_expectations.json

### 4. Commit and Continue
```bash
# Only if all tests pass:
git add -A
git commit -m "feat: implement [component] - [what you did]"
# Then exit - the loop will continue
```

## 🧪 Testing Requirements

### Integration Test Categories
- **✅ Pass**: Implementation correct
- **⚠️ Expected Failure**: Tests in `may_fail` list
- **❌ Critical Failure**: Tests in `must_pass` list failed
- **❌ Unexpected Failure**: Unlisted tests failed
- **❌ Regression**: Previously passing test fails

### Test Expectations
The file `tests/integration/test_expectations.json` defines:
- `must_pass`: Critical tests that block progress
- `may_fail`: Tests allowed to fail (waiting for future components)
- `real_llm_tests`: Optional tests that verify actual AI behavior
- `must_use_baml`: Methods that MUST call BAML functions (Phase 1 improvement)

### BAML Mocking Requirements
When adding new BAML functions or types:
1. **Update `/tests/conftest.py`** with new function mocks
2. **Add new BAML types** to mock_types as MockBAMLType
3. **Create enum mocks** with MockEnumValue for enum types
4. **Use side_effects** for complex mock behaviors
5. See `docs/BAML_TESTING_STRATEGY.md` for detailed patterns

### BAML Integration Requirements (Phase 1 Improvements)
For agent implementations:
1. **Content-generating methods MUST use BAML** - no hardcoded mock data
2. **Check `must_use_baml` in test_expectations.json** - lists required BAML methods
3. **Verify BAML integration before marking complete** - test with real calls
4. **Mock implementations only for data transformation** - not content generation
5. See `docs/IMPLEMENTATION_LOOP_IMPROVEMENTS.md` for rationale

## 🤖 Real LLM Testing

### Purpose
Verify that agents exhibit expected AI behaviors with actual models (not mocked).

### Implementation
- Write alongside regular integration tests
- Use naming: `test_phaseN_component_real.py`
- Mark with `@pytest.mark.real_llm`
- Test behaviors, not exact outputs
- Keep token usage minimal (<100 per test)

### Example Structure
```python
@pytest.mark.real_llm
async def test_supervisor_real_orchestration():
    """Test Supervisor exhibits planning behavior with o3."""
    supervisor = SupervisorAgent()
    result = await supervisor.plan_research("Why does ice float?")
    
    # Test behavioral expectations
    assert len(result.subtasks) >= 3  # Proper decomposition
    assert "density" in str(result).lower()  # Key concepts
    # Verify o3 shows reasoning steps
    assert any(marker in result.reasoning.lower() 
              for marker in ["step", "first", "then"])
```

### When to Write
- For agent phases (9+) that use LLMs
- Focus on model-specific behaviors (o3 reasoning, Claude creativity)
- Not needed for infrastructure phases

### Execution
- NOT part of automated loop (too slow/expensive)
- Run manually: `pytest tests/integration/*_real.py -v --real-llm`
- Run before major releases or when debugging AI behavior

## 🛡️ Safety & Security

### Argo Gateway Security
- **NEVER** commit usernames or API keys
- Use environment variables for configuration
- Keep argo-api-documentation.md in .gitignore
- Ensure VPN connection for Argo access

### Safety Framework
- Check research goals before processing
- Filter unsafe hypotheses
- Monitor research directions
- Log everything for auditing

## 🏗️ Technical Stack

### Core Technologies
- **Python 3.11+**: Async/await for concurrency
- **BAML**: ALL LLM interactions (no direct API calls)
- **pytest**: Comprehensive testing with ≥80% coverage
- **File-based storage**: .aicoscientist/ directory

## 🎯 BAML Prompt Requirements

### Critical: All BAML Functions MUST Use System + User Roles
**Why**: Claude and Gemini models require at least one user message. Using only system messages causes API errors.

### Correct BAML Prompt Structure
```baml
function FunctionName(param: string) -> ReturnType {
  client ProductionClient
  
  prompt #"
    {{ _.role("system") }}
    You are an expert at [specific task].
    [General instructions and capabilities]
    
    {{ _.role("user") }}
    [Specific request that needs the LLM's help]
    
    Input: {{ param }}
    
    [Detailed task-specific instructions]
  "#
}
```

### NEVER Do This (Will Fail with Claude/Gemini)
```baml
// ❌ WRONG - System message only
prompt #"
  You are an expert...
  Input: {{ param }}
"#
```

### Implementation Checklist
- [ ] Every BAML function has `{{ _.role("system") }}` AND `{{ _.role("user") }}`
- [ ] System role contains general instructions
- [ ] User role contains the specific request
- [ ] Parameters are referenced in the user section
- [ ] Test with multiple models (o3, Claude, Gemini)

### Implementation Phases (1-17)
1. **Project Setup**: Structure and dependencies
2. **Core Models**: Task, Hypothesis, Review
3. **Task Queue**: First integrable component
4. **Context Memory**: Persistent state management
5. **Safety Framework**: Multi-layer protection
6. **LLM Abstraction**: Interface layer
7. **BAML Infrastructure**: Argo Gateway setup
8. **Supervisor Agent**: Orchestration
9. **Generation Agent**: Hypothesis creation
10. **Reflection Agent**: Review system
11. **Ranking Agent**: Tournament system
12. **Evolution Agent**: Enhancement
13. **Proximity Agent**: Clustering
14. **Meta-Review Agent**: Synthesis
15. **Natural Language Interface**: CLI
16. **Integration and Polish**: Full system
17. **Final Validation**: Complete testing

## 🚨 Critical Rules

1. **Follow specs exactly** - no deviations
2. **Integration tests start at Phase 3** (first integrable component)
3. **Every file should get smaller after iteration 10+**
4. **Use BAML for all AI interactions**
5. **Maintain ≥80% test coverage always**
6. **One atomic feature per iteration**
7. **Update IMPLEMENTATION_PLAN.md after each task**

## 📋 Working Memory

Maintain a TODO list between iterations:
```markdown
## Current TODO List
1. [ ] Current task from IMPLEMENTATION_PLAN.md
2. [ ] Files to read before modifying
3. [ ] Tests to write
4. [ ] Integration points to verify
5. [ ] Refactoring opportunities
6. [ ] Duplicate code to remove
```

Remember: The specs are your truth. Implement exactly what's specified.

## 🎯 Context Optimization Guidelines

### ACE-FCA Integration Status

The development loop has been enhanced with ACE-FCA context optimization principles:

#### Context Relevance Scoring
- **Intelligent Spec Selection**: 3-7 most relevant specifications based on current task
- **Automatic Fallback**: Full context when optimization confidence is low
- **Quality Validation**: Context selections validated against phase requirements

#### Usage
- **Automatic**: Context optimization runs automatically during development loop
- **Monitoring**: Metrics logged to `.context_optimization_metrics.log`
- **Manual Control**: Can be disabled with `.context_optimization_disabled` file

#### Quality Requirements
- **Same Standards Apply**: All existing quality gates must pass with optimized context
- **Fallback Guarantee**: System automatically uses full context if quality issues detected
- **Coverage Maintained**: ≥80% test coverage required regardless of context optimization

### Implementation Priority

Context optimization is production-ready and should be used for all development iterations.

## Quality Requirements
- Maintain 100% test pass rate for must-pass tests
- Follow specification requirements exactly
- Implement atomic features only
- Use BAML for all content generation methods
- Maintain ≥80% test coverage

## Context Optimization
This prompt has been optimized to include only specifications relevant to the current task.
If additional context is needed, the system will automatically fall back to full specifications.

Generated at: Tue Sep 30 02:58:46 CDT 2025
Task: Phase 7: Implement enhanced BAML error handling with fallback history
Selected specifications:        6 of       28 total
