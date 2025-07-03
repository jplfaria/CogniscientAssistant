# Generation Agent Specification

**Type**: Agent  
**Interactions**: Supervisor Agent, Context Memory, Web Search Tools, Meta-review Agent

## Prerequisites
- Read: System Overview and Architecture Specification
- Read: Multi-Agent Framework Specification
- Read: Context Memory System Specification

## Purpose

The Generation Agent initiates the research process by creating novel scientific hypotheses and research proposals aligned with the scientist's research goal. It employs multiple hypothesis generation techniques including literature exploration, scientific debates, and assumption identification to explore the hypothesis space and produce diverse, grounded proposals.

## Agent Behavior

The Generation Agent exhibits the following behaviors:

1. **Initial Focus Area Generation**: Creates initial research focus areas based on the research goal
2. **Literature-Grounded Hypothesis Creation**: Searches and synthesizes scientific literature to generate novel hypotheses
3. **Scientific Debate Simulation**: Engages in self-play debates to refine and improve hypotheses
4. **Assumption Identification**: Discovers testable intermediate assumptions that could lead to breakthroughs
5. **Research Space Expansion**: Reviews existing work to identify unexplored areas
6. **Hypothesis Categorization**: Summarizes and categorizes generated hypotheses for quick understanding

## Inputs

### From Research Configuration
```
ResearchGoal {
  goal_description: string (natural language)
  preferences: dict
  constraints: list[string]
  attributes: dict
  domain_focus: string (optional)
  prior_publications: list[PDF] (optional)
}
```

### From Context Memory
```
PriorState {
  existing_hypotheses: list[Hypothesis]
  research_overview: ResearchOverview (optional)
  meta_review_feedback: MetaReviewFeedback (optional)
  generation_statistics: dict
}
```

### From Meta-review Agent
```
GenerationFeedback {
  common_issues: list[string]
  improvement_suggestions: list[string]
  unexplored_areas: list[string]
  quality_patterns: dict
}
```

## Outputs

### Hypothesis Structure
```
Hypothesis {
  id: string
  title: string
  summary: string (2-3 sentences)
  full_description: string
  category: string
  assumptions: list[Assumption]
  experimental_protocol: Protocol
  expected_outcomes: list[string]
  novelty_rationale: string
  grounding_citations: list[Citation]
  generation_method: string
  timestamp: datetime
}
```

### Assumption Structure
```
Assumption {
  statement: string
  testability: boolean
  sub_assumptions: list[Assumption]
  evidence_required: string
  priority: High | Medium | Low
}
```

### Protocol Structure
```
Protocol {
  overview: string
  steps: list[ExperimentalStep]
  required_resources: list[string]
  timeline: string
  feasibility_notes: string
}
```

## Generation Techniques

### 1. Literature Exploration via Web Search

**Behavior**:
- Formulates targeted search queries from research goal
- Retrieves and analyzes relevant research articles
- Identifies gaps and opportunities in existing work
- Synthesizes findings into novel hypotheses

**Process**:
1. Extract key concepts from research goal
2. Generate multiple search query variations
3. Retrieve top N relevant papers (typically 10-20)
4. Summarize current state of knowledge
5. Identify unexplored connections or gaps
6. Formulate hypothesis addressing identified opportunities

**Example Search Patterns**:
- "[disease] mechanism recent advances"
- "[target] [pathway] therapeutic potential"
- "[method] applications [domain] limitations"

### 2. Simulated Scientific Debates

**Behavior**:
- Creates multiple expert personas with different viewpoints
- Simulates multi-turn debates on hypothesis viability
- Refines hypotheses through dialectical process
- Captures debate insights in final hypothesis

**Debate Structure**:
```
ScientificDebate {
  participants: list[ExpertPersona]
  rounds: 3-5
  focus: Novelty | Feasibility | Impact
  conclusion: RefinedHypothesis
}
```

**Expert Personas**:
- Skeptical Reviewer (challenges assumptions)
- Domain Specialist (deep technical knowledge)
- Interdisciplinary Thinker (cross-domain connections)
- Practical Experimentalist (feasibility focus)

### 3. Iterative Assumption Identification

**Behavior**:
- Decomposes research goal into core questions
- Identifies plausible intermediate assumptions
- Builds assumption trees through conditional reasoning
- Aggregates testable assumptions into complete hypotheses

**Assumption Tree Example**:
```
Root: "Mechanism X causes Disease Y"
├── Assumption 1: "Protein A interacts with Protein B"
│   ├── Sub 1.1: "Binding occurs at Site S"
│   └── Sub 1.2: "Interaction is pH-dependent"
└── Assumption 2: "Pathway P is dysregulated"
    ├── Sub 2.1: "Upstream signal is amplified"
    └── Sub 2.2: "Downstream target is inhibited"
```

### 4. Research Expansion

**Behavior**:
- Analyzes existing hypothesis distribution in Context Memory
- Identifies underexplored areas from meta-review feedback
- Targets generation toward promising gaps
- Avoids redundancy with existing hypotheses

**Expansion Strategies**:
- Adjacent field exploration (e.g., cancer → neurodegeneration)
- Scale variation (molecular → systems level)
- Temporal exploration (acute → chronic effects)
- Methodological innovation (new experimental approaches)

## Quality Control Mechanisms

### Internal Validation
Before submitting a hypothesis, the Generation Agent:
1. Checks novelty against existing hypotheses in Context Memory
2. Verifies logical consistency of assumptions
3. Ensures experimental protocol is complete
4. Validates grounding citations exist
5. Confirms alignment with research goal

### Hypothesis Filtering Criteria
Hypotheses are discarded if they:
- Duplicate existing hypotheses (>80% similarity)
- Contain logical contradictions
- Lack testable predictions
- Fall outside research goal constraints
- Violate safety/ethical guidelines

## Tool Integration

### Web Search Usage
```
SearchRequest {
  query: string
  result_count: int (default: 10)
  date_filter: string (optional, e.g., "last_5_years")
  domain_filter: list[string] (optional)
  exclude_terms: list[string] (optional)
}
```

### Document Processing
- Extract key findings from PDFs
- Parse methodology sections
- Identify cited hypotheses
- Extract experimental data

### Citation Management
- Maintain bibliography of accessed sources
- Format citations consistently
- Track citation relevance scores
- Link citations to specific claims

## State Management

### Read Operations
- Query existing hypotheses to avoid duplication
- Access meta-review feedback for improvement
- Review research overview for context
- Check generation statistics for method effectiveness

### Write Operations
- Store new hypotheses with full metadata
- Update generation method statistics
- Log search queries and results
- Record debate transcripts for analysis

## Performance Optimization

### Parallel Generation
- Multiple hypothesis generation threads
- Different techniques run concurrently
- Results aggregated asynchronously
- Deduplication at collection point

### Caching Strategy
- Cache literature search results
- Store processed document summaries
- Reuse expert persona configurations
- Maintain assumption template library

### Resource Management
- Limit concurrent web searches to N (typically 5)
- Batch document processing requests
- Control debate simulation depth
- Manage memory for large PDF sets

## Error Handling

### Common Error Scenarios
1. **Web Search Failures**
   - Retry with exponential backoff
   - Fall back to cached results
   - Use alternative search queries

2. **Document Access Issues**
   - Skip inaccessible documents
   - Note missing citations
   - Proceed with available data

3. **Generation Loops**
   - Detect repetitive outputs
   - Inject randomness to break loops
   - Switch generation techniques

4. **Resource Exhaustion**
   - Pause generation temporarily
   - Clear intermediate caches
   - Resume with reduced batch size

## Integration Patterns

### With Supervisor Agent
- Receive generation tasks with parameters
- Report completion status and statistics
- Request additional resources if needed
- Signal when generation plateaus

### With Meta-review Agent
- Incorporate feedback on common issues
- Adjust generation strategies based on patterns
- Focus on addressing identified weaknesses
- Avoid over-fitting to review critiques

### With Context Memory
- Atomic hypothesis writes
- Bulk similarity queries
- Streaming search result storage
- Checkpoint generation state

## Success Metrics

The Generation Agent's effectiveness is measured by:
1. **Novelty Rate**: Percentage of hypotheses passing novelty review
2. **Diversity Score**: Coverage of hypothesis space
3. **Grounding Quality**: Citation relevance and recency
4. **Generation Efficiency**: Hypotheses per compute hour
5. **Downstream Success**: Percentage advancing past initial review

## Configuration Parameters

```
GenerationConfig {
  max_hypotheses_per_task: int (default: 10)
  search_results_per_query: int (default: 10)
  debate_rounds: int (default: 3)
  assumption_tree_depth: int (default: 3)
  parallel_generation_threads: int (default: 4)
  novelty_threshold: float (default: 0.8)
  enable_techniques: list[TechniqueType]
}
```

## Examples

### Drug Repurposing Hypothesis
```
Input: "Find novel drug repurposing opportunities for AML"
Output: Hypothesis proposing KIRA6 (IRE1α inhibitor) for AML treatment
- Based on: ER stress pathway literature
- Novel connection: IRE1α role in AML cell survival
- Protocol: In vitro dose-response in AML cell lines
```

### Mechanism Discovery Hypothesis  
```
Input: "Explain cf-PICI spread across bacterial species"
Output: Hypothesis about tail fiber interaction flexibility
- Based on: Phage biology and horizontal gene transfer
- Novel insight: Promiscuous tail recognition mechanism
- Protocol: Comparative genomics and binding assays
```

## Boundaries

**What the Generation Agent Does**:
- Creates novel, testable hypotheses
- Grounds proposals in scientific literature
- Provides detailed experimental protocols
- Explores diverse generation strategies
- Maintains hypothesis quality standards

**What the Generation Agent Does Not Do**:
- Evaluate hypothesis quality (Reflection Agent's role)
- Rank hypotheses (Ranking Agent's role)
- Modify existing hypotheses (Evolution Agent's role)
- Determine research priorities (Supervisor's role)
- Conduct actual experiments (External validation)