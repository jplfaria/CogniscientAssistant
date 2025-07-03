# AI Co-Scientist System Overview and Architecture Specification

**Type**: System Architecture  
**Interactions**: All system components

## Purpose

The AI Co-Scientist is a multi-agent system designed to augment scientific research by generating novel hypotheses and research proposals. The system operates as a collaborative tool for scientists, employing specialized agents that mirror the scientific method to iteratively generate, evaluate, and refine research outputs.

## System Behavior

The AI Co-Scientist system exhibits the following core behaviors:

1. **Research Goal Processing**: Accepts research goals specified in natural language from scientists
2. **Hypothesis Generation**: Creates novel scientific hypotheses grounded in existing literature
3. **Iterative Refinement**: Continuously improves hypothesis quality through debate, evaluation, and evolution
4. **Quality Assessment**: Ranks hypotheses using tournament-based evaluation with Elo ratings
5. **Research Synthesis**: Produces comprehensive research overviews and experimental protocols
6. **Human Collaboration**: Incorporates scientist feedback and guidance throughout the process

## System Components

### Core Processing Components

**Supervisor Agent**
- Orchestrates the entire system by managing task queues and resource allocation
- Parses research goals into research plan configurations
- Assigns specialized agents to worker processes based on system state
- Monitors progress and determines when terminal states are reached

**Specialized Agents**
- Generation Agent: Creates initial hypotheses through literature exploration and scientific debate
- Reflection Agent: Reviews hypotheses for correctness, novelty, and quality
- Ranking Agent: Conducts tournaments to evaluate and prioritize hypotheses
- Evolution Agent: Refines and improves existing hypotheses
- Proximity Agent: Calculates similarity between hypotheses for clustering
- Meta-review Agent: Synthesizes feedback and generates research overviews

**Supporting Infrastructure**
- Worker Processes: Execute agent tasks asynchronously
- Context Memory: Persists system state and enables iterative computation
- Tool Interface: Provides access to web search and specialized AI models

## System Inputs

**Primary Input**: Research Goal
- Natural language description of the scientific objective
- May include constraints, preferences, and desired attributes
- Can incorporate existing research documents and prior work
- Supports multimodal input (text and documents)

**Secondary Inputs**:
- Scientist feedback on generated hypotheses
- Manual hypothesis reviews
- Scientist-provided seed ideas
- Research direction refinements

## System Outputs

**Primary Outputs**:
1. **Ranked Hypotheses**: Prioritized list of research hypotheses with:
   - Hypothesis text and summary
   - Experimental protocols
   - Literature grounding and citations
   - Elo ratings and rankings

2. **Research Overview**: Comprehensive synthesis including:
   - Research roadmap and future directions
   - Categorized hypothesis areas
   - Suggested experiments
   - Potential research contacts

**Output Formats**:
- Natural language explanations
- Structured research proposals (NIH Specific Aims format)
- Experimental design protocols

## System Workflow

1. **Initialization**
   - Scientist provides research goal
   - System parses goal into research plan configuration
   - Supervisor initializes task queue

2. **Generation Phase**
   - Generation Agent creates initial hypotheses
   - Multiple generation strategies employed (literature search, debate, assumption identification)

3. **Review Phase**
   - Reflection Agent performs multiple review types
   - Reviews assess novelty, correctness, quality, and safety

4. **Ranking Phase**
   - Ranking Agent conducts Elo-based tournaments
   - Hypotheses compete through scientific debates
   - Rankings updated based on tournament results

5. **Evolution Phase**
   - Evolution Agent improves top-ranked hypotheses
   - Multiple refinement strategies applied
   - New hypotheses generated from existing ones

6. **Synthesis Phase**
   - Meta-review Agent identifies patterns and feedback
   - Research overview generated
   - Results formatted for scientist consumption

## Key System Properties

**Asynchronous Execution**
- Agents operate independently as worker processes
- Task queue enables flexible resource allocation
- System scales computation based on needs

**Iterative Improvement**
- Self-improving feedback loops through meta-review
- Test-time compute scaling for enhanced reasoning
- Continuous refinement until quality thresholds met

**Human-Centric Design**
- Natural language interface for all interactions
- Multiple touchpoints for scientist intervention
- Transparent reasoning and explanations

## Quality Assurance Mechanisms

**Multi-Level Review System**
- Initial review for basic quality checks
- Full review with literature grounding
- Deep verification of assumptions
- Observation review for experimental validation
- Simulation review for mechanism testing
- Tournament review based on competition results

**Safety Safeguards**
- Research goal safety evaluation
- Hypothesis safety review
- Continuous monitoring of research directions
- Comprehensive activity logging

## System Boundaries

**What the System Does**:
- Generates novel, testable hypotheses
- Grounds proposals in existing literature
- Ranks and prioritizes research directions
- Synthesizes complex information
- Facilitates human-AI collaboration

**What the System Does Not Do**:
- Conduct actual experiments
- Make final research decisions
- Replace human scientific judgment
- Access proprietary databases without permission
- Generate unsafe or unethical research

## Success Criteria

A successful AI Co-Scientist system will:
1. Generate hypotheses that improve in quality over time (measured by Elo ratings)
2. Produce outputs aligned with scientist-specified research goals
3. Ground all proposals in verifiable literature
4. Maintain safety and ethical standards
5. Enable efficient scientist collaboration
6. Scale computation effectively for complex problems

## Error Conditions

The system must handle:
- Invalid or unsafe research goals
- Literature search failures
- Tool unavailability
- Conflicting scientist feedback
- Resource constraints
- Hypothesis generation failures

## Integration Points

**External Tools**:
- Web search APIs for literature access
- Specialized AI models (e.g., AlphaFold)
- Document processing systems
- Citation databases

**Human Interfaces**:
- Natural language chat interface
- Hypothesis review interface
- Research goal refinement tools
- Feedback submission mechanisms