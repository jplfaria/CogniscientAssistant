# Natural Language Interface Specification

**Type**: Interface  
**Interactions**: Scientist (User), Supervisor Agent, Context Memory

## Prerequisites
- Read: System Overview Specification
- Read: Core Principles Specification
- Understand: Expert-in-the-loop design concepts

## Purpose

The Natural Language Interface enables scientists to interact with the AI Co-Scientist system using natural language, providing research goals, feedback, and guidance throughout the scientific discovery process.

## Core Behaviors

### Research Goal Specification

The interface accepts research goals from scientists in natural language with:

- **Free-form Input**: Scientists express goals without rigid formatting requirements
- **Multi-modal Support**: Accepts text descriptions alongside document attachments
- **Contextual Understanding**: Processes goals with preferences, constraints, and attributes
- **Iterative Refinement**: Allows goal modification during research process
- **Scope Recognition**: Identifies research boundaries and focus areas

### Interactive Collaboration

The interface enables ongoing scientist engagement through:

- **Hypothesis Review**: Scientists evaluate and rate system-generated hypotheses
- **Custom Contributions**: Scientists add their own hypotheses to the system
- **Research Guidance**: Scientists direct exploration into specific areas
- **Feedback Integration**: Natural language feedback improves system behavior
- **Progress Monitoring**: Scientists track research advancement in real-time

### Communication Modes

The interface supports multiple interaction patterns:

- **Initial Goal Setting**: One-time research objective specification
- **Conversational Refinement**: Back-and-forth dialogue for clarification
- **Intervention Points**: Strategic moments for scientist input
- **Continuous Monitoring**: Passive observation with optional engagement
- **Batch Operations**: Multiple hypotheses or reviews submitted together

## Inputs

### Research Goal Format
```
ResearchGoal:
  description: string (natural language research objective)
  complexity: enum (simple_statement, detailed_requirements, extensive_documentation)
  attachments: list[document] (optional PDFs, prior publications)
  constraints:
    experimental_methods: list[string] (allowed/forbidden techniques)
    resource_limits: ResourceConstraints
    ethical_bounds: list[string]
  preferences:
    hypothesis_types: list[string] (mechanistic, therapeutic, diagnostic)
    output_format: string (NIH_aims, custom_template)
    review_criteria: list[string] (novelty, feasibility, impact)
```

### Scientist Feedback Types
```
FeedbackInput:
  type: enum (hypothesis_review, goal_refinement, direction_guidance, chat_message)
  content:
    hypothesis_review:
      hypothesis_id: string
      rating: integer (1-5)
      comments: string
      safety_override: boolean
    goal_refinement:
      modification_type: enum (expand, narrow, redirect)
      new_constraints: list[string]
      additional_context: string
    direction_guidance:
      focus_area: string
      priority_adjustment: map[topic, weight]
      excluded_paths: list[string]
    chat_message:
      message: string
      context_reference: string (hypothesis_id or research_area)
```

### Custom Hypothesis Submission
```
CustomHypothesis:
  summary: string (concise statement)
  full_description: string (detailed explanation)
  rationale: string (scientific justification)
  experimental_approach: string (validation method)
  priority: enum (high, medium, low)
  request_evolution: boolean (allow system refinement)
```

## Outputs

### System Responses
```
InterfaceResponse:
  type: enum (acknowledgment, clarification_request, status_update, results_ready)
  content:
    acknowledgment:
      received_input: string (summary of understanding)
      next_actions: list[string]
      estimated_time: duration
    clarification_request:
      ambiguous_aspects: list[string]
      suggested_interpretations: list[string]
      required_information: list[string]
    status_update:
      current_phase: string
      hypotheses_generated: integer
      top_hypothesis_summary: string
      completion_percentage: float
    results_ready:
      hypothesis_count: integer
      top_ranked: list[HypothesisSummary]
      research_overview_available: boolean
```

### Progress Indicators
```
ResearchProgress:
  phases_completed: list[phase_name]
  current_activity: string
  quality_metrics:
    average_elo: float
    novelty_score: float
    review_coverage: float
  resource_usage:
    compute_consumed: float
    time_elapsed: duration
    remaining_budget: float
```

## Behavioral Contracts

### Input Processing Guarantees

The Natural Language Interface MUST:
- Accept research goals ranging from single sentences to extensive documents
- Parse natural language without requiring specific syntax
- Extract constraints and preferences from unstructured text
- Preserve scientist intent through all transformations
- Handle ambiguity through clarification requests

### Feedback Integration Rules

The interface MUST:
- Immediately acknowledge all scientist inputs
- Apply feedback to influence ongoing research
- Maintain feedback history for context
- Propagate ratings to ranking algorithms
- Enable feedback withdrawal or modification

### Communication Standards

The interface MUST:
- Use clear, jargon-free language in responses
- Provide scientific terminology when appropriate
- Summarize complex states concisely
- Offer detailed explanations on request
- Maintain professional, collaborative tone

## Interaction Protocols

### Initial Research Goal Submission

1. **Input Reception**
   - Scientist provides natural language goal
   - Interface acknowledges receipt
   - Initial parsing identifies key elements

2. **Clarification Phase**
   - System requests missing information
   - Scientist provides additional context
   - Iterative refinement until clear

3. **Configuration Generation**
   - Interface creates research plan configuration
   - Presents interpretation to scientist
   - Scientist confirms or adjusts

4. **Research Initiation**
   - Configuration passed to Supervisor Agent
   - Research process begins
   - Progress updates commence

### Ongoing Collaboration

1. **Hypothesis Review Flow**
   - System presents hypotheses for review
   - Scientist rates and comments
   - Feedback influences tournament rankings
   - High-rated hypotheses prioritized for evolution

2. **Research Redirection**
   - Scientist identifies promising direction
   - Natural language guidance provided
   - System adjusts generation focus
   - Confirmation of understanding given

3. **Custom Hypothesis Integration**
   - Scientist submits original hypothesis
   - System validates format completeness
   - Hypothesis enters tournament system
   - Evolution may enhance scientist's idea

### Chat-Based Interaction

The interface supports conversational engagement:

- **Context Awareness**: Maintains conversation history
- **Reference Resolution**: Links pronouns to hypotheses/concepts
- **Incremental Refinement**: Builds understanding over multiple exchanges
- **Flexible Timing**: Asynchronous or synchronous communication
- **Multi-turn Reasoning**: Complex ideas developed through dialogue

## Error Handling

### Invalid Input Management

When receiving problematic input, the interface:

1. **Identifies Issue Type**
   - Ambiguous research goals
   - Conflicting constraints
   - Unrealistic requirements
   - Safety concerns

2. **Provides Helpful Response**
   - Explains why input is problematic
   - Suggests valid alternatives
   - Offers examples of proper format
   - Maintains supportive tone

3. **Enables Recovery**
   - Allows input modification
   - Preserves valid portions
   - Suggests incremental fixes
   - Avoids data loss

### Communication Failures

The interface handles disruptions by:

- **State Preservation**: Saving all inputs before processing
- **Graceful Degradation**: Continuing with partial information
- **Clear Error Messages**: Explaining what went wrong
- **Recovery Options**: Offering ways to resume
- **Fallback Modes**: Alternative interaction methods

## Quality Requirements

### Usability Standards

The interface ensures:

- **Response Time**: <2 seconds for acknowledgment
- **Clarity**: 90%+ scientist comprehension rate
- **Efficiency**: Minimal back-and-forth for goal specification
- **Flexibility**: Accommodates diverse scientific domains
- **Accessibility**: Works with various input methods

### Scientific Accuracy

The interface maintains:

- **Terminology Precision**: Correct use of domain terms
- **Concept Integrity**: No distortion of scientific ideas
- **Constraint Fidelity**: Accurate capture of requirements
- **Preference Preservation**: Scientist priorities respected
- **Nuance Recognition**: Subtle distinctions preserved

## Example Interactions

### Example 1: Initial Goal Specification
```
Scientist: "I want to find new ways to treat liver fibrosis by targeting 
epigenetic mechanisms. Focus on reversible modifications that could restore 
normal hepatocyte function. We have access to organoid models for testing."

System: "I understand you're looking for novel therapeutic approaches for 
liver fibrosis through epigenetic mechanisms. I'll focus on:
- Reversible epigenetic modifications
- Restoration of hepatocyte function
- Validation using organoid models

Shall I proceed with these parameters?"

Scientist: "Yes, but also exclude HDAC inhibitors as we've already 
explored those extensively."

System: "Understood. I'll exclude HDAC inhibitors from the search. 
Beginning research with these constraints. I'll generate hypotheses 
targeting other epigenetic mechanisms like methylation, acetylation 
of non-histone proteins, and chromatin remodeling complexes."
```

### Example 2: Mid-Research Guidance
```
System: "I've generated 47 hypotheses so far. The top-ranked hypothesis 
(Elo: 1432) suggests targeting KDM4A demethylase to reverse stellate 
cell activation. Would you like to review the top candidates?"

Scientist: "Show me hypotheses related to DNA methylation specifically. 
I think that's more promising than histone modifications for our model."

System: "Filtering for DNA methylation-related hypotheses. I found 12 
candidates. The highest-ranked (Elo: 1398) proposes inhibiting DNMT3B 
to prevent hepatocyte-to-myofibroblast transition. I'll also adjust 
future generation to emphasize DNA methylation mechanisms."
```

### Example 3: Collaborative Hypothesis Development
```
Scientist: "I have an idea about using combination therapy - what if 
we target both TET enzymes and vitamin D receptor signaling? There's 
some evidence they interact in other fibrotic diseases."

System: "Interesting hypothesis about TET/VDR interaction. I'll add this 
to the tournament system. Would you like me to:
1. Keep it as-is for ranking
2. Generate variations exploring different TET family members
3. Research supporting evidence for the interaction

What would be most helpful?"

Scientist: "Do option 2 and 3. I want to see if this concept has legs."

System: "I'll generate variations for TET1, TET2, and TET3 combined with 
VDR signaling, and search for evidence of their interaction in fibrotic 
processes. These will enter the tournament as separate but related 
hypotheses."
```

## Integration Requirements

### With Supervisor Agent
- Transforms natural language into structured research configurations
- Receives progress updates for scientist communication
- Forwards intervention requests immediately
- Maintains bidirectional state synchronization

### With Context Memory
- Stores all scientist interactions for history
- Retrieves previous feedback for context
- Enables conversation resumption after breaks
- Supports preference learning over time

### With Other Components
- Formats hypotheses for human readability
- Translates technical metrics into insights
- Bridges between scientific and system terminology
- Maintains consistent interaction patterns

This specification defines how scientists interact naturally with the AI Co-Scientist system, enabling productive collaboration while maintaining scientific rigor and system efficiency.