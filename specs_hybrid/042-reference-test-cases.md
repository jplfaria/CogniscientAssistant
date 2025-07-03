# Reference Test Cases Specification

**Type**: Validation Test Suite  
**Components**: All System Components, External Validation Systems
**Source**: AI Co-Scientist Paper Validation Examples

## Prerequisites
- Read: Validation Criteria Specification
- Read: System Overview and Architecture Specification
- Read: All Agent Specifications (Generation through Meta-review)
- Understand: Scientific validation principles from the paper

## Purpose

This specification defines the reference test cases demonstrated in the AI Co-Scientist paper. These cases represent real-world scientific problems that were successfully addressed by the system, providing concrete examples of expected system behavior and output quality.

## Reference Test Case Categories

### Category 1: Drug Repurposing (Medium Complexity)

**Description**: Identifying existing FDA-approved drugs that can be repurposed for new therapeutic applications through combinatorial search of known compounds.

### Category 2: Novel Target Discovery (High Complexity)

**Description**: Discovering entirely new therapeutic targets that have not been previously considered for specific diseases.

### Category 3: Mechanism Explanation (Very High Complexity)

**Description**: Understanding and explaining complex biological mechanisms and evolutionary systems.

## Test Case 1: Drug Repurposing for Acute Myeloid Leukemia

### Test Configuration

**Research Goal Input**: 
```
"Identify FDA-approved drugs that could be repurposed for treating Acute Myeloid Leukemia (AML), focusing on compounds with demonstrated safety profiles that might show efficacy against AML cell lines"
```

**Expected System Behavior**:

1. **Generation Agent**:
   - Searches literature for AML biology and existing treatments
   - Identifies key pathways and targets in AML
   - Generates hypotheses for drug repurposing based on mechanism overlap
   - Considers 2,300+ FDA-approved drugs across multiple cancer types

2. **Reflection Agent**:
   - Reviews hypotheses for biological plausibility
   - Checks for existing evidence of efficacy
   - Identifies potential safety concerns
   - Suggests refinements based on mechanism of action

3. **Ranking Agent**:
   - Conducts tournaments between candidate drugs
   - Ranks based on:
     - Mechanism relevance to AML
     - Existing evidence strength
     - Safety profile
     - Feasibility of testing

4. **Evolution Agent**:
   - Combines successful drug candidates for combination therapy
   - Explores dosing variations
   - Considers patient subpopulations
   - Enhances hypotheses with biomarker strategies

### Expected Outputs

**Top Candidates Identified**:
1. **KIRA6**: IRE1α inhibitor
   - Expected IC50: 7-13 nM range in AML cell lines
   - Target cell lines: KG-1, MOLM-13, HL-60
   - Mechanism: ER stress pathway modulation

2. **Binimetinib**: MEK1/2 inhibitor
   - Expected IC50: ~7 nM in MOLM-13 cells
   - Rationale: MAPK pathway dysregulation in AML

3. **Additional Candidates**:
   - Pacritinib (JAK2/FLT3 inhibitor)
   - Cerivastatin (HMG-CoA reductase inhibitor)
   - Leflunomide (DHODH inhibitor)

### Validation Criteria

**Computational Validation**:
- DepMap correlation analysis shows negative scores
- Literature supports mechanism relevance
- Safety profile acceptable for oncology use

**Expert Review Format**:
- NIH Specific Aims format presentation
- Board-certified hematologist/oncologist review
- Minimum 6 expert reviewers

**Laboratory Validation** (External):
- Dose-response curves in AML cell lines
- IC50 determination
- Comparison with standard AML treatments

### Success Metrics
- Generate 50+ drug repurposing hypotheses
- Top 10 candidates show DepMap scores < -0.3
- At least 5 candidates demonstrate IC50 < 100 nM in validation
- Expert approval rate > 60% for top candidates

## Test Case 2: Novel Epigenetic Targets for Liver Fibrosis

### Test Configuration

**Research Goal Input**:
```
"Discover novel epigenetic therapeutic targets for treating liver fibrosis, focusing on reversible modifications that could halt or reverse fibroblast activation without affecting normal liver function"
```

**Expected System Behavior**:

1. **Generation Agent**:
   - Explores epigenetic mechanisms in fibrosis
   - Identifies understudied epigenetic modifiers
   - Generates hypotheses for novel targets
   - Links targets to druggable pathways

2. **Reflection Agent**:
   - Evaluates novelty against existing targets
   - Assesses druggability of proposed targets
   - Reviews potential off-target effects
   - Considers reversibility of modifications

3. **Meta-review Agent**:
   - Synthesizes patterns across epigenetic targets
   - Identifies common mechanisms
   - Suggests therapeutic strategies
   - Highlights safety considerations

### Expected Outputs

**Novel Epigenetic Targets**:
- 3 previously uncharacterized epigenetic modifiers
- Mechanisms involving:
  - Histone modifications
  - DNA methylation patterns
  - Chromatin remodeling complexes

**Drug Candidates**:
- 4 compounds targeting identified modifiers
- At least 1 FDA-approved drug for repurposing
- Clear mechanism of action for each

### Validation Criteria

**In Vitro Validation** (External):
- Human hepatic organoid model
- TGF-β induced fibrosis protocol
- Live cell imaging for fibroblast activity
- Viability assays for toxicity

**Success Indicators**:
- All 4 compounds show significant anti-fibrotic activity (p < 0.01)
- Reduction in myofibroblast markers
- No significant cellular toxicity
- Dose-dependent response curves

### Success Metrics
- Identify 3+ novel epigenetic targets
- Generate 20+ therapeutic hypotheses
- 4/4 tested compounds show efficacy
- Mechanism validated through molecular assays

## Test Case 3: Antimicrobial Resistance Mechanism Discovery

### Test Configuration

**Research Goal Input**:
```
"Explain why capsid-forming phage-inducible chromosomal islands (cf-PICIs) are found across diverse bacterial species and what evolutionary advantage they provide"
```

**Expected System Behavior**:

1. **Generation Agent**:
   - Reviews cf-PICI literature
   - Explores phage-bacteria interactions
   - Generates mechanism hypotheses
   - Considers evolutionary pressures

2. **Evolution Agent**:
   - Explores variations of transfer mechanisms
   - Considers different phage interactions
   - Proposes testable predictions
   - Suggests experimental approaches

3. **Meta-review Agent**:
   - Synthesizes understanding across hypotheses
   - Identifies key mechanism components
   - Highlights experimental validation needs

### Expected Output

**Primary Hypothesis**:
"cf-PICIs hijack diverse helper phages by interacting with multiple phage tail types, enabling horizontal transfer across broader host ranges than traditional PICIs"

**Supporting Evidence**:
- Structural analysis of cf-PICI proteins
- Phylogenetic distribution patterns
- Phage tail diversity correlation
- Host range expansion data

**Experimental Predictions**:
- cf-PICIs can transfer between distant bacterial species
- Transfer efficiency correlates with phage tail compatibility
- Blocking tail interactions prevents transfer
- cf-PICI spread patterns match phage host ranges

### Validation Criteria

**Hypothesis Quality**:
- Matches unpublished experimental findings
- Explains observed cf-PICI distribution
- Makes testable predictions
- Accounts for evolutionary pressures

**Time Efficiency**:
- System generates hypothesis in < 3 days
- Compare to 18 months experimental work
- Full mechanistic explanation provided

### Success Metrics
- Generate correct mechanism hypothesis
- Include all key interaction components
- Provide experimental validation strategy
- Time to discovery < 72 hours

## Cross-Case Validation Patterns

### Complexity Progression

Test cases demonstrate increasing complexity:
1. **Drug Repurposing**: Search known space for new applications
2. **Novel Targets**: Discover unknown therapeutic opportunities  
3. **Mechanism Discovery**: Explain complex biological systems

### Common Validation Elements

All cases include:
- Literature grounding verification
- Expert review components
- Experimental validation design
- Iterative improvement tracking

### System Capabilities Demonstrated

1. **Literature Integration**: All cases require extensive literature analysis
2. **Hypothesis Generation**: Novel, testable hypotheses in each domain
3. **Scientific Reasoning**: Mechanistic understanding and predictions
4. **Practical Outputs**: Actionable experimental protocols

## Test Execution Guidelines

### Setup Requirements

1. **Knowledge Base**:
   - PubMed access for literature search
   - Drug databases for repurposing  
   - Protein/pathway databases
   - Clinical trial registries

2. **Expert Reviewers**:
   - Domain specialists for each test case
   - Standardized review criteria
   - Blinded hypothesis evaluation

3. **Validation Partners**:
   - Laboratory facilities for in vitro tests
   - Computational resources for analyses
   - Statistical support for results

### Execution Steps

1. **Initialize System**: Load research goal
2. **Run Generation Cycle**: Allow full hypothesis generation
3. **Execute Tournaments**: Complete Elo ranking process  
4. **Perform Reviews**: All review types for top hypotheses
5. **Evolution Iterations**: Minimum 5 improvement cycles
6. **Generate Proposals**: NIH Specific Aims format
7. **Expert Validation**: External review process
8. **Compare Results**: Match against expected outputs

### Acceptance Criteria

**For Each Test Case**:
- System completes without critical errors
- Outputs match expected categories
- Quality metrics meet thresholds
- Expert validation confirms utility

**Overall System**:
- 3/3 test cases produce valid results
- Complexity handling demonstrated
- Time efficiency achieved
- Scientific value confirmed

## Limitations and Considerations

### Not Included in Reference Tests

1. **Wet Lab Execution**: Tests validate hypothesis quality, not experimental execution
2. **Long-term Outcomes**: Clinical translation beyond scope
3. **Resource Optimization**: Focus on quality over efficiency
4. **Multi-domain Integration**: Each test is domain-specific

### External Dependencies

1. **Expert Availability**: Requires qualified reviewers
2. **Laboratory Access**: For validation experiments
3. **Database Access**: Literature and drug databases
4. **Computational Resources**: For large-scale analysis

### Interpretation Guidelines

1. **Partial Success**: Some hypotheses may fail validation
2. **Novel Findings**: Unexpected discoveries are successes
3. **Iteration Value**: Improvement over cycles is key
4. **Expert Judgment**: Human validation remains critical