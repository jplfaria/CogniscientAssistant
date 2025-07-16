# BAML Schemas Quick Reference for AI Co-Scientist

This file provides BAML schema templates for the implementation loop. Use these as starting points when implementing agents.

## Core Data Types

```baml
class Hypothesis {
  id string @description("Unique identifier")
  summary string @description("One-line hypothesis statement")
  description string @description("Full scientific hypothesis")
  experimental_protocol string @description("How to test this hypothesis")
  confidence float @description("0.0 to 1.0 confidence score")
  safety_score float @description("0.0 to 1.0 safety rating")
  elo_rating float @description("Current Elo rating, starts at 1200")
  state string @description("GENERATED|UNDER_REVIEW|REVIEWED|RANKED|etc")
}

class ResearchGoal {
  goal string @description("Natural language research objective")
  constraints string[] @description("Any limitations or requirements")
  safety_cleared boolean @description("Passed initial safety check")
}

class ReviewResult {
  hypothesis_id string
  review_type string @description("initial|full|deep_verification|safety")
  passed boolean
  feedback string
  suggestions string[]
  safety_concerns string[]
}

class TournamentMatch {
  hypothesis_1 Hypothesis
  hypothesis_2 Hypothesis
  debate_turns string[] @description("Alternating arguments")
  winner_id string
  rationale string
  elo_change float
}
```

## Agent Functions

### Generation Agent
```baml
function generate_hypotheses(
  goal: ResearchGoal,
  context: string,
  feedback: string?
) -> Hypothesis[] {
  client ArgoAI
  prompt #"
    Research Goal: {{ goal.goal }}
    Context from previous iterations: {{ context }}
    {% if feedback %}Meta-review feedback: {{ feedback }}{% endif %}
    
    Generate 10-20 novel scientific hypotheses that:
    1. Address the research goal directly
    2. Are scientifically plausible and testable
    3. Include specific experimental protocols
    4. Are safe and ethical
    
    Focus on diversity of approaches.
  "#
}
```

### Reflection Agent
```baml
function review_hypothesis(
  hypothesis: Hypothesis,
  review_type: string,
  research_goal: ResearchGoal
) -> ReviewResult {
  client ArgoAI
  prompt #"
    Review Type: {{ review_type }}
    Research Goal: {{ research_goal.goal }}
    
    Hypothesis: {{ hypothesis.summary }}
    Description: {{ hypothesis.description }}
    Protocol: {{ hypothesis.experimental_protocol }}
    
    Evaluate based on:
    1. Alignment with research goal
    2. Scientific validity
    3. Novelty
    4. Testability
    5. Safety and ethics
    
    Provide specific feedback and suggestions.
  "#
}
```

### Ranking Agent
```baml
function compare_hypotheses(
  h1: Hypothesis,
  h2: Hypothesis,
  research_goal: ResearchGoal,
  debate_depth: string
) -> TournamentMatch {
  client ArgoAI
  prompt #"
    Research Goal: {{ research_goal.goal }}
    Debate Depth: {{ debate_depth }}
    
    Hypothesis 1: {{ h1.summary }}
    Hypothesis 2: {{ h2.summary }}
    
    Conduct a scientific debate comparing these hypotheses.
    Consider: novelty, feasibility, potential impact, rigor.
    
    {% if debate_depth == "multi_turn" %}
    Provide 3 rounds of arguments from each hypothesis.
    {% else %}
    Provide one strong argument for each.
    {% endif %}
    
    Determine the winner and explain why.
  "#
}
```

### Evolution Agent
```baml
function evolve_hypothesis(
  hypothesis: Hypothesis,
  strategy: string,
  context: string
) -> Hypothesis {
  client ArgoAI
  prompt #"
    Original: {{ hypothesis.summary }}
    Evolution Strategy: {{ strategy }}
    Context: {{ context }}
    
    Apply the {{ strategy }} strategy:
    {% if strategy == "enhancement" %}
    Strengthen with additional evidence and methods
    {% elif strategy == "combination" %}
    Combine with related ideas from context
    {% elif strategy == "simplification" %}
    Make more testable and focused
    {% elif strategy == "out_of_box" %}
    Generate radical alternative approach
    {% endif %}
    
    Maintain scientific rigor and safety.
  "#
}
```

### Meta-review Agent
```baml
function synthesize_feedback(
  iteration_data: string,
  agent_metrics: string
) -> MetaReviewResult {
  client ArgoAI
  prompt #"
    Iteration Data: {{ iteration_data }}
    Agent Performance: {{ agent_metrics }}
    
    Analyze patterns across all agent activities:
    1. What strategies are working well?
    2. What common issues are occurring?
    3. How can hypothesis quality improve?
    4. Are we converging on good solutions?
    
    Provide specific feedback for each agent type.
  "#
}
```

## Client Configuration

```baml
client ArgoAI {
  provider openai
  options {
    base_url "http://localhost:8050/v1"
    model "gpt4o"  // or "claudeopus4"
    temperature 0.7
    max_tokens 2000
  }
}

// For safety-critical operations
client ArgoAISafety {
  provider openai
  options {
    base_url "http://localhost:8050/v1"
    model "gpt4o"
    temperature 0.1  // Lower temperature for consistency
    max_tokens 1000
  }
}
```

## Usage in Python

```python
from baml_client import b
from baml_types import Hypothesis, ResearchGoal

async def generate_hypotheses_batch(goal: ResearchGoal) -> List[Hypothesis]:
    """Generate hypotheses using BAML."""
    context = await load_context()
    feedback = await get_latest_feedback()
    
    # BAML function call
    hypotheses = await b.generate_hypotheses(
        goal=goal,
        context=context,
        feedback=feedback
    )
    
    # Post-process
    for h in hypotheses:
        h.id = generate_id()
        h.elo_rating = 1200.0
        h.state = "GENERATED"
    
    return hypotheses
```

## Testing BAML Functions

```baml
test generate_hypotheses_test {
  functions [generate_hypotheses]
  args {
    goal {
      goal "Find novel antimicrobial resistance mechanisms"
      constraints ["Focus on gram-negative bacteria", "Consider CRISPR applications"]
      safety_cleared true
    }
    context "Previous iterations explored efflux pumps and biofilm formation"
    feedback null
  }
  checks {
    assert len(result) >= 10
    assert all(h.confidence > 0.5 for h in result)
    assert all(h.safety_score > 0.8 for h in result)
  }
}
```