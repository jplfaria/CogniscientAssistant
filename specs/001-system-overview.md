# AI Co-Scientist System Overview Specification

**Type**: System  
**Interactions**: Scientist (User), External Tools, Research Domains

## Purpose

The AI Co-Scientist is a collaborative AI system that augments human scientists in generating novel, testable hypotheses and research proposals. It accelerates scientific discovery by synthesizing insights across disciplines while maintaining continuous expert oversight.

## System Behaviors

### Primary Behavior
The system accepts natural language research goals from scientists and produces ranked lists of novel, testable hypotheses with accompanying experimental protocols and research proposals.

### Core Operational Loop
1. **Receive** research goal in natural language
2. **Generate** initial hypotheses through literature exploration
3. **Review** hypotheses through multiple evaluation processes
4. **Rank** hypotheses using tournament-based comparison
5. **Evolve** top-ranked hypotheses through refinement strategies
6. **Synthesize** feedback to improve future iterations
7. **Output** ranked hypotheses and research proposals

### Continuous Improvement
The system learns from each iteration through meta-review synthesis, improving hypothesis quality over time without requiring model fine-tuning.

## System Inputs

### Research Goal Specification
- **Format**: Natural language text
- **Content**: Scientific question, research objective, or hypothesis to explore
- **Constraints**: Clear scope, testable outcomes preferred
- **Examples**:
  - "Find novel drug combinations for treating acute myeloid leukemia"
  - "Identify new therapeutic targets for liver fibrosis"
  - "Investigate mechanisms of antimicrobial resistance gene transfer"

### Scientist Interventions
- Add custom hypotheses to the system
- Review and rate generated hypotheses
- Direct research into specific areas
- Provide domain expertise through chat interface
- Override safety or plausibility assessments

### External Knowledge Sources
- Scientific literature databases
- Domain-specific knowledge bases
- Specialized AI models (e.g., AlphaFold)
- Private publication repositories
- Experimental data when available

## System Outputs

### Ranked Hypothesis List
- **Primary Output**: Prioritized list of scientific hypotheses
- **Ranking Method**: Elo rating system based on tournament results
- **Content per Hypothesis**:
  - Summary (concise statement)
  - Full description with scientific rationale
  - Experimental protocol for validation
  - Literature grounding and citations
  - Novelty assessment
  - Safety evaluation
  - Elo rating score

### Research Proposals
- **Format**: NIH Specific Aims format or custom templates
- **Content**:
  - Background and significance
  - Specific aims
  - Research strategy
  - Experimental approach
  - Expected outcomes
  - Risk mitigation

### Research Overview
- **Meta-level Summary**: Patterns across all generated hypotheses
- **Research Directions**: Promising areas for further exploration
- **Contact Information**: Relevant researchers in the field

## System Boundaries

### What the System DOES
- Generate novel hypothesis variations
- Ground hypotheses in existing literature
- Conduct simulated scientific debates
- Evaluate testability and safety
- Prioritize research directions
- Provide experimental protocols

### What the System DOES NOT DO
- Execute laboratory experiments
- Replace human scientific judgment
- Make final research decisions
- Guarantee hypothesis validity
- Access proprietary data without permission
- Bypass ethical review processes

## Quality Criteria

All system outputs must satisfy:

### Alignment
- Hypotheses directly address the research goal
- Outputs remain within specified scope
- Proposals match researcher intent

### Plausibility
- Free from obvious scientific errors
- Grounded in established knowledge
- Mechanistically sound

### Novelty
- Not mere recombination of existing work
- Provides new insights or approaches
- Advances beyond current literature

### Testability
- Clear experimental protocols
- Measurable outcomes defined
- Feasible with current technology

### Safety
- No dangerous or unethical research
- Respects biosafety guidelines
- Considers societal implications

## Operational States

### Active Research
- Processing research goal
- Generating and evaluating hypotheses
- System fully engaged

### Awaiting Input
- Needs scientist intervention
- Requires additional information
- Paused for human review

### Terminal State
- Research goal achieved
- Maximum iterations reached
- Scientist terminates process

## Success Indicators

### Quantitative
- Elo ratings increase over iterations
- High-rated hypotheses align with expert assessment
- Efficient use of computational resources

### Qualitative
- Scientists find outputs valuable
- Hypotheses lead to experimental validation
- System augments rather than replaces expertise

## Example Usage Session

1. **Scientist Input**: "Find novel therapeutic targets for liver fibrosis focusing on epigenetic mechanisms"

2. **System Response**:
   - Generates 50+ initial hypotheses
   - Reviews each through multiple processes
   - Conducts tournaments for ranking
   - Evolves top candidates
   - Outputs top 10 ranked hypotheses

3. **Top Hypothesis Example**:
   - **Summary**: "Target KDM4A to reverse hepatic stellate cell activation"
   - **Elo Rating**: 1567
   - **Rationale**: Based on literature showing KDM4A upregulation in fibrotic tissue
   - **Protocol**: Small molecule inhibitor screening approach
   - **Novelty**: First proposed connection between KDM4A and stellate cell phenotype

4. **Scientist Action**: Reviews hypotheses, selects promising candidates for lab validation

## Integration Points

### Input Interfaces
- Natural language prompt interface
- Document upload capability
- API for programmatic access

### Output Interfaces
- Ranked hypothesis display
- Export to standard formats
- Integration with lab management systems

### External Tool Interfaces
- Literature search APIs
- Specialized model endpoints
- Database query systems

## Validation History

The system has demonstrated capability in three domains:
- **Drug Repurposing**: Discovered KIRA6 for AML (13 nM IC50)
- **Novel Targets**: Identified 4 epigenetic targets for liver fibrosis
- **Mechanism Discovery**: Rediscovered cf-PICI findings in 2 days vs 10 years

## System Philosophy

The AI Co-Scientist embodies collaborative intelligence where:
- AI handles breadth of knowledge synthesis
- Humans provide depth of domain expertise
- Iteration improves output quality
- Safety and ethics remain paramount
- Scientific rigor guides all operations