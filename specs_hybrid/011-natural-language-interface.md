# Natural Language Interface Specification

**Type**: Interface  
**Interactions**: Supervisor Agent, Meta-review Agent, Context Memory

## Prerequisites
- Read: System Overview and Architecture Specification
- Read: Supervisor Agent Specification
- Understand: Research Goal Configuration concepts

## Purpose

The Natural Language Interface provides the primary communication channel between scientists and the AI Co-Scientist system. It enables researchers to specify goals, provide feedback, and guide the research process using familiar scientific language without requiring technical AI expertise.

## Behavior

The Natural Language Interface exhibits the following behaviors:

### 1. Research Goal Acceptance
- Receives research objectives expressed in natural scientific language
- Accepts inputs ranging from simple queries to comprehensive research documents
- Processes multimodal content including text, PDFs, and data files
- Validates input for safety and feasibility constraints

### 2. Interactive Communication
- Maintains conversational context throughout research sessions
- Interprets scientist feedback and refinement requests
- Translates natural language directives into system actions
- Provides clarification prompts when input is ambiguous

### 3. Output Formatting
- Presents hypotheses and research proposals in scientific formats
- Adapts communication style to match scientist's domain expertise
- Structures outputs for specific use cases (grants, papers, presentations)
- Includes appropriate citations and supporting evidence

### 4. Continuous Collaboration
- Enables real-time steering of research direction
- Incorporates scientist feedback into ongoing processes
- Supports iterative refinement through dialogue
- Maintains conversation history for context

## Inputs

### Research Goal Specification
```
ResearchGoalInput {
  goal_text: string              # Natural language research objective
  constraints: List[string]      # Optional constraints in natural language
  preferences: List[string]      # Optional preferences for hypothesis attributes
  attachments: List[Document]    # PDFs, datasets, prior research
  max_tokens: int               # Maximum input length (default: 50000)
}
```

### Interactive Commands
```
InteractiveInput {
  command_type: enum {
    "add_idea"        # Contribute a hypothesis
    "review_idea"     # Provide review of specific hypothesis
    "discuss"         # General research discussion
    "refine_goal"     # Modify research objectives
    "request_detail"  # Ask for elaboration on specific aspect
  }
  content: string     # Natural language command content
  context_id: string  # Reference to specific hypothesis or topic
}
```

### Feedback Input
```
FeedbackInput {
  feedback_text: string         # Natural language feedback
  target_hypothesis: string     # Optional specific hypothesis ID
  feedback_type: enum {
    "general"                   # Overall research direction
    "hypothesis_specific"       # About particular hypothesis
    "methodological"           # About experimental approach
    "literature"               # About citations/references
  }
}
```

## Outputs

### Formatted Research Output
```
ResearchOutput {
  format_type: enum {
    "hypothesis_list"          # Ranked list of hypotheses
    "research_proposal"        # Full research proposal
    "nih_aims_page"           # NIH Specific Aims format
    "research_overview"        # Synthesized summary
    "experimental_protocol"    # Detailed methodology
  }
  content: string              # Natural language content
  supporting_data: Dict        # Citations, figures, data
}
```

### Interactive Response
```
InteractiveResponse {
  response_text: string        # Natural language response
  suggested_actions: List[string]  # Recommended next steps
  clarification_needed: bool   # Whether more input required
  session_state: string        # Current research phase
}
```

### Progress Communication
```
ProgressUpdate {
  message: string              # Natural language status update
  phase: string               # Current processing phase
  hypotheses_generated: int    # Number of hypotheses so far
  estimated_time: string      # Time estimate in natural language
}
```

## Interface Behaviors

### Language Processing
- **Input Normalization**: Standardizes varied natural language inputs while preserving scientific meaning
- **Context Preservation**: Maintains conversation context across interactions
- **Domain Adaptation**: Recognizes and adapts to scientific terminology and conventions
- **Ambiguity Resolution**: Requests clarification for unclear instructions

### Safety and Validation
- **Goal Screening**: Evaluates research goals for safety and ethical concerns
- **Constraint Validation**: Ensures specified constraints are feasible
- **Harmful Request Detection**: Identifies and rejects potentially dangerous research directions
- **Scope Verification**: Confirms research goals align with system capabilities

### Communication Patterns
- **Progressive Disclosure**: Provides information at appropriate detail levels
- **Scientific Formatting**: Uses standard scientific communication conventions
- **Citation Integration**: Embeds literature references naturally in responses
- **Visual Representation**: Describes complex concepts with structured formats

## Interaction Examples

### Example 1: Simple Research Goal
```
Scientist: "Find novel therapeutic targets for Alzheimer's disease focusing on 
          neuroinflammation pathways"

System: "I'll explore therapeutic targets for Alzheimer's disease with a focus 
        on neuroinflammation. I'll generate hypotheses considering:
        - Current understanding of neuroinflammatory mechanisms
        - Druggable targets in these pathways
        - Novel approaches not yet in clinical trials
        
        Starting hypothesis generation now..."
```

### Example 2: Iterative Refinement
```
Scientist: "The hypothesis about microglial activation is interesting, but can 
          you explore more about the role of astrocytes?"

System: "I'll refine the research to emphasize astrocyte-mediated mechanisms. 
        I'll generate new hypotheses that:
        - Focus on astrocyte-specific pathways
        - Consider astrocyte-microglia interactions
        - Explore astrocyte dysfunction in neuroinflammation
        
        Updating research direction..."
```

### Example 3: Adding Constraints
```
Scientist: "Please focus only on targets that have existing small molecule 
          modulators, even if not approved for Alzheimer's"

System: "I'll constrain the search to targets with known small molecule 
        modulators. This includes:
        - FDA-approved drugs for other indications
        - Compounds in clinical trials
        - Well-characterized research tools
        
        Applying this constraint to hypothesis generation..."
```

## Error Handling

### Input Errors
- **Ambiguous Goal**: Request clarification with specific questions
- **Conflicting Constraints**: Identify conflicts and ask for resolution
- **Excessive Length**: Summarize input and confirm key points
- **Missing Context**: Prompt for additional information

### Processing Errors
- **Unsafe Request**: Explain why request cannot be processed
- **Out of Scope**: Suggest alternative approaches within capabilities
- **Technical Limitations**: Communicate constraints clearly
- **Resource Limits**: Provide options for simplified approaches

## Quality Requirements

### Responsiveness
- Initial response within 2 seconds of input
- Progress updates every 10-30 seconds during processing
- Complete responses formatted appropriately for scientific use

### Accuracy
- Preserve scientific meaning without distortion
- Maintain precision in technical terminology
- Accurately reflect system capabilities and limitations

### Accessibility
- No technical jargon in system communications
- Clear explanations of system actions
- Intuitive command recognition without training

## Integration Patterns

### With Supervisor Agent
- Translates natural language goals into ResearchPlanConfig
- Receives system state updates for progress communication
- Forwards interactive commands for execution

### With Meta-review Agent  
- Provides scientist feedback for incorporation
- Receives synthesized overviews for formatting
- Enables discussion of research patterns

### With Context Memory
- Stores conversation history
- Retrieves previous interactions for context
- Maintains session continuity across interactions