# Proximity Agent Specification

**Type**: Agent  
**Interactions**: Supervisor Agent, Context Memory, Ranking Agent  

## Overview

The Proximity Agent calculates similarity between research hypotheses and proposals, building and maintaining a proximity graph. It assists in organizing hypotheses into related clusters and helps the Ranking Agent prioritize tournament matches between similar hypotheses. This agent ensures diverse yet coherent exploration of the research space.

## Core Behaviors

### Similarity Calculation
- Computes pairwise similarity scores between hypotheses
- Considers research goal context in similarity assessments
- Uses semantic understanding to identify conceptual relationships
- Updates similarity scores as hypotheses evolve

### Graph Construction
- Builds a proximity graph connecting related hypotheses
- Maintains edge weights representing similarity strength
- Identifies hypothesis clusters based on similarity thresholds
- Updates graph structure as new hypotheses are added

### Cluster Management
- Groups highly similar hypotheses into conceptual clusters
- Tracks cluster evolution over time
- Identifies outlier hypotheses exploring unique directions
- Provides cluster summaries for research overview

## Inputs

### From Supervisor Agent
```
Input Structure:
  - task_type: "calculate_proximity"
  - hypothesis_ids: List[string]
  - research_goal: string
  - similarity_config:
    - threshold: float (minimum similarity for edge creation)
    - clustering_method: "hierarchical" | "density_based"
    - update_existing: boolean
```

### From Context Memory
```
Retrieved Data:
  - hypothesis_details:
    - hypothesis_id: string
    - summary: string
    - full_description: string
    - experimental_approach: string
    - timestamp: datetime
  - existing_proximity_graph:
    - nodes: List[hypothesis_id]
    - edges: List[{source, target, weight}]
    - clusters: List[cluster_definition]
```

## Outputs

### Proximity Graph
```
Graph Structure:
  - nodes: List[
      - hypothesis_id: string
      - cluster_id: string (optional)
      - centrality_score: float
    ]
  - edges: List[
      - source_id: string
      - target_id: string
      - similarity_score: float (0.0 to 1.0)
      - similarity_type: string (conceptual|methodological|target-based)
    ]
  - graph_metrics:
    - density: float
    - average_clustering_coefficient: float
    - connected_components: integer
```

### Cluster Analysis
```
Cluster Structure:
  - clusters: List[
      - cluster_id: string
      - member_hypotheses: List[hypothesis_id]
      - cluster_theme: string
      - representative_hypothesis: hypothesis_id
      - internal_similarity: float
    ]
  - outliers: List[hypothesis_id]
  - cluster_relationships: List[{cluster_1, cluster_2, relationship_strength}]
```

### Similarity Report
```
Report Structure:
  - pairwise_similarities: List[
      - hypothesis_1: hypothesis_id
      - hypothesis_2: hypothesis_id
      - overall_similarity: float
      - similarity_breakdown:
        - conceptual: float
        - methodological: float
        - target_overlap: float
    ]
  - diversity_metrics:
    - coverage_score: float
    - redundancy_score: float
    - exploration_breadth: float
```

## Behavioral Contracts

### Similarity Assessment
- MUST consider research goal context in all similarity calculations
- MUST use consistent similarity metrics across all comparisons
- MUST normalize similarity scores to [0.0, 1.0] range
- MUST distinguish between different types of similarity
- SHOULD identify both obvious and subtle conceptual relationships

### Graph Maintenance
- MUST maintain graph consistency as hypotheses are added/removed
- MUST update similarities when hypotheses are evolved
- MUST preserve historical similarity data for analysis
- SHOULD optimize graph structure for efficient querying
- SHOULD detect and merge duplicate or near-duplicate hypotheses

### Clustering Quality
- MUST produce stable clusters across minor hypothesis variations
- MUST ensure clusters are interpretable and meaningful
- MUST identify clear cluster themes or commonalities
- SHOULD balance cluster size and cohesion
- SHOULD adapt clustering granularity to hypothesis pool size

## Interaction Protocols

### With Supervisor Agent
```
1. Receive proximity calculation task
2. Estimate computation time based on hypothesis count
3. Report progress for large hypothesis sets
4. Return complete proximity graph and clusters
5. Update task status to "completed"
```

### With Context Memory
```
1. Query hypothesis details for similarity calculation
2. Retrieve existing proximity graph if available
3. Lock graph structure during updates
4. Write updated graph atomically
5. Maintain graph version history
```

### With Ranking Agent
```
1. Provide similarity scores for hypothesis pairs
2. Suggest high-similarity matches for tournaments
3. Identify cluster representatives for diverse comparisons
4. Update graph based on tournament results
```

## Examples

### Example 1: Drug Repurposing Similarity
```
Input:
  - Research goal: "Repurpose FDA-approved drugs for AML treatment"
  - Hypothesis A: "Metformin targets AMPK pathway in AML cells"
  - Hypothesis B: "Sitagliptin modulates immune response in AML"
  - Hypothesis C: "Rapamycin inhibits mTOR in leukemic stem cells"

Process:
  - Calculate semantic similarity of mechanisms
  - Identify pathway relationships (AMPK-mTOR connection)
  - Assess target cell overlap
  - Consider therapeutic approach similarity

Output:
  - A-C similarity: 0.85 (related pathways, same target cells)
  - A-B similarity: 0.45 (different mechanisms, same disease)
  - B-C similarity: 0.40 (different approaches)
  - Cluster: {A, C} - "Metabolic pathway inhibitors"
```

### Example 2: Hypothesis Clustering
```
Input:
  - 50 hypotheses for liver fibrosis treatment
  - Clustering threshold: 0.7

Process:
  1. Calculate 1,225 pairwise similarities
  2. Build proximity graph with edges > 0.7
  3. Apply clustering algorithm
  4. Identify cluster themes
  5. Find outlier hypotheses

Output:
  - 8 clusters identified:
    - "Epigenetic modulators" (12 hypotheses)
    - "Anti-fibrotic cytokines" (8 hypotheses)
    - "Stellate cell inhibitors" (7 hypotheses)
    - etc.
  - 3 outlier hypotheses exploring novel mechanisms
  - Graph density: 0.24
```

### Example 3: Dynamic Graph Update
```
Scenario: New hypothesis added to existing pool

Input:
  - New hypothesis: "CRISPR-edited hepatocytes for fibrosis reversal"
  - Existing graph: 30 nodes, 85 edges

Process:
  1. Calculate similarity to all 30 existing hypotheses
  2. Add edges where similarity > threshold
  3. Check if new hypothesis joins existing cluster
  4. Update cluster assignments if needed
  5. Recalculate graph metrics

Output:
  - 4 new edges created
  - Hypothesis joins "Gene therapy" cluster
  - Cluster internal similarity: 0.78 → 0.81
  - Graph density: 0.189 → 0.194
```

## Performance Characteristics

### Computational Complexity
- Similarity calculation: O(n²) for n hypotheses
- Graph construction: O(n² + e) where e is edge count
- Clustering: O(n² log n) worst case
- Incremental update: O(n) for single hypothesis addition

### Quality Metrics
- Similarity consistency: >0.95 test-retest reliability
- Cluster stability: >0.85 adjusted Rand index
- Semantic accuracy: >0.80 agreement with expert groupings
- Graph sparsity: Typically 20-30% edge density

### Resource Usage
- Memory: O(n²) for full similarity matrix
- Storage: Compressed graph format ~10KB per 100 hypotheses
- Computation: Parallel processing for large hypothesis sets
- Caching: Similarity scores cached for 24 hours