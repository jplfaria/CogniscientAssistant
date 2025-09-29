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