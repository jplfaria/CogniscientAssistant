# Output Formats Specification

**Type**: System Component  
**Interactions**: All Agents, Natural Language Interface, Context Memory

## Prerequisites
- Read: Meta-review Agent Specification (for research overview generation)
- Read: Natural Language Interface Specification (for user preferences)
- Understand: NIH grant format requirements and scientific documentation standards

## Purpose

The Output Formats component defines how the AI Co-Scientist system structures and presents research results to scientists. It ensures consistency, scientific rigor, and adaptability across different output types while maintaining compatibility with established research communication standards.

## Core Behaviors

### Format Generation
- Transforms agent outputs into structured documents
- Adapts content to specified templates (NIH, custom)
- Maintains scientific accuracy during formatting
- Preserves relationships between hypotheses and evidence
- Ensures reproducibility through detailed documentation

### Content Organization
- Groups related hypotheses thematically
- Prioritizes based on Elo rankings and review scores
- Structures experimental protocols hierarchically
- Links supporting literature appropriately
- Balances comprehensiveness with readability

### Quality Assurance
- Validates completeness of required sections
- Ensures consistency across document sections
- Verifies citation accuracy and formatting
- Checks experimental protocol feasibility
- Maintains appropriate scientific language

## Output Types

### Hypothesis Documentation
```
HypothesisOutput:
  summary: string (50-100 words)
  full_description: string (detailed mechanism/approach)
  experimental_protocol: 
    overview: string
    steps: List[ProtocolStep]
    controls: List[ControlDescription]
    expected_results: string
    timeline: string
  category: enum (mechanistic, therapeutic, diagnostic, preventive)
  grounding:
    primary_citations: List[Citation]
    supporting_evidence: List[Evidence]
    contradictory_findings: List[Citation] (if any)
  safety_assessment:
    risk_level: enum (minimal, low, moderate, high)
    mitigation_strategies: List[string]
  resource_requirements:
    equipment: List[string]
    reagents: List[string]
    estimated_cost: string
    personnel_expertise: List[string]
```

### Research Proposal Format
```
ResearchProposal:
  title: string
  abstract: string (250-300 words)
  specific_aims: 
    overview: string (disease context, unmet need, approach)
    aims: List[
      aim_number: integer
      title: string
      hypothesis: string
      rationale: string
      experimental_approach: string
      expected_outcomes: string
      alternative_strategies: string
    ]
  significance:
    scientific_premise: string
    innovation: string
    impact: string
  approach:
    preliminary_data: string (if available)
    research_design: string
    methods: List[MethodSection]
    timeline: GanttChart
    pitfalls_alternatives: List[RiskMitigation]
  budget_justification: string (optional)
  references: List[Citation]
```

### NIH Specific Aims Page
```
NIHSpecificAims:
  header:
    title: string (concise, descriptive)
    PI_name: string (if provided)
    institution: string (if provided)
  
  opening_paragraph:
    disease_description: string (2-3 sentences)
    unmet_need: string (2-3 sentences)
    proposed_solution: string (2-3 sentences)
    long_term_goal: string (1 sentence)
    
  overall_objective: string (1-2 sentences)
  central_hypothesis: string (1-2 sentences)
  rationale: string (2-3 sentences)
  
  specific_aims:
    - aim_1:
        statement: string (1 sentence)
        hypothesis: string (if applicable)
        approach_summary: string (2-3 sentences)
    - aim_2:
        statement: string (1 sentence)
        hypothesis: string (if applicable)
        approach_summary: string (2-3 sentences)
    - aim_3: (optional)
        statement: string (1 sentence)
        hypothesis: string (if applicable)
        approach_summary: string (2-3 sentences)
        
  expected_outcomes: string (2-3 sentences)
  positive_impact: string (1-2 sentences)
```

### Research Overview Document
```
ResearchOverview:
  executive_summary:
    research_goal: string
    key_findings: List[string] (3-5 bullet points)
    recommended_priorities: List[string]
    
  research_areas: List[
    area_name: string
    importance_score: float (0.0-1.0)
    justification: string
    top_hypotheses: List[
      rank: integer
      hypothesis_summary: string
      elo_rating: float
      key_advantages: List[string]
    ]
    proposed_experiments: List[
      experiment_name: string
      objectives: List[string]
      methodology: string
      expected_timeline: string
      success_criteria: List[string]
    ]
    relevant_experts: List[string]
    key_references: List[Citation]
  ]
  
  cross_cutting_insights: List[string]
  synergistic_opportunities: List[string]
  resource_optimization: string
  risk_assessment: RiskMatrix
  implementation_roadmap: List[Phase]
```

### Experimental Protocol Format
```
ExperimentalProtocol:
  protocol_name: string
  hypothesis_reference: string
  version: string
  last_updated: datetime
  
  objectives:
    primary: string
    secondary: List[string]
    
  materials:
    reagents: List[
      name: string
      catalog_number: string
      vendor: string
      amount_needed: string
    ]
    equipment: List[
      item: string
      specifications: string
      alternatives: List[string]
    ]
    
  methods:
    preparation: List[Step]
    experimental_procedure: List[
      step_number: integer
      description: string
      duration: string
      critical_points: List[string]
      safety_notes: List[string]
    ]
    data_collection: List[
      measurement: string
      instrument: string
      parameters: object
      frequency: string
    ]
    
  controls:
    positive: List[ControlDescription]
    negative: List[ControlDescription]
    technical: List[ControlDescription]
    
  data_analysis:
    statistical_tests: List[string]
    success_criteria: List[string]
    power_calculation: string
    
  expected_results:
    primary_outcome: string
    alternative_outcomes: List[string]
    troubleshooting: List[CommonIssue]
```

## Formatting Rules

### Scientific Writing Standards
- Use active voice for clarity
- Define abbreviations on first use
- Maintain consistent terminology
- Include units for all measurements
- Follow discipline-specific conventions

### Citation Formatting
```
Citation:
  authors: List[string] (LastName, FirstInitial format)
  title: string
  journal: string (abbreviated per PubMed)
  year: integer
  volume: integer
  pages: string (e.g., "123-145")
  doi: string
  pubmed_id: string (if available)
```

### Figure and Table References
- Number sequentially (Figure 1, Table 1)
- Include descriptive captions
- Reference in text before appearance
- Provide legends for all symbols
- Ensure standalone interpretability

## Output Customization

### User Preferences Integration
```
FormatPreferences:
  document_type: enum (proposal, aims_page, overview, custom)
  length_constraints:
    min_words: integer
    max_words: integer
    page_limit: integer
  style_guidelines:
    citation_style: enum (APA, Vancouver, Nature, Science)
    terminology_preferences: map[term, preferred_term]
    abbreviation_list: List[Abbreviation]
  emphasis_areas:
    sections_to_expand: List[string]
    sections_to_minimize: List[string]
  institution_requirements:
    template_url: string
    specific_sections: List[RequiredSection]
```

### Domain Adaptation
```
DomainFormatting:
  field: enum (oncology, neuroscience, immunology, etc.)
  specialized_sections:
    clinical_relevance: boolean
    translational_timeline: boolean
    regulatory_considerations: boolean
  terminology_database: string (reference URL)
  required_validations: List[ValidationCriterion]
```

## Quality Control

### Completeness Validation
- All required sections present
- Minimum content thresholds met
- Citations properly formatted
- Figures/tables referenced correctly
- No placeholder text remaining

### Consistency Checks
- Terminology uniform throughout
- Hypothesis numbering sequential
- Cross-references accurate
- Abbreviations used consistently
- Format specifications followed

### Scientific Accuracy
- Claims supported by citations
- Methods sufficiently detailed
- Statistics appropriately applied
- Limitations acknowledged
- Ethical considerations addressed

## Examples

### Example 1: NIH Specific Aims for AML Drug Repurposing
```
Title: Repurposing KIRA6 as a Novel Therapeutic for Acute Myeloid Leukemia

Acute myeloid leukemia (AML) remains a devastating malignancy with 
5-year survival rates below 30%. Current therapies often fail due to 
resistance and severe toxicity. We propose repurposing KIRA6, an IRE1α 
inhibitor, as it showed exceptional efficacy (IC50=13nM) in AML cell 
lines through our AI-driven discovery platform.

OVERALL OBJECTIVE: To validate KIRA6 as a therapeutic agent for AML 
and elucidate its mechanism of action.

CENTRAL HYPOTHESIS: KIRA6 induces AML cell death by disrupting ER 
stress responses critical for leukemic cell survival.

Aim 1: Determine KIRA6's efficacy and mechanism in AML models.
We will test KIRA6 in patient-derived AML samples and xenograft models, 
using transcriptomics and proteomics to map its effects on ER stress 
pathways.

Aim 2: Identify biomarkers for KIRA6 sensitivity.
We will correlate KIRA6 response with genetic and molecular features 
across 50 AML samples to develop a precision medicine approach.

Aim 3: Optimize KIRA6 combination therapies.
We will screen KIRA6 with standard AML drugs to identify synergistic 
combinations that enhance efficacy while minimizing toxicity.

EXPECTED OUTCOMES: These studies will establish KIRA6's therapeutic 
potential and provide the foundation for clinical translation, 
potentially offering new hope for AML patients.
```

### Example 2: Research Overview Executive Summary
```
Research Goal: Identify novel epigenetic targets for liver fibrosis

KEY FINDINGS:
• Discovered 17 high-confidence epigenetic targets with anti-fibrotic potential
• Top candidate: BRD4 inhibition (Elo: 1456) reverses stellate cell activation
• Identified 4 synergistic target combinations for enhanced efficacy
• Validated approach using patient-derived hepatic organoids
• Novel mechanism: HDAC6-TGFβ feedback loop disruption

RECOMMENDED PRIORITIES:
1. Advance BRD4 inhibitor JQ1 analog testing in 3D liver models
2. Investigate HDAC6/BET dual inhibition strategy  
3. Develop stellate cell-specific delivery methods
4. Initiate combination screening with standard of care
5. Establish biomarker panel for treatment response
```

### Example 3: Experimental Protocol Summary
```
Protocol: BRD4 Inhibition in Hepatic Stellate Cells
Reference: Hypothesis LF-2024-0089
Version: 1.2

OBJECTIVES:
Primary: Assess JQ1 impact on stellate cell activation markers
Secondary: Determine dose-response and reversibility

KEY METHODS:
1. Isolate primary stellate cells from fibrotic liver tissue
2. Culture in activation medium ± JQ1 (0.1-10 μM)
3. Measure: αSMA, Col1a1, TIMP1 expression (qPCR, Western)
4. Assess: Cell viability, proliferation, migration
5. Timeline: 7-day treatment with daily medium changes

CRITICAL CONTROLS:
- Vehicle (DMSO) negative control
- TGFβ activation positive control  
- Hepatocyte co-culture for specificity
- Time-matched untreated samples

SUCCESS CRITERIA:
- >50% reduction in activation markers at non-toxic doses
- Dose-dependent response with clear IC50
- Reversibility upon treatment withdrawal
- Minimal hepatocyte toxicity (<10%)
```

## Integration Requirements

### With Generation Agent
- Receives raw hypothesis content
- Applies appropriate formatting templates
- Preserves scientific accuracy
- Maintains citation linkages

### With Meta-review Agent  
- Formats research overviews
- Organizes synthesis results
- Structures feedback reports
- Creates summary documents

### With Natural Language Interface
- Accepts format preferences
- Provides preview capabilities
- Enables format adjustments
- Supports export options

### With Context Memory
- Stores format preferences
- Maintains version history
- Tracks document evolution
- Enables format reuse

## Performance Considerations

### Processing Efficiency
- Template application: <1 second per hypothesis
- Document generation: <30 seconds for full proposal
- Format validation: Real-time during generation
- Export preparation: <5 seconds per format

### Scalability
- Handles 100+ hypotheses per document
- Supports parallel format generation
- Manages multiple output types simultaneously
- Maintains performance with complex templates

This specification ensures the AI Co-Scientist system produces professional, scientifically rigorous outputs that meet the diverse needs of researchers while maintaining consistency and quality across all generated documents.