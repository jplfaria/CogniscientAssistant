# Proximity Agent Specification

**Type**: Agent  
**Interactions**: Supervisor Agent, Context Memory, Ranking Agent, Meta-review Agent, Evolution Agent

## Prerequisites
- Read: System Overview and Architecture Specification
- Read: Multi-Agent Framework Specification
- Read: Context Memory System Specification
- Understand: Graph data structures and similarity metrics

## Purpose
The Proximity Agent is a non-generative agent responsible for computing semantic similarity relationships between research hypotheses and maintaining a proximity graph that enables efficient exploration, clustering, and de-duplication of the hypothesis landscape within the context of the current research goal.

## Agent Behavior
1. **Calculate Hypothesis Similarity**: Compute semantic similarity scores between pairs of hypotheses considering the research goal context
2. **Build Proximity Graph**: Construct and maintain a graph structure where nodes are hypotheses and weighted edges represent similarity relationships
3. **Enable Hypothesis Clustering**: Support grouping of related hypotheses by providing graph-based clustering information
4. **Detect Near-Duplicates**: Identify hypotheses that are semantically too similar to prevent redundant exploration
5. **Facilitate Landscape Navigation**: Provide structured access to the hypothesis space for efficient browsing and exploration
6. **Update Graph Incrementally**: Process new hypotheses asynchronously and integrate them into the existing proximity graph

## Inputs

### From Supervisor Agent
```
ProximityTask {
  task_type: "compute_similarity" | "update_graph" | "find_similar" | "check_duplicate"
  hypothesis_ids: List[string]  # IDs of hypotheses to process
  threshold?: float  # Optional similarity threshold for operations
  max_results?: int  # Optional limit for similar hypothesis queries
}
```

### From Context Memory
```
Hypothesis {
  id: string
  summary: string
  full_description: string
  experimental_protocol: string
  timestamp: datetime
  metadata: {
    evolution_source?: string[]  # IDs of parent hypotheses if evolved
    generation_method?: string
  }
}

ResearchGoal {
  goal_text: string
  domain: string
  constraints: List[string]
}
```

## Outputs

### To Context Memory
```
ProximityGraph {
  nodes: List[{
    hypothesis_id: string
    embedding?: vector  # Optional: cached embedding for efficiency
  }]
  edges: List[{
    source_id: string
    target_id: string
    similarity_score: float  # 0.0 to 1.0
    similarity_type: "semantic" | "methodological" | "domain"
  }]
  clusters: List[{
    cluster_id: string
    hypothesis_ids: List[string]
    centroid_id: string  # Most representative hypothesis
    coherence_score: float
  }]
  last_updated: datetime
}

DuplicationReport {
  hypothesis_id: string
  duplicates: List[{
    duplicate_id: string
    similarity_score: float
    overlap_aspects: List[string]  # e.g., ["method", "outcome", "target"]
  }]
  recommendation: "keep" | "merge" | "discard"
}
```

## Core Functionality

### Similarity Computation

**Behavior**: Calculate context-aware semantic similarity between hypothesis pairs

**Process**:
1. Extract key aspects from each hypothesis (summary, methodology, expected outcomes)
2. Apply research goal as context for relevance weighting
3. Compute multi-dimensional similarity scores
4. Aggregate into final similarity metric

**Example**:
```
Research Goal: "Develop novel antimicrobial compounds"
Hypothesis A: "Use peptide libraries to identify AMR inhibitors"
Hypothesis B: "Screen natural product extracts for antimicrobial activity"
Similarity Score: 0.75 (high methodological similarity, moderate target similarity)
```

### Graph Construction and Maintenance

**Behavior**: Build and incrementally update the proximity graph structure

**Operations**:
- **Initialize Graph**: Create empty graph structure for new research session
- **Add Nodes**: Insert new hypotheses as nodes when generated
- **Compute Edges**: Calculate similarities for new nodes against existing ones
- **Prune Edges**: Remove edges below threshold to maintain graph sparsity
- **Update Clusters**: Recompute clustering when graph structure changes significantly

### Clustering and Organization

**Behavior**: Group similar hypotheses to reveal research landscape structure

**Clustering Strategies**:
1. **Density-based Clustering**: Identify dense regions in similarity space
2. **Hierarchical Clustering**: Create nested groups at different similarity levels
3. **Topic-based Clustering**: Group by dominant research themes

**Example Output**:
```
Cluster: "Peptide-based Approaches"
- Members: 5 hypotheses
- Centroid: "Antimicrobial peptide library screening"
- Coherence: 0.82
- Key themes: ["peptides", "screening", "structure-activity"]
```

### Duplicate Detection

**Behavior**: Identify overly similar hypotheses to maintain diversity

**Detection Criteria**:
- Similarity score above configurable threshold (default: 0.95)
- Matching on multiple dimensions (method, target, expected outcome)
- Consideration of hypothesis metadata (generation method, evolution source)

**Actions**:
- Flag near-duplicates for review
- Suggest merge operations for highly similar variants
- Track duplication patterns to inform generation strategies

## Integration Patterns

### With Ranking Agent
- Ranking Agent queries proximity graph to optimize tournament pairings
- Similar hypotheses are preferentially matched in early rounds
- Graph structure informs comparison context

### With Evolution Agent
- Evolution Agent uses proximity data to find combinable hypotheses
- Graph identifies conceptually distant hypotheses for cross-pollination
- Clustering information guides evolution strategies

### With Meta-review Agent
- Meta-review Agent accesses clusters to identify review patterns
- Similar hypotheses may share common strengths/weaknesses
- Cluster-level insights inform meta-review summaries

## State Management

### Read Operations
- Current proximity graph structure
- Hypothesis details for similarity computation
- Research goal for context
- Configuration parameters (thresholds, limits)

### Write Operations
- Updated proximity graph with new nodes/edges
- Clustering assignments and metrics
- Duplication reports and recommendations
- Graph statistics and metadata

## Error Handling

1. **Incomplete Hypothesis Data**
   - Use available fields for partial similarity computation
   - Flag hypotheses with insufficient data
   - Maintain graph consistency with placeholder nodes

2. **Graph Scaling Issues**
   - Implement edge pruning for graphs exceeding size limits
   - Use approximate similarity methods for large hypothesis sets
   - Batch process updates to manage computational load

3. **Similarity Computation Failures**
   - Fallback to simpler similarity metrics
   - Cache successful computations
   - Report computation errors without blocking graph updates

## Configuration

```
proximity_agent_config {
  similarity_threshold: 0.3  # Minimum score for edge creation
  duplicate_threshold: 0.95  # Score above which hypotheses are duplicates
  max_edges_per_node: 10    # Limit connections for graph sparsity
  clustering_method: "density"  # Options: density, hierarchical, topic
  update_batch_size: 20      # Process new hypotheses in batches
  embedding_cache: true      # Cache embeddings for efficiency
}
```

## Performance Metrics

1. **Graph Coverage**: Percentage of hypotheses with computed similarities
2. **Clustering Quality**: Average cluster coherence score
3. **Duplicate Detection Rate**: Number of duplicates identified vs. total hypotheses
4. **Update Latency**: Time to integrate new hypotheses into graph
5. **Graph Connectivity**: Average degree and component analysis

## Examples

### Example 1: New Hypothesis Integration
```
Input:
  task_type: "update_graph"
  hypothesis_ids: ["hyp_234"]

Process:
  1. Retrieve hypothesis "hyp_234" details
  2. Compute similarities with 50 existing hypotheses
  3. Add top 10 edges (scores > 0.3) to graph
  4. Update cluster assignments
  5. Check for duplicates

Output:
  - Added 8 new edges
  - Assigned to cluster "Natural Products"
  - No duplicates detected
  - Graph updated successfully
```

### Example 2: Duplicate Detection
```
Input:
  task_type: "check_duplicate"
  hypothesis_ids: ["hyp_456"]
  threshold: 0.9

Output:
  DuplicationReport {
    hypothesis_id: "hyp_456"
    duplicates: [{
      duplicate_id: "hyp_123"
      similarity_score: 0.96
      overlap_aspects: ["method", "target", "mechanism"]
    }]
    recommendation: "merge"
  }
```

### Example 3: Finding Similar Hypotheses
```
Input:
  task_type: "find_similar"
  hypothesis_ids: ["hyp_789"]
  max_results: 5

Output:
  similar_hypotheses: [
    {id: "hyp_234", score: 0.82, reason: "Similar enzymatic approach"},
    {id: "hyp_567", score: 0.75, reason: "Related molecular target"},
    {id: "hyp_890", score: 0.71, reason: "Comparable screening method"},
    {id: "hyp_345", score: 0.68, reason: "Overlapping compound class"},
    {id: "hyp_678", score: 0.65, reason: "Similar validation strategy"}
  ]
```

## Boundaries

### What the Proximity Agent Does
- Compute semantic similarities between hypotheses
- Maintain and update proximity graph structure
- Identify clusters and patterns in hypothesis landscape
- Detect near-duplicate hypotheses
- Provide graph-based navigation capabilities

### What the Proximity Agent Does Not Do
- Generate new hypotheses (handled by Generation Agent)
- Evaluate hypothesis quality (handled by Reflection Agent)
- Rank hypotheses competitively (handled by Ranking Agent)
- Modify or merge hypotheses (handled by Evolution Agent)
- Make final decisions on hypothesis selection (handled by Supervisor Agent)