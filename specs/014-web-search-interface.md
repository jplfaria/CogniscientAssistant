# Web Search Interface Specification

**Type**: Tool Interface  
**Interactions**: Generation Agent, Reflection Agent, Meta-review Agent, Supervisor Agent

## Prerequisites
- Read: 007-generation-agent.md (for understanding literature exploration)
- Read: 008-reflection-agent.md (for full review with web search)
- Understand: Scientific literature search requirements from source materials

## Overview

The Web Search Interface provides agents with access to scientific literature and current research knowledge. This tool serves as the primary mechanism for grounding hypotheses in existing scientific evidence, verifying novelty, and gathering experimental observations. It enables the AI Co-Scientist to operate with up-to-date scientific knowledge by accessing open-access literature and research databases.

## Behavior

The Web Search Interface enables scientific literature discovery through natural language queries. It provides structured access to research papers, abstracts, and experimental results while respecting access restrictions and maintaining result quality.

### Core Responsibilities
1. Convert natural language queries into effective literature searches
2. Retrieve relevant scientific papers and research articles
3. Provide structured metadata for discovered literature
4. Support iterative refinement of search queries
5. Maintain focus on open-access and publicly available content

### Search Types Supported
- **Literature exploration**: Broad searches on research topics
- **Novelty verification**: Checking if specific hypotheses already exist
- **Evidence gathering**: Finding experimental results and observations
- **Background research**: Understanding broader research context
- **Citation verification**: Confirming references and scientific claims

## Inputs

### Search Query Structure
```
LiteratureSearchQuery:
  query: string                    # Natural language search terms
  search_type: SearchType          # Type of search being performed
  filters: Optional[SearchFilters] # Constraints on results
  max_results: int = 10           # Maximum papers to return
  
SearchType:
  - EXPLORATION      # Broad topic exploration
  - NOVELTY_CHECK   # Verify if idea exists
  - EVIDENCE        # Find supporting/refuting evidence
  - BACKGROUND      # General context gathering
  - CITATION        # Verify specific claims

SearchFilters:
  date_range: Optional[DateRange]      # Publication date constraints
  domains: Optional[List[string]]      # Specific databases or sources
  open_access_only: bool = true       # Restrict to accessible papers
  peer_reviewed: bool = true          # Quality filter
```

## Outputs

### Search Results Structure
```
LiteratureSearchResults:
  query_id: string                         # Unique identifier for this search
  articles: List[ScientificArticle]        # Found papers
  total_found: int                         # Total matches (may exceed returned)
  search_metadata: SearchMetadata          # Information about the search

ScientificArticle:
  title: string                            # Paper title
  authors: List[string]                    # Author names
  abstract: string                         # Paper abstract
  doi: Optional[string]                    # Digital Object Identifier
  publication_date: date                   # When published
  journal: Optional[string]                # Publication venue
  relevance_score: float                   # 0.0 to 1.0
  full_text_available: bool               # Can access full paper
  key_findings: Optional[List[string]]     # Extracted important results
  
SearchMetadata:
  execution_time_ms: int                   # Search duration
  sources_searched: List[string]           # Which databases queried
  query_expansion: Optional[string]        # How query was modified
  filters_applied: List[string]            # Active constraints
```

## Behavior Contracts

### Quality Guarantees
1. Interface MUST return scientifically relevant literature
2. Results MUST include proper citations and metadata
3. Relevance scores MUST reflect query-article alignment
4. Interface MUST respect access restrictions and licenses
5. Searches SHOULD prioritize peer-reviewed sources

### Performance Expectations
1. Simple queries SHOULD return within 5 seconds
2. Complex searches MAY take up to 30 seconds
3. Results SHOULD be sorted by relevance score
4. Interface SHOULD cache recent searches

### Safety Boundaries
1. Interface MUST NOT access paywalled content without authorization
2. Queries MUST be filtered for scientific relevance
3. Results MUST exclude predatory journals when identifiable
4. Interface MUST rate-limit to prevent service abuse

## Interaction Protocols

### With Generation Agent
- **RECEIVE**: Exploratory queries about research topics
- **SEND**: Relevant papers for hypothesis foundation
- **HANDLE**: Iterative query refinement based on findings
- **SUPPORT**: Gap identification through result analysis

### With Reflection Agent
- **RECEIVE**: Targeted queries for hypothesis validation
- **SEND**: Evidence for or against specific claims
- **HANDLE**: Deep searches for experimental results
- **SUPPORT**: Novelty verification through exhaustive search

### With Meta-review Agent
- **RECEIVE**: Broad queries about research trends
- **SEND**: Representative papers across topic areas
- **HANDLE**: Pattern identification requests
- **SUPPORT**: Research landscape overview

## Error Handling

### Service Failures
1. **IF** search service unavailable:
   - Return cached results if query matches
   - Queue request for retry
   - Notify requesting agent of degraded mode

2. **IF** rate limit exceeded:
   - Implement exponential backoff
   - Prioritize novelty checks over exploration
   - Aggregate similar queries

### Result Quality Issues
1. **IF** no results found:
   - Suggest alternative query formulations
   - Recommend broader search terms
   - Check for spelling or terminology issues

2. **IF** too many results:
   - Apply additional relevance filtering
   - Suggest query refinement strategies
   - Return most relevant subset

## Examples

### Example 1: Drug Repurposing Literature Search
**Input**:
```
query: "KIRA6 IRE1α inhibitor ER stress acute myeloid leukemia"
search_type: EXPLORATION
filters: {
  date_range: "2020-2024",
  open_access_only: true
}
```

**Output**:
```
articles: [
  {
    title: "Targeting ER stress in AML with selective IRE1α inhibitors",
    relevance_score: 0.95,
    key_findings: ["KIRA6 shows potent activity in AML cell lines", 
                   "IC50 values in nanomolar range"]
  },
  ...
]
```

### Example 2: Novelty Verification
**Input**:
```
query: "epigenetic HDAC inhibition liver stellate cell activation fibrosis"
search_type: NOVELTY_CHECK
max_results: 20
```

**Output**:
```
articles: [],  # No direct matches
search_metadata: {
  query_expansion: "Added synonyms: hepatic fibrogenesis, HSC activation",
  filters_applied: ["peer_reviewed", "open_access"]
}
```

## Natural Language Examples

### Scientist Request
"Find recent papers on the role of inflammation in Alzheimer's disease progression"

### Interface Processing
1. Identifies key concepts: inflammation, Alzheimer's, progression
2. Expands query with synonyms: neuroinflammation, AD, disease advancement
3. Applies recency filter: last 5 years
4. Searches multiple databases for comprehensive coverage

### Agent Usage
Generation Agent receives search results and synthesizes findings:
"Based on 15 recent papers, microglial activation appears central to AD progression..."

## Integration Considerations

### Asynchronous Operation
- Searches execute independently of agent processing
- Results cached for rapid re-access
- Multiple searches can run in parallel

### Result Processing
- Agents must handle partial results during long searches
- Relevance scores guide hypothesis development
- Missing full-text access influences search strategy

### Feedback Loop
- Failed searches inform query reformulation
- Result patterns guide search refinement
- Usage analytics improve search effectiveness