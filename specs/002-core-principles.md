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