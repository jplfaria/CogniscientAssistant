# Expert-in-the-Loop Interaction Specification

**Type**: Interaction Interface  
**Interactions**: Natural Language Interface, Supervisor Agent, Generation Agent, Reflection Agent, Ranking Agent, Meta-review Agent

## Prerequisites
- Read: Natural Language Interface Specification
- Read: Supervisor Agent Specification
- Understand: Research Goal Configuration concept from System Overview

## Purpose

The Expert-in-the-Loop Interaction system provides continuous collaboration mechanisms between domain experts and the AI Co-Scientist system. This specification defines how human expertise guides, validates, and enhances the automated hypothesis generation process while maintaining the system's collaborative paradigm.

## Core Behaviors

### 1. Research Goal Specification
The system accepts and processes expert-defined research objectives:
- Receives natural language descriptions of scientific goals
- Parses constraints, preferences, and desired hypothesis attributes
- Processes experimental limitations and feasibility requirements
- Updates research configurations based on expert refinements

### 2. Continuous Feedback Integration
The system incorporates expert guidance throughout operation:
- Accepts feedback at any stage of hypothesis generation
- Processes natural language comments and suggestions
- Updates evaluation criteria based on expert preferences
- Adjusts research directions according to expert insights

### 3. Hypothesis Contribution
The system integrates expert-generated hypotheses:
- Accepts direct hypothesis submissions from experts
- Enters expert hypotheses into the tournament system
- Treats expert contributions equally in ranking processes
- Enables combination of expert and AI-generated ideas

### 4. Review and Validation
The system facilitates expert review processes:
- Presents hypotheses for expert evaluation
- Collects structured feedback on quality, novelty, and feasibility
- Records expert assessments for system learning
- Prioritizes hypotheses based on expert validation

### 5. Research Direction Guidance
The system responds to expert steering:
- Accepts constraints on literature search scope
- Focuses on expert-specified research directions
- Prioritizes approaches indicated by experts
- Excludes areas marked as unproductive

## Inputs

### Research Goal Input
- **Format**: Natural language text (max 2000 characters)
- **Content**: Scientific objectives, constraints, preferences
- **Modality**: Text or multimodal with supporting documents
- **Timing**: Initial setup and refinement at any time

### Expert Feedback Input
- **Format**: Natural language comments
- **Types**: 
  - General guidance and suggestions
  - Specific hypothesis reviews
  - Research direction preferences
  - Quality assessments
- **Timing**: Continuous throughout system operation

### Expert Hypothesis Input
- **Format**: Structured hypothesis submission
  - Hypothesis text (required)
  - Supporting rationale (optional)
  - Experimental approach (optional)
- **Integration**: Enters standard evaluation pipeline

### Review Assessments
- **Novelty Score**: Integer 1-5 scale
- **Impact Score**: Integer 1-5 scale
- **Feasibility Assessment**: Text description
- **Recommendation**: Continue/Modify/Abandon

## Outputs

### Feedback Acknowledgment
- Confirmation of feedback receipt
- Summary of understood changes
- Updated research configuration display

### Integration Reports
- Status of expert hypothesis in tournament
- Ranking relative to AI-generated hypotheses
- Evolution/combination results if applicable

### Review Summaries
- Aggregated expert assessments
- Identified patterns in feedback
- Recommended next steps based on reviews

## Interaction Patterns

### Conversational Interaction
```
Expert: "Focus on repurposing existing FDA-approved drugs for treating liver fibrosis"
System: "Research goal updated. Constraining hypothesis generation to FDA-approved compounds with potential anti-fibrotic properties."

Expert: "This hypothesis about using metformin is interesting but needs to consider diabetic patient populations specifically"
System: "Feedback noted. Updating hypothesis to include diabetic patient stratification in experimental design."
```

### Hypothesis Submission
```
Expert: "Add hypothesis: Combination therapy using losartan and vitamin D may reduce hepatic stellate cell activation through complementary pathways"
System: "Expert hypothesis added to tournament. Current ranking position: 3 of 47. Similarity score with existing hypotheses: 0.23."
```

### Review Process
```
System: "Please review hypothesis H-127: [hypothesis text]"
Expert: "Novelty: 4, Impact: 3, Feasible but requires longitudinal study design"
System: "Review recorded. Hypothesis H-127 promoted to evolution queue based on high novelty score."
```

## Quality Requirements

### Responsiveness
- Acknowledge expert input within 2 seconds
- Process feedback updates within 10 seconds
- Complete hypothesis integration within 30 seconds

### Transparency
- Clearly indicate how feedback affects system behavior
- Show expert hypothesis performance in tournaments
- Provide rationale for system recommendations

### Flexibility
- Accept feedback in various natural language forms
- Handle partial or incremental guidance
- Support correction of misunderstood instructions

## Error Handling

### Invalid Input
- **Behavior**: Request clarification for ambiguous instructions
- **Response**: "Could you please clarify what you mean by [unclear portion]?"
- **Recovery**: Continue with previous configuration until clarified

### Conflicting Guidance
- **Behavior**: Present conflicts to expert for resolution
- **Response**: "Your recent guidance conflicts with earlier constraint [X]. Which should take precedence?"
- **Recovery**: Maintain both constraints until explicitly resolved

### System Limitations
- **Behavior**: Clearly communicate when requests exceed capabilities
- **Response**: "I cannot directly modify experimental protocols, but I can incorporate this constraint into hypothesis generation."
- **Recovery**: Suggest alternative approaches within system capabilities

## Safety Boundaries

### Expert Authority
- Expert can override any system-generated content
- Expert can halt or redirect processes at any time
- Expert maintains final decision on hypothesis pursuit

### Transparency Requirements
- System must clearly identify AI-generated vs expert-contributed content
- System must not misrepresent expert input
- System must maintain audit trail of expert interactions

### Ethical Considerations
- Respect expert's domain expertise
- Acknowledge limitations of AI understanding
- Defer to expert judgment on safety and ethics

## Integration Points

### With Natural Language Interface
- Shares language processing capabilities
- Uses same conversation context management
- Maintains consistent interaction patterns

### With Supervisor Agent
- Forwards processed expert goals
- Triggers re-planning based on feedback
- Influences task prioritization

### With Ranking Agent
- Submits expert hypotheses to tournaments
- Incorporates expert rankings as ground truth
- Adjusts Elo calculations based on expert validation

### With Meta-review Agent
- Provides expert feedback for synthesis
- Influences research overview generation
- Guides summary emphasis based on expert priorities

## Examples

### Drug Repurposing Scenario
```
Expert: "Find treatments for liver fibrosis using existing drugs. Prioritize those with known safety profiles in elderly patients."
System: "Configuring search for FDA-approved drugs with anti-fibrotic potential and established geriatric safety data."
[System generates hypotheses]
Expert: "The ACE inhibitor hypothesis is promising. Can you explore combination therapies?"
System: "Expanding hypothesis generation to include ACE inhibitor combinations. Focusing on synergistic anti-fibrotic mechanisms."
```

### Iterative Refinement
```
Expert: "The hypotheses are too focused on single targets. Real fibrosis involves multiple pathways."
System: "Adjusting generation parameters to emphasize multi-pathway approaches. Reranking existing hypotheses based on pathway diversity."
[System regenerates]
Expert: "Much better. Now ensure each hypothesis includes biomarkers for treatment monitoring."
System: "Adding biomarker identification requirement to all hypothesis evaluations."
```