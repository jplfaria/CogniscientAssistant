# Generation Agent Specification

**Type**: Agent  
**Interactions**: Supervisor Agent, Context Memory, Web Search, Meta-review Agent

## Prerequisites
- Read: [001-system-overview.md] (for understanding system goals)
- Read: [004-multi-agent-architecture.md] (for agent collaboration patterns)
- Read: [005-supervisor-agent.md] (for task assignment and orchestration)
- Understand: Research plan configuration from Supervisor Agent

## Overview

The Generation Agent initiates the research process by creating novel hypotheses and research proposals that address a given research goal. It employs multiple strategies including literature exploration, scientific debates, and iterative refinement to produce scientifically grounded and potentially groundbreaking hypotheses.

## Behavior

The Generation Agent operates as an asynchronous worker process, receiving tasks from the Supervisor Agent's queue. It generates initial focus areas and iteratively extends them into concrete hypotheses with experimental protocols.

### Core Responsibilities
1. Parse research goals and constraints from the research plan configuration
2. Generate initial research focus areas based on the goal
3. Create novel hypotheses through multiple generation strategies
4. Ground hypotheses in existing literature while identifying gaps
5. Produce structured outputs with summaries and experimental protocols
6. Iterate based on feedback from the Meta-review Agent

### Generation Strategies

#### Literature Exploration via Web Search
- Iteratively search for relevant research articles
- Retrieve and analyze scientific publications
- Summarize existing work to identify knowledge gaps
- Build upon prior findings to propose novel directions
- Maintain citations and evidence trails

#### Simulated Scientific Debates
- Employ self-play techniques to refine hypotheses
- Simulate expert discussions with multiple perspectives
- Conduct multi-turn debates leading to refined outputs
- Challenge assumptions through dialectical reasoning
- Synthesize opposing viewpoints into stronger hypotheses

#### Iterative Assumptions Identification
- Identify testable intermediate assumptions
- Decompose complex hypotheses into sub-assumptions
- Use conditional reasoning to explore implications
- Aggregate plausible assumptions into complete hypotheses
- Ensure each assumption can lead to scientific discovery

#### Research Expansion
- Review existing hypotheses in Context Memory
- Analyze feedback from Meta-review Agent
- Identify unexplored areas of the hypothesis space
- Generate complementary or alternative approaches
- Avoid redundancy while maintaining diversity

## Inputs

### From Supervisor Agent
```
ResearchPlanConfiguration:
  - goal: string (natural language research objective)
  - constraints: list[string] (laboratory, ethical, resource constraints)
  - preferences: dict (novelty weight, feasibility requirements)
  - evaluation_criteria: list[string] (what constitutes success)
  - prior_work: optional[list[document]] (PDFs, papers to consider)
```

### From Context Memory
```
SystemState:
  - existing_hypotheses: list[Hypothesis]
  - meta_review_feedback: optional[string]
  - generation_statistics: dict
  - iteration_count: int
```

### From Web Search Tool
```
SearchResults:
  - articles: list[ScientificArticle]
  - relevance_scores: list[float]
  - abstracts: list[string]
  - full_text_available: list[bool]
```

## Outputs

### Generated Hypothesis Structure
```
Hypothesis:
  - id: string (unique identifier)
  - summary: string (concise one-sentence description)
  - category: string (mechanistic, therapeutic, diagnostic, etc.)
  - full_description: string (detailed explanation)
  - novelty_claim: string (what makes this novel)
  - assumptions: list[string] (key assumptions made)
  - experimental_protocol: ExperimentalProtocol
  - supporting_evidence: list[Citation]
  - confidence_score: float (0-1)
  - generation_method: string (which strategy was used)
```

### Experimental Protocol Structure
```
ExperimentalProtocol:
  - objective: string
  - methodology: string (step-by-step approach)
  - required_resources: list[string]
  - timeline: string (estimated duration)
  - success_metrics: list[string]
  - potential_challenges: list[string]
  - safety_considerations: list[string]
```

### Summary Output for Scientists
```
HypothesisSummary:
  - core_idea: string (accessible explanation)
  - scientific_impact: string (why this matters)
  - feasibility_assessment: string
  - next_steps: list[string]
```

## Behavior Contracts

### Quality Guarantees
1. Every hypothesis MUST be grounded in scientific literature
2. All assumptions MUST be explicitly stated
3. Experimental protocols MUST be actionable and specific
4. Novel aspects MUST be clearly differentiated from existing work
5. Citations MUST be provided for all claims

### Iteration Behavior
1. WHEN receiving meta-review feedback, incorporate insights into new generations
2. WHEN hypothesis space is saturated, explore alternative generation strategies
3. WHEN confidence is low, conduct additional literature exploration
4. WHEN debates reach impasse, synthesize opposing views into new hypothesis

### Error Handling
1. IF web search fails, continue with cached literature knowledge
2. IF hypothesis generation produces duplicates, filter and regenerate
3. IF constraints conflict, prioritize safety and ethics
4. IF no novel hypotheses emerge, report saturation to Supervisor

## Interaction Protocols

### With Supervisor Agent
- RECEIVE: Task assignment with research plan configuration
- SEND: Generated hypotheses batch
- SEND: Progress updates and statistics
- RECEIVE: Resource allocation adjustments

### With Context Memory
- READ: Previous hypotheses and system state
- WRITE: New hypotheses and generation metadata
- READ: Meta-review feedback from previous iterations

### With Web Search Tool
- SEND: Targeted queries for specific topics
- RECEIVE: Relevant articles and abstracts
- SEND: Follow-up queries based on findings

### With Meta-review Agent (Indirect)
- RECEIVE: Synthesized feedback via Context Memory
- ADAPT: Generation strategies based on patterns identified

## Performance Characteristics

### Success Metrics
- Number of novel hypotheses generated per iteration
- Hypothesis quality scores from reviews
- Diversity of hypothesis categories
- Grounding quality (citation density and relevance)
- Iteration-over-iteration improvement rate

### Resource Usage
- Computation scales with literature search depth
- Memory usage proportional to hypothesis count
- API calls for web search (rate-limited)
- LLM tokens for generation and debates

## Examples

### Example 1: Drug Repurposing for AML
**Input**: "Identify existing FDA-approved drugs that could be repurposed for acute myeloid leukemia treatment"

**Output**: Hypothesis proposing KIRA6 (an IRE1α inhibitor) for AML treatment based on:
- Literature showing ER stress in AML cells
- KIRA6's mechanism targeting this pathway
- Experimental protocol for in vitro validation
- IC50 predictions in AML cell lines

### Example 2: Liver Fibrosis Target Discovery
**Input**: "Discover novel epigenetic targets for treating liver fibrosis"

**Output**: Multiple hypotheses identifying specific histone deacetylases and methyltransferases with:
- Mechanistic rationale for anti-fibrotic activity
- Human hepatic organoid experimental protocols
- Literature support from related fibrotic diseases

### Example 3: AMR Mechanism Explanation
**Input**: "Explain how cf-PICIs exist across multiple bacterial species"

**Output**: Hypothesis proposing cf-PICI interaction with diverse phage tails:
- Mechanism for expanded host range
- Evolutionary advantages explained
- Experimental validation approach
- Predictions for specific bacterial species

## Safety Considerations

1. All generated hypotheses undergo initial safety screening
2. Experimental protocols include safety warnings
3. Potentially dangerous research directions are flagged
4. Ethical considerations are embedded in all outputs
5. Dual-use research concerns trigger additional review

## Natural Language Examples

### Scientist Input
"I want to understand why certain cancer cells become resistant to immunotherapy. Focus on metabolic changes that might be involved."

### Generation Agent Process
1. Searches literature on immunotherapy resistance
2. Identifies metabolic pathways altered in resistant cells
3. Conducts debate on competing mechanisms
4. Generates hypothesis about specific metabolite accumulation
5. Designs experimental protocol using patient-derived samples
6. Outputs structured hypothesis with literature support

### Output Summary
"Hypothesis: Resistant cancer cells upregulate tryptophan metabolism, producing kynurenine that creates an immunosuppressive microenvironment. This can be validated by measuring metabolite levels in resistant vs. sensitive tumors and testing IDO inhibitors to restore immunotherapy response."