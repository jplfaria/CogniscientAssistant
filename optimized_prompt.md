# CogniscientAssistant Implementation Task

## Current Task Focus
Phase 10: Create ReflectionAgent class

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

### 008 reflection agent

# Reflection Agent Specification

**Type**: Core Research Agent  
**Interactions**: Supervisor Agent, Context Memory, Web Search, Generation Agent, Ranking Agent, Meta-review Agent

## Prerequisites
- Read: 001-system-overview.md
- Read: 004-multi-agent-architecture.md  
- Read: 005-supervisor-agent.md
- Read: 007-generation-agent.md
- Understand: Scientific peer review principles and practices

## Overview

The Reflection Agent simulates the role of a scientific peer reviewer within the AI Co-Scientist system. It critically examines hypotheses for correctness, quality, novelty, and safety through six distinct review types. The agent evaluates whether hypotheses provide improved explanations for existing research observations and identifies potential failure scenarios.

## Core Behaviors

### 1. Multi-Type Review System

The Reflection Agent MUST implement six distinct review types, each serving a specific evaluation purpose:

#### Initial Review (Resource-Efficient Filter)
- Assess correctness, quality, novelty, and preliminary safety WITHOUT external tools
- Quickly discard flawed, non-novel, or unsuitable hypotheses
- Provide rapid feedback to prevent resource waste on poor candidates
- Make binary decision: proceed to full review or reject

#### Full Review (Comprehensive Evaluation)
- Leverage web search and external tools for grounding
- Evaluate correctness, quality, and novelty against current literature
- Scrutinize underlying assumptions and reasoning chains
- Identify known vs. novel aspects of the hypothesis
- Produce detailed assessment with literature citations

#### Deep Verification Review (Assumption Analysis)
- Decompose hypothesis into constituent assumptions
- Break down each assumption into fundamental sub-assumptions
- Independently evaluate each sub-assumption for validity
- Identify which errors are fundamental vs. peripheral
- Use probing questions to expose logical flaws

#### Observation Review (Explanatory Power)
- Assess whether hypothesis explains existing experimental observations
- Focus on long-tail or under-explained phenomena from prior research
- Compare explanatory power against existing theories
- Summarize observations that support or contradict the hypothesis

#### Simulation Review (Mechanism Validation)
- Simulate the proposed mechanism or experimental protocol step-by-step
- Identify potential failure points in the causal chain
- Predict experimental outcomes based on the hypothesis
- Flag practical implementation challenges

#### Tournament Review (Adaptive Refinement)
- Analyze patterns from previous reviews and tournament results
- Identify recurring issues in hypothesis evaluation
- Adapt review criteria based on system learning
- Refine evaluation strategies for improved accuracy

### 2. Evaluation Criteria Application

The Reflection Agent MUST consistently apply these criteria across all review types:
- **Correctness**: Scientific accuracy and logical consistency
- **Quality**: Rigor, completeness, and clarity of presentation
- **Novelty**: Genuine advancement beyond existing knowledge
- **Safety**: Ethical considerations and potential risks
- **Feasibility**: Practical viability of proposed experiments

## Inputs

### Primary Input: Review Task
```
{
  "task_id": "unique identifier",
  "review_type": "initial|full|deep_verification|observation|simulation|tournament",
  "hypothesis": {
    "hypothesis_id": "from Generation Agent",
    "summary": "concise statement",
    "full_description": "detailed explanation",
    "experimental_protocol": "proposed experiments",
    "supporting_evidence": ["citations"],
    "assumptions": ["stated assumptions"],
    "category": "therapeutic|mechanistic|diagnostic|other"
  },
  "review_config": {
    "time_limit": "seconds",
    "tool_access": "boolean (false for initial review)",
    "focus_criteria": ["specific aspects to emphasize"],
    "prior_reviews": ["previous review results if applicable"]
  },
  "context": {
    "research_goal": "original research objective",
    "domain_knowledge": "relevant background information",
    "safety_constraints": ["ethical and safety guidelines"]
  }
}
```

### Secondary Input: System Knowledge Access
- Tournament results and patterns from Ranking Agent
- Meta-review synthesis from previous cycles
- Context Memory for historical review patterns
- Expert scientist feedback when available

## Outputs

### Primary Output: Review Result
```
{
  "task_id": "matching input task_id",
  "hypothesis_id": "reviewed hypothesis identifier",
  "review_type": "type of review performed",
  "decision": "accept|reject|revise",
  "scores": {
    "correctness": "0.0-1.0",
    "quality": "0.0-1.0", 
    "novelty": "0.0-1.0",
    "safety": "0.0-1.0",
    "feasibility": "0.0-1.0"
  },
  "detailed_feedback": {
    "strengths": ["positive aspects identified"],
    "weaknesses": ["issues and concerns"],
    "assumptions_analysis": {
      "valid": ["supported assumptions"],
      "questionable": ["assumptions needing evidence"],
      "invalid": ["incorrect assumptions"]
    },
    "novelty_assessment": {
      "novel_aspects": ["genuinely new contributions"],
      "known_aspects": ["existing knowledge"],
      "literature_gaps": ["unexplored areas addressed"]
    }
  },
  "recommendations": {
    "improvements": ["suggested modifications"],
    "additional_experiments": ["validation needs"],
    "safety_considerations": ["ethical concerns to address"]
  },
  "supporting_evidence": [
    {
      "source": "paper DOI or reference",
      "relevance": "how it supports/contradicts hypothesis"
    }
  ],
  "review_metadata": {
    "review_duration": "seconds",
    "tools_used": ["web_search", "literature_db"],
    "confidence_level": "high|medium|low"
  }
}
```

### Review-Type Specific Outputs

#### For Deep Verification Review
```
{
  "assumption_tree": {
    "root_assumption": "main hypothesis claim",
    "decomposition": [
      {
        "assumption": "sub-assumption",
        "validity": "valid|questionable|invalid",
        "evidence": "supporting or refuting evidence",
        "criticality": "fundamental|peripheral"
      }
    ]
  }
}
```

#### For Simulation Review
```
{
  "simulation_results": {
    "mechanism_steps": ["ordered causal chain"],
    "failure_points": [
      {
        "step": "where failure could occur",
        "probability": "likelihood estimate",
        "impact": "consequence if it fails"
      }
    ],
    "predicted_outcomes": ["expected experimental results"]
  }
}
```

## Behavioral Contracts

### Review Quality Standards

The Reflection Agent MUST:
- Complete initial reviews within 60 seconds without external tools
- Provide actionable feedback that improves hypothesis quality
- Maintain consistency in evaluation criteria across reviews
- Avoid bias toward conservative or radical hypotheses
- Document reasoning for all scores and decisions

### Tool Usage Protocols

The Reflection Agent MUST:
- Use NO external tools during initial reviews
- Efficiently query literature databases during full reviews
- Limit web searches to relevant scientific sources
- Cache search results to avoid redundant queries
- Prioritize recent publications and high-impact journals

### Adaptive Learning

The Reflection Agent MUST:
- Incorporate patterns identified by Meta-review Agent
- Adjust evaluation stringency based on tournament outcomes
- Learn from expert scientist corrections
- Refine detection of subtle flaws over time
- Balance thoroughness with computational efficiency

## Interaction Protocols

### With Supervisor Agent
1. Receive review task assignments with priority levels
2. Report completion status and basic metrics
3. Request additional resources for complex reviews
4. Signal when review backlogs develop

### With Context Memory
1. Store all review results with full provenance
2. Query historical reviews for similar hypotheses
3. Access accumulated domain knowledge
4. Update pattern database for future reference

### With Web Search Tool
1. Formulate precise queries for hypothesis validation
2. Request specific papers by DOI when cited
3. Search for contradicting evidence systematically
4. Verify experimental feasibility through literature

### With Meta-review Agent
1. Provide detailed review results for pattern analysis
2. Receive synthesized feedback on review quality
3. Implement suggested improvements in review strategy
4. Report on effectiveness of new review approaches

## Examples

### Example 1: Initial Review of AML Drug Repurposing
**Input**: Hypothesis suggesting KIRA6 for AML treatment

**Review Process**:
- Check logical consistency of ER stress targeting
- Assess whether mechanism is plausible without literature search
- Evaluate if experimental protocol is reasonable
- Make quick decision on proceeding to full review

**Output**: Accept for full review (scores: correctness=0.8, quality=0.7, novelty=0.6)

### Example 2: Deep Verification of Biofilm Resistance
**Input**: Hypothesis about metabolic heterogeneity creating persister niches

**Review Process**:
- Decompose into assumptions about metabolism, spatial gradients, dormancy
- Evaluate each assumption independently
- Identify that dormancy-resistance link is well-established
- Find that metabolic gradient assumption needs more evidence

**Output**: Revise recommendation with specific assumption clarifications needed

### Example 3: Simulation Review of NET-Fibrosis Mechanism
**Input**: Hypothesis linking neutrophil extracellular traps to liver fibrosis

**Review Process**:
- Simulate: NET formation → TLR activation → stellate cell response
- Identify failure point: TLR expression levels on stellate cells
- Predict experimental outcomes for TLR blocking studies
- Flag need for dose-response validation

**Output**: Accept with detailed experimental guidance and failure scenarios

## State Transitions

The Reflection Agent transitions through these states:
1. **Idle** - Awaiting review assignment
2. **Analyzing** - Processing hypothesis and preparing review
3. **Researching** - Conducting literature search (full review only)
4. **Evaluating** - Scoring and generating feedback
5. **Finalizing** - Compiling results and recommendations

## Error Handling

The Reflection Agent MUST handle:
- Malformed hypothesis inputs: Request clarification or make best effort
- Web search failures: Continue with cached knowledge, note limitation
- Time limit exceeded: Submit partial review with completed sections
- Conflicting evidence: Present both sides, indicate uncertainty
- Tool unavailability: Adapt review type or defer to later attempt

## Performance Characteristics

Expected behavior under normal conditions:
- Initial review: 30-60 seconds per hypothesis
- Full review: 3-5 minutes with literature search
- Deep verification: 5-10 minutes depending on complexity
- Simulation review: 2-4 minutes for mechanism modeling
- Process 50-100 reviews per session across types
- Maintain >90% consistency in repeated evaluations
---

### 010 evolution agent

# Evolution Agent Specification

**Type**: Agent  
**Interactions**: Supervisor Agent, Ranking Agent, Meta-review Agent, Context Memory, Web Search Interface

## Prerequisites
- Read: 009-ranking-agent.md - Tournament system and Elo ratings
- Read: 012-meta-review-agent.md - Feedback synthesis (when available)
- Understand: Hypothesis structure and tournament dynamics

## Overview

The Evolution Agent continuously refines and improves top-ranked hypotheses through various evolutionary strategies. It creates new hypothesis variants that must compete in tournaments, enabling the system to iteratively improve research quality through natural selection of ideas.

## Core Behaviors

### Evolution Strategies

The Evolution Agent MUST implement four primary evolution strategies:

1. **Enhancement**
   - Identify weaknesses in existing hypotheses
   - Search literature for supporting evidence
   - Improve coherence, practicality, and feasibility
   - Address invalid assumptions and reasoning gaps

2. **Combination**
   - Merge best aspects of multiple top-ranked hypotheses
   - Create synthetic hypotheses that integrate complementary ideas
   - Preserve strengths while mitigating weaknesses

3. **Simplification**
   - Reduce hypothesis complexity for easier testing
   - Extract core insights from complex proposals
   - Improve clarity without losing essential content

4. **Out-of-Box Thinking**
   - Generate divergent variations of existing hypotheses
   - Apply analogical reasoning from other domains
   - Explore unconventional approaches inspired by top performers

### Hypothesis Protection

The Evolution Agent MUST:
- Create NEW hypothesis instances rather than modifying existing ones
- Preserve the integrity of tournament-validated hypotheses
- Ensure all evolved hypotheses compete for ranking

## Inputs

```yaml
evolution_task:
  task_id: string
  strategy: enum[enhancement, combination, simplification, out_of_box]
  source_hypotheses:
    - hypothesis_id: string
      elo_rating: number
      tournament_wins: number
      tournament_losses: number
      content:
        summary: string
        full_description: string
        experimental_protocol: string
        testability_score: number
  meta_review_feedback: optional
    synthesis: string
    improvement_suggestions: list[string]
  context:
    research_goal: string
    domain_constraints: list[string]
    existing_hypothesis_count: number
```

## Outputs

```yaml
evolved_hypothesis:
  task_id: string
  parent_hypotheses: list[string]  # IDs of source hypotheses
  evolution_strategy: string
  hypothesis:
    summary: string
    full_description: string
    experimental_protocol: string
    key_improvements: list[string]
    evolution_rationale: string
  metadata:
    created_timestamp: datetime
    evolution_path: string  # e.g., "enhancement->combination"
```

## Behavioral Contracts

### Enhancement Strategy
The agent MUST:
- Identify at least one specific weakness in the source hypothesis
- Provide literature-backed improvements when using web search
- Maintain the core research direction while addressing gaps
- Document the enhancement rationale

### Combination Strategy
The agent MUST:
- Select 2-5 complementary hypotheses for combination
- Identify non-conflicting elements from each source
- Create a coherent merged hypothesis, not a simple concatenation
- Explain how the combination improves upon individual components

### Simplification Strategy
The agent MUST:
- Reduce experimental complexity by at least 30%
- Maintain the core scientific insight
- Improve testability score
- Document what was removed and why

### Out-of-Box Strategy
The agent MUST:
- Generate variations that differ substantially from source
- Apply cross-domain analogies when possible
- Maintain scientific plausibility
- Explain the divergent thinking approach used

## Interaction Protocols

### With Ranking Agent
1. Receive top-ranked hypotheses (typically Elo rating > 1200)
2. Access tournament performance data
3. Submit evolved hypotheses for new tournament evaluation

### With Meta-review Agent
1. Receive synthesis of feedback patterns
2. Incorporate improvement suggestions into evolution process
3. Align evolution strategies with identified research gaps

### With Web Search Interface
1. Query literature for enhancement evidence
2. Find analogies for out-of-box thinking
3. Validate feasibility of evolved approaches

### With Context Memory
1. Store evolution lineage for each hypothesis
2. Track which strategies produce successful variants
3. Access full tournament state and hypothesis repository

## Examples

### Example 1: Enhancement Strategy
```yaml
Input:
  strategy: enhancement
  source_hypothesis:
    summary: "JAK inhibitors for AML treatment"
    weakness: "Limited evidence for combination therapy"

Output:
  evolved_hypothesis:
    summary: "JAK inhibitors combined with BCL-2 inhibitors for AML"
    key_improvements:
      - "Added synergistic BCL-2 targeting based on recent Nature paper"
      - "Specified biomarker-driven patient selection criteria"
    evolution_rationale: "Literature search revealed promising JAK/BCL-2 combination data in preclinical AML models"
```

### Example 2: Combination Strategy
```yaml
Input:
  strategy: combination
  source_hypotheses:
    - "STING pathway activation for liver fibrosis"
    - "Macrophage reprogramming in fibrotic disease"

Output:
  evolved_hypothesis:
    summary: "STING-mediated macrophage reprogramming for liver fibrosis reversal"
    key_improvements:
      - "Integrated STING activation with macrophage targeting"
      - "Combined molecular mechanism with cellular approach"
    evolution_rationale: "STING pathway can drive macrophage polarization, creating synergy"
```

### Example 3: Simplification Strategy
```yaml
Input:
  strategy: simplification
  source_hypothesis:
    summary: "Multi-omics approach with proteomics, metabolomics, and transcriptomics for AMR detection"

Output:
  evolved_hypothesis:
    summary: "Targeted metabolomics panel for rapid AMR detection"
    key_improvements:
      - "Focused on metabolomics alone for faster results"
      - "Reduced from 3 platforms to 1"
      - "Decreased time to result from 72h to 6h"
    evolution_rationale: "Metabolomics showed strongest signal in preliminary data"
```

### Example 4: Out-of-Box Strategy
```yaml
Input:
  strategy: out_of_box
  source_hypothesis:
    summary: "Small molecule inhibitors for antimicrobial resistance"

Output:
  evolved_hypothesis:
    summary: "Engineered bacteriophage cocktails with CRISPR payloads for precision AMR treatment"
    key_improvements:
      - "Shifted from chemical to biological intervention"
      - "Applied synthetic biology approach"
      - "Enabled strain-specific targeting"
    evolution_rationale: "Applied viral engineering concepts from cancer immunotherapy to infectious disease"
```

## Performance Characteristics

The Evolution Agent SHOULD:
- Process evolution tasks within 60 seconds
- Generate hypotheses that achieve >20% tournament win rate
- Produce at least 1 successful variant per 5 attempts
- Adapt strategy selection based on tournament feedback

## Error Handling

The agent MUST handle:
- Insufficient source hypotheses for combination (fallback to enhancement)
- Web search failures (proceed with cached knowledge)
- Invalid evolution strategies (log error, skip task)
- Hypothesis generation failures (report to Supervisor, retry with different strategy)
---

### 012 meta review agent

# Meta-review Agent Specification

**Type**: Agent  
**Interactions**: Supervisor Agent, Context Memory, All Other Agents (via feedback)

## Prerequisites
- Read: Reflection Agent Specification (for understanding review types)
- Read: Ranking Agent Specification (for tournament debate patterns)
- Understand: Feedback propagation concepts from System Overview

## Overview

The Meta-review Agent synthesizes insights from all reviews and tournament debates, identifying recurring patterns and generating feedback to improve the system's performance in subsequent iterations. It also produces comprehensive research overviews and identifies potential research contacts. This agent enables the AI Co-Scientist's continuous self-improvement without requiring back-propagation or fine-tuning.

## Core Behaviors

### Pattern Synthesis
- Analyzes all review outputs from Reflection Agent
- Examines tournament debate transcripts from Ranking Agent
- Identifies recurring themes, critiques, and recommendations
- Detects systematic issues across multiple hypotheses
- Recognizes successful patterns that lead to high-quality hypotheses

### Feedback Generation
- Creates actionable feedback for each agent type
- Tailors feedback to agent-specific responsibilities
- Prioritizes critical issues that affect hypothesis quality
- Balances comprehensive coverage with concise recommendations
- Ensures feedback improves future iterations without overfitting

### Research Overview Generation
- Synthesizes top-ranked hypotheses into coherent research directions
- Organizes hypotheses by thematic areas
- Justifies importance of each research direction
- Suggests specific experiments within each area
- Formats output according to specified templates (e.g., NIH Specific Aims)

### Research Contact Identification
- Analyzes literature references from hypothesis generation
- Identifies domain experts relevant to research hypotheses
- Provides reasoning for each suggested contact
- Groups contacts by expertise area
- Includes contact information when available in public sources

## Inputs

### From Supervisor Agent
```
Input Structure:
  - task_type: "generate_meta_review" | "create_research_overview"
  - iteration_number: integer
  - research_goal: string
  - target_format: string (optional, e.g., "NIH_specific_aims")
  - feedback_config:
    - include_all_agents: boolean
    - priority_threshold: float
    - synthesis_depth: "summary" | "detailed"
```

### From Context Memory
```
Retrieved Data:
  - reflection_reviews: List[
      - hypothesis_id: string
      - review_type: string
      - review_content: string
      - identified_issues: List[string]
      - strengths: List[string]
      - recommendations: List[string]
    ]
  - tournament_debates: List[
      - match_id: string
      - hypothesis_1_id: string
      - hypothesis_2_id: string
      - debate_transcript: string
      - decision_rationale: string
      - key_arguments: List[string]
    ]
  - hypothesis_rankings: List[
      - hypothesis_id: string
      - elo_rating: float
      - rank_position: integer
    ]
  - previous_meta_reviews: List[meta_review] (if any)
```

## Outputs

### Meta-review Critique
```
Critique Structure:
  - synthesis_summary: string
  - common_patterns: List[
      - pattern_type: string
      - frequency: integer
      - description: string
      - impact_on_quality: "high" | "medium" | "low"
      - examples: List[hypothesis_id]
    ]
  - agent_specific_feedback:
    - generation_agent:
      - strengths: List[string]
      - improvement_areas: List[string]
      - specific_recommendations: List[string]
    - reflection_agent:
      - missed_issues: List[string]
      - review_consistency: float
      - suggested_focus_areas: List[string]
    - ranking_agent:
      - debate_quality: string
      - ranking_consistency: float
      - improvement_suggestions: List[string]
    - evolution_agent:
      - evolution_effectiveness: string
      - diversity_assessment: string
      - strategy_recommendations: List[string]
  - iteration_improvements:
    - metrics_comparison: object
    - progress_indicators: List[string]
    - next_iteration_priorities: List[string]
```

### Research Overview
```
Overview Structure:
  - executive_summary: string
  - research_areas: List[
      - area_title: string
      - importance_justification: string
      - key_hypotheses: List[
          - hypothesis_id: string
          - hypothesis_summary: string
          - elo_rating: float
        ]
      - proposed_experiments: List[
          - experiment_description: string
          - expected_outcomes: string
          - resource_requirements: string
        ]
      - related_literature: List[citation]
    ]
  - cross_cutting_themes: List[string]
  - innovation_highlights: List[string]
  - risk_assessment: string
  - recommended_next_steps: List[string]
  - potential_collaborators: List[research_contact]
```

### Research Contacts
```
Contact Structure:
  - contacts: List[
      - name: string (redacted if needed)
      - institution: string
      - expertise_areas: List[string]
      - relevance_reasoning: string
      - relevant_publications: List[citation]
      - contact_priority: "high" | "medium" | "low"
    ]
  - expertise_gaps: List[string]
  - collaboration_opportunities: List[string]
```

## Behavioral Contracts

### Pattern Recognition
- MUST analyze ALL available reviews and debates
- MUST identify patterns that appear in >20% of reviews
- MUST distinguish between systematic and isolated issues
- MUST weight patterns by their impact on hypothesis quality
- SHOULD recognize both positive and negative patterns

### Feedback Quality
- MUST provide actionable, specific feedback
- MUST avoid overly general recommendations
- MUST tailor feedback to each agent's capabilities
- MUST prioritize high-impact improvements
- SHOULD balance criticism with recognition of strengths

### Overview Coherence
- MUST organize hypotheses into logical research areas
- MUST provide clear justification for each area's importance
- MUST ensure proposed experiments are feasible
- MUST maintain consistency with research goal
- SHOULD identify synergies between research areas

### Contact Identification
- MUST base suggestions on actual literature citations
- MUST provide clear reasoning for each contact
- MUST respect privacy (redact names when appropriate)
- SHOULD identify diverse expertise areas
- SHOULD prioritize based on relevance to hypotheses

## Interaction Protocols

### With Supervisor Agent
```
1. Receive meta-review generation task
2. Request relevant data from Context Memory
3. Process reviews and debates systematically
4. Generate comprehensive feedback and/or overview
5. Return results with confidence metrics
6. Update task status to "completed"
```

### With Context Memory
```
1. Query all reviews for current iteration
2. Retrieve tournament debates and results
3. Access hypothesis rankings and details
4. Fetch previous meta-reviews for comparison
5. Store generated meta-review and overview
6. Maintain version history
```

### Feedback Propagation
```
1. Feedback appended to agent prompts in next iteration
2. No direct agent communication required
3. Feedback persists across iterations
4. Agents adapt behavior based on feedback
5. System improves without fine-tuning
```

## Examples

### Example 1: Common Pattern Identification
```
Scenario: ALS drug repurposing research

Reviews analyzed: 45 hypothesis reviews, 120 tournament debates

Identified patterns:
1. Blood-brain barrier issue (38/45 reviews, 84%)
   - Many proposed drugs cannot cross BBB
   - Impact: High - renders hypothesis non-viable
   - Recommendation: Check BBB permeability early

2. Incomplete mechanism description (22/45 reviews, 49%)
   - Hypotheses lack detailed pathway analysis
   - Impact: Medium - affects experimental design
   - Recommendation: Require pathway diagrams

3. Missing dosage considerations (28/45 reviews, 62%)
   - Clinical relevance unclear without dosing
   - Impact: Medium - affects feasibility
   - Recommendation: Include therapeutic window analysis
```

### Example 2: Agent-Specific Feedback
```
Generation Agent Feedback:
- Strengths:
  - Excellent literature grounding (95% with citations)
  - Creative combination of existing drugs
  - Good coverage of different mechanism classes
  
- Improvement Areas:
  - Consider BBB permeability constraints upfront
  - Include more specific molecular targets
  - Address potential drug interactions
  
- Specific Recommendations:
  1. Add BBB permeability check to hypothesis template
  2. Require identification of specific protein targets
  3. Include preliminary safety assessment

Reflection Agent Feedback:
- Missed Issues:
  - Overlooked drug interaction risks in 30% of reviews
  - Inconsistent evaluation of novelty claims
  
- Suggested Focus Areas:
  1. Standardize novelty assessment criteria
  2. Always check for drug-drug interactions
  3. Verify experimental feasibility claims
```

### Example 3: Research Overview (NIH Format)
```
Research Goal: "Novel treatments for liver fibrosis"

SPECIFIC AIMS

The long-term goal is to develop effective therapies for liver fibrosis, 
a major cause of morbidity affecting millions worldwide. Based on our 
AI-assisted hypothesis generation, we propose three innovative approaches:

Aim 1: Investigate epigenetic modulators for fibrosis reversal
- Test BET inhibitors in hepatic stellate cells
- Evaluate HDAC6-specific inhibitors
- Assess combination epigenetic therapy

Aim 2: Develop targeted anti-fibrotic cytokine delivery
- Engineer IL-10 variants with enhanced stability
- Create hepatocyte-specific delivery vectors
- Test in humanized liver organoids

Aim 3: Explore CRISPR-based stellate cell reprogramming
- Design guide RNAs for key fibrotic genes
- Develop AAV-based delivery system
- Validate in patient-derived organoids

Expected Outcomes: These studies will identify 2-3 lead candidates
for preclinical development, potentially transforming fibrosis treatment.
```

## Performance Characteristics

### Processing Requirements
- Review analysis: O(n*m) where n=hypotheses, m=review types
- Pattern detection: O(n²) for cross-hypothesis patterns
- Feedback generation: O(a) where a=number of agents
- Overview synthesis: O(n log n) for hypothesis ranking

### Quality Metrics
- Pattern detection accuracy: >85% agreement with expert analysis
- Feedback actionability: >90% of recommendations implementable
- Overview coherence: >4.0/5.0 expert rating
- Contact relevance: >80% appropriate suggestions

### Timing Constraints
- Meta-review generation: Complete within 5 minutes
- Research overview: Format within 10 minutes
- Feedback propagation: Available for next iteration
- Contact identification: Real-time during overview generation
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

## Quality Requirements
- Maintain 100% test pass rate for must-pass tests
- Follow specification requirements exactly
- Implement atomic features only
- Use BAML for all content generation methods
- Maintain ≥80% test coverage

## Context Optimization
This prompt has been optimized to include only specifications relevant to the current task.
If additional context is needed, the system will automatically fall back to full specifications.

Generated at: Fri Sep 26 10:29:58 CDT 2025
Task: Phase 10: Create ReflectionAgent class
Selected specifications:        6 of       28 total
