# Research Proposal Format Specification

**Type**: Process Specification  
**Interactions**: Generation Agent, Evolution Agent, Meta-review Agent, Expert Interface

## Prerequisites
- Read: Hypothesis Generation and Evolution Specification
- Read: Review Types and Processes Specification
- Read: Meta-review Agent Specification
- Understand: Research proposal standards (NIH, NSF, conference formats)

## Purpose
The Research Proposal Format specification defines how the AI Co-Scientist system structures and presents research hypotheses, experimental protocols, and comprehensive research plans in standardized formats suitable for scientific communication, grant applications, and peer review.

## Core Proposal Components

### 1. Hypothesis Proposal Structure
```
HypothesisProposal {
  hypothesis_id: string (unique identifier)
  summary: string (150-300 words, concise overview)
  full_description: string (detailed hypothesis with mechanisms)
  experimental_protocol: ExperimentalProtocol
  literature_grounding: LiteratureSupport
  novelty_statement: string (what makes this unique)
  testability_features: List[TestableOutcome]
  safety_considerations: SafetyAssessment
  elo_rating: float (current tournament score)
  review_history: List[ReviewSummary]
}
```

### 2. Experimental Protocol Format
```
ExperimentalProtocol {
  protocol_type: enum (in_vitro, in_vivo, computational, clinical)
  objectives: List[string] (specific experimental goals)
  methods: {
    materials: List[Material] (reagents, cell lines, models)
    procedures: List[Step] (numbered, detailed steps)
    controls: {
      positive: List[Control]
      negative: List[Control]
    }
    measurements: List[Metric] (quantifiable outcomes)
    timeline: string (estimated duration)
  }
  validation_approach: string (how results confirm/refute hypothesis)
  resource_requirements: ResourceEstimate
}
```

### 3. Literature Support Structure
```
LiteratureSupport {
  primary_citations: List[Citation] (directly supporting papers)
  background_citations: List[Citation] (contextual references)
  contradictory_evidence: List[Citation] (conflicting findings)
  knowledge_gaps: List[string] (what this addresses)
}
```

## Standard Output Formats

### 1. NIH Specific Aims Page Format
The system MUST format proposals according to NIH guidelines when requested:

```
NIHSpecificAimsPage {
  title: string (concise, descriptive project title)
  disease_description: string (background on condition)
  unmet_need: string (gap in current knowledge/treatment)
  overall_objective: string (overarching project goal)
  central_hypothesis: string (testable main hypothesis)
  rationale: string (supporting evidence and logic)
  specific_aims: List[SpecificAim] (2-4 aims)
  impact_statement: string (potential significance)
}

SpecificAim {
  aim_number: int (1-4)
  aim_title: string (brief descriptive title)
  hypothesis: string (aim-specific hypothesis)
  rationale: string (why this aim matters)
  approach: string (experimental strategy)
  expected_outcomes: List[string]
  potential_pitfalls: List[string]
  alternative_approaches: List[string]
}
```

### 2. Research Overview Format
For comprehensive multi-hypothesis presentations:

```
ResearchOverview {
  research_goal: string (scientist's objective)
  executive_summary: string (300-500 words)
  research_areas: List[ResearchArea]
  integrated_approach: string (how areas connect)
  recommended_contacts: List[ExpertContact]
  resource_summary: ResourceEstimate
  timeline_overview: string
}

ResearchArea {
  area_name: string
  justification: string (why important)
  key_hypotheses: List[string] (hypothesis IDs)
  suggested_experiments: List[ExperimentSummary]
  illustrative_examples: List[string]
  expected_impact: string
}
```

### 3. Conference Submission Format
```
ConferenceSubmission {
  title: string
  authors: List[string] (including "AI Co-Scientist System")
  abstract: string (150-250 words)
  keywords: List[string] (3-6 keywords)
  introduction: string
  hypothesis: string
  methods: string (condensed protocol)
  expected_results: string
  discussion: string
  references: List[Citation]
}
```

## Formatting Behaviors

### 1. Content Adaptation
The system MUST:
- Adjust detail level based on format requirements
- Preserve scientific accuracy across all formats
- Include all safety and ethical considerations
- Maintain consistency between different format versions

### 2. Language and Style
- Use field-appropriate terminology
- Follow journal/agency style guidelines
- Maintain active voice for clarity
- Avoid unnecessary jargon

### 3. Dynamic Formatting
Based on configuration parameters:
```
FormatConfiguration {
  output_format: enum (nih_aims, research_overview, conference, custom)
  detail_level: enum (summary, standard, comprehensive)
  include_preliminary_data: boolean
  citation_style: enum (apa, mla, nature, science)
  max_length: int (word/page limit)
  required_sections: List[string]
  custom_template: string (optional, user-provided)
}
```

## Integration with System Components

### With Generation Agent
- Receives: Raw hypothesis structures
- Formats: According to selected output format
- Returns: Formatted proposal ready for review

### With Evolution Agent
- Receives: Enhanced/combined hypotheses
- Updates: Proposal sections affected by evolution
- Maintains: Version history and change tracking

### With Meta-review Agent
- Receives: Synthesis directives
- Produces: Integrated research overviews
- Incorporates: Feedback from multiple reviews

### With Expert Interface
- Accepts: Format preferences and constraints
- Delivers: Proposals in requested formats
- Supports: Real-time format adjustments

## Quality Assurance

### 1. Format Validation
The system MUST ensure:
- All required sections are present
- Word/page limits are respected
- Citations are properly formatted
- No placeholder text remains

### 2. Content Coherence
- Hypothesis aligns with experimental approach
- Methods can feasibly test the hypothesis
- Timeline matches protocol complexity
- Resources match experimental needs

### 3. Completeness Checks
```
ProposalCompleteness {
  has_all_sections: boolean
  citations_valid: boolean
  protocols_detailed: boolean
  safety_addressed: boolean
  format_compliant: boolean
}
```

## Error Handling

### 1. Incomplete Information
- Flag missing required elements
- Provide clear error messages
- Suggest information sources

### 2. Format Conflicts
- Detect incompatible requirements
- Propose resolution options
- Maintain scientific integrity

### 3. Length Constraints
- Intelligent content prioritization
- Essential information preservation
- Clear indication of truncations

## Examples

### Example 1: NIH Aims Page for Drug Repurposing
```
Input: Hypothesis about existing drug for new indication
Output: 
- Disease: "Alzheimer's Disease"
- Unmet Need: "No disease-modifying treatments"
- Specific Aim 1: "Validate neuroprotective effects in vitro"
- Specific Aim 2: "Demonstrate efficacy in mouse models"
- Specific Aim 3: "Establish optimal dosing regimen"
```

### Example 2: Conference Abstract
```
Input: Novel biomarker discovery hypothesis
Output:
- Title: "AI-Guided Discovery of Circulating Biomarkers for Early Cancer Detection"
- Abstract: Structured with background, methods, results, conclusions
- Keywords: "machine learning, biomarkers, early detection, liquid biopsy"
```

## Extensibility

The system MUST support:
- New format templates via configuration
- Custom section definitions
- Field-specific requirements
- Multi-language output (future enhancement)
- Integration with document management systems

## Performance Requirements

- Format generation: < 5 seconds per proposal
- Batch formatting: Support for multiple hypotheses
- Real-time preview during editing
- Concurrent format generation for different outputs