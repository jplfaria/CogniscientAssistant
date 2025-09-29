# External Tools Interface Specification

**Type**: Tool Interface  
**Interactions**: Generation Agent, Reflection Agent, Evolution Agent, All Agents  
**Core Function**: Provide access to specialized computational models and databases

## Prerequisites
- Read: Web Search Interface Specification (014)
- Read: Generation Agent Specification (007)
- Read: Reflection Agent Specification (008)
- Understand: API-based integration patterns

## Overview

The External Tools Interface provides agents with access to specialized computational resources beyond web search. This includes domain-specific AI models (e.g., AlphaFold for protein structure prediction), scientific databases (e.g., FDA-approved drugs, cell receptors), and custom data repositories provided by scientists.

## Core Behavior

The External Tools Interface enables agents to:
- Query specialized AI models for domain-specific predictions
- Access constrained databases for hypothesis validation
- Retrieve information from private repositories
- Obtain computational results that enhance hypothesis evaluation

### Tool Categories

```
ToolCategory:
  - SPECIALIZED_MODEL    # AlphaFold, ESMFold, other AI models
  - SCIENTIFIC_DATABASE  # FDA drugs, cell receptors, chemical compounds
  - PRIVATE_REPOSITORY   # Custom scientist-provided collections
  - COMPUTATIONAL_SERVICE # Other scientific computation services
```

## Inputs

### Tool Request Structure
```
ExternalToolRequest:
  tool_type: ToolCategory
  tool_name: string  # e.g., "AlphaFold", "FDA_Drug_Database"
  query: QueryObject
  constraints: Optional[ConstraintSet]
  timeout_seconds: Optional[int]  # Default: 300
```

### Query Types
```
QueryObject (varies by tool):
  - ProteinQuery:
      sequence: string
      structure_type: Optional[string]
  - DatabaseQuery:
      search_criteria: Dict[string, Any]
      max_results: Optional[int]
  - RepositoryQuery:
      search_terms: List[string]
      filters: Optional[FilterSet]
```

## Outputs

### Tool Response Structure
```
ExternalToolResponse:
  tool_name: string
  status: ResponseStatus
  results: ResultObject
  metadata: ResponseMetadata
  cached: boolean
```

### Response Status
```
ResponseStatus:
  - SUCCESS
  - PARTIAL_SUCCESS
  - FAILURE
  - TIMEOUT
  - ACCESS_DENIED
```

### Result Types
```
ResultObject (varies by tool):
  - ProteinStructureResult:
      confidence_scores: Dict[string, float]
      structure_data: string  # PDB format or similar
      warnings: Optional[List[string]]
  - DatabaseResult:
      matches: List[DatabaseEntry]
      total_count: int
      query_constraints_met: boolean
  - RepositoryResult:
      documents: List[Document]
      relevance_scores: List[float]
```

## Behavior Contracts

### General Tool Behavior
- Tools MUST return results within specified timeout
- Tools MUST respect access permissions and rate limits
- Tools SHOULD cache results for identical queries
- Tools MAY return partial results on timeout

### Specialized Model Behavior
- Models MUST provide confidence scores with predictions
- Models MUST indicate when input is outside training domain
- Models SHOULD return interpretable error messages
- Models MAY provide alternative predictions

### Database Behavior
- Databases MUST honor all specified constraints
- Databases MUST indicate if query space is fully searched
- Databases SHOULD provide result counts before detailed retrieval
- Databases MAY suggest query refinements

### Repository Behavior
- Repositories MUST respect access controls
- Repositories MUST maintain data isolation between scientists
- Repositories SHOULD support relevance ranking
- Repositories MAY provide citation information

## Interaction Protocols

### Generation Agent Protocol
The Generation Agent:
- RECEIVES: Available tool catalog with capabilities
- SENDS: Tool requests during hypothesis formulation
- HANDLES: Constraint validation from databases
- SUPPORTS: Iterative refinement based on tool feedback

### Reflection Agent Protocol
The Reflection Agent:
- RECEIVES: Tool results for verification
- SENDS: Validation queries to specialized models
- HANDLES: Confidence scores and predictions
- SUPPORTS: Cross-referencing multiple tools

### Evolution Agent Protocol
The Evolution Agent:
- RECEIVES: Tool constraints for hypothesis modification
- SENDS: Queries to validate evolved hypotheses
- HANDLES: Domain-specific feedback
- SUPPORTS: Tool-guided hypothesis refinement

### General Agent Protocol
All agents:
- MUST handle tool unavailability gracefully
- SHOULD use tool results to enhance reasoning
- MAY request multiple tools in parallel
- MUST respect tool-specific rate limits

## Error Handling

### Service Failures
- **Unavailable Tool**: Use cached results if available, otherwise proceed without tool input
- **Timeout**: Return partial results if any, mark as incomplete
- **Access Denied**: Log attempt, inform requesting agent, continue with available tools

### Quality Issues
- **Low Confidence**: Include results but flag uncertainty
- **Invalid Input**: Return error with correction suggestions
- **Constraint Violations**: Explain which constraints failed

### Fallback Strategies
- Use alternative tools when primary tool fails
- Combine multiple lower-quality sources
- Rely on web search for general information
- Proceed with explicit uncertainty acknowledgment

## Safety Boundaries

- NEVER expose private repository data across scientists
- ALWAYS validate tool inputs for safety
- NEVER exceed rate limits or abuse external services
- ALWAYS respect intellectual property rights

## Examples

### Example 1: AlphaFold Query
```
Input:
  tool_type: SPECIALIZED_MODEL
  tool_name: "AlphaFold"
  query: {
    sequence: "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEK"
  }

Output:
  status: SUCCESS
  results: {
    confidence_scores: {"overall": 0.87, "per_residue": [...]},
    structure_data: "ATOM    1  N   MET A   1 ...",
    warnings: ["Low confidence for residues 45-52"]
  }
```

### Example 2: FDA Drug Database Query
```
Input:
  tool_type: SCIENTIFIC_DATABASE
  tool_name: "FDA_Drug_Database"
  query: {
    search_criteria: {
      "indication": "type 2 diabetes",
      "approval_year": {"after": 2010}
    },
    max_results: 20
  }

Output:
  status: SUCCESS
  results: {
    matches: [
      {"name": "Canagliflozin", "class": "SGLT2 inhibitor", ...},
      {"name": "Dulaglutide", "class": "GLP-1 agonist", ...}
    ],
    total_count: 15,
    query_constraints_met: true
  }
```

### Example 3: Private Repository Search
```
Input:
  tool_type: PRIVATE_REPOSITORY
  tool_name: "Lab_Publications"
  query: {
    search_terms: ["CRISPR", "base editing", "liver"],
    filters: {"publication_date": {"after": "2020-01-01"}}
  }

Output:
  status: SUCCESS
  results: {
    documents: [
      {"title": "Optimized base editing in hepatocytes", "relevance": 0.95},
      {"title": "CRISPR screens in liver organoids", "relevance": 0.82}
    ],
    relevance_scores: [0.95, 0.82]
  }
```

### Example 4: Tool Unavailability
```
Input:
  tool_type: SPECIALIZED_MODEL
  tool_name: "AlphaFold"
  query: {sequence: "MKTAYIAK..."}

Output:
  status: FAILURE
  results: null
  metadata: {
    error_type: "SERVICE_UNAVAILABLE",
    message: "AlphaFold API is currently down",
    retry_after: 3600
  }
```

## Tool Integration Considerations

### Extensibility
- New tools can be added without modifying agent behavior
- Tool catalog is discoverable and self-documenting
- Agents adapt to available tool capabilities

### Performance
- Asynchronous execution for long-running computations
- Result caching with appropriate TTL
- Parallel tool queries when beneficial

### Monitoring
- Track tool usage patterns
- Monitor success rates and latencies
- Identify bottlenecks and optimization opportunities

## Natural Language Understanding

Agents translate research needs into appropriate tool queries:
- "Check if this protein structure is known" → AlphaFold query
- "Find FDA-approved kinase inhibitors" → FDA database search
- "Search our lab's recent CRISPR papers" → Private repository query

The interface handles the complexity of tool selection and query formulation, allowing agents to focus on scientific reasoning.