// BAML Function Definitions for AI Co-Scientist
// This file defines all LLM-based functions used by agents

// ============================================================================
// Hypothesis Generation Functions
// ============================================================================

// Generate a new hypothesis based on research goal and context
function GenerateHypothesis(
  goal: string @description("Research goal or objective"),
  constraints: string[] @description("Constraints to consider (ethical, practical, etc.)"),
  existing_hypotheses: Hypothesis[] @description("Already generated hypotheses to avoid duplication"),
  focus_area: string? @description("Specific area to focus on"),
  generation_method: string @description("Method to use: literature_based, debate, assumptions, or expansion")
) -> Hypothesis {
  client DefaultClient
  
  prompt #"
    You are a brilliant research scientist tasked with generating novel hypotheses.
    
    Research Goal: {{ goal }}
    
    Constraints to consider:
    {{ constraints }}
    
    {% if existing_hypotheses %}
    Already explored hypotheses (avoid duplication):
    {% for hyp in existing_hypotheses %}
    - {{ hyp.summary }}
    {% endfor %}
    {% endif %}
    
    {% if focus_area %}
    Focus Area: {{ focus_area }}
    {% endif %}
    
    Generation Method: {{ generation_method }}
    
    Based on the {{ generation_method }} approach, generate a novel hypothesis that:
    1. Addresses the research goal
    2. Respects all constraints
    3. Is scientifically plausible
    4. Offers potential for significant discovery
    5. Is distinct from existing hypotheses
    
    Provide a complete hypothesis with experimental protocol and supporting evidence.
  "#
}

// ============================================================================
// Hypothesis Evaluation Functions
// ============================================================================

// Evaluate a hypothesis from different perspectives
function EvaluateHypothesis(
  hypothesis: Hypothesis @description("The hypothesis to evaluate"),
  review_type: ReviewType @description("Type of review to perform"),
  evaluation_criteria: string[] @description("Specific criteria to evaluate against"),
  context: map<string, string>? @description("Additional context for evaluation")
) -> Review {
  client DefaultClient
  
  prompt #"
    You are an expert scientific reviewer performing a {{ review_type }} review.
    
    Hypothesis to evaluate:
    Summary: {{ hypothesis.summary }}
    Full Description: {{ hypothesis.full_description }}
    Novelty Claim: {{ hypothesis.novelty_claim }}
    
    Assumptions:
    {% for assumption in hypothesis.assumptions %}
    - {{ assumption }}
    {% endfor %}
    
    Experimental Protocol:
    Objective: {{ hypothesis.experimental_protocol.objective }}
    Methodology: {{ hypothesis.experimental_protocol.methodology }}
    
    Evaluation Criteria:
    {{ evaluation_criteria }}
    
    {% if context %}
    Additional Context:
    {{ context }}
    {% endif %}
    
    Perform a thorough {{ review_type }} review, providing:
    1. Quantitative scores (0-1) for correctness, quality, novelty, safety, and feasibility
    2. Detailed narrative feedback
    3. Key strengths and weaknesses
    4. Specific improvement suggestions
    5. Your confidence level in this assessment
    
    {% if review_type == "deep_verification" %}
    Additionally, decompose and evaluate each assumption for validity and criticality.
    {% endif %}
    
    {% if review_type == "simulation" %}
    Additionally, simulate the experimental mechanism step-by-step and identify potential failure points.
    {% endif %}
  "#
}

// ============================================================================
// Safety Check Functions
// ============================================================================

// Perform safety check on hypothesis or task
function PerformSafetyCheck(
  target_type: string @description("Type of item: hypothesis, task, or goal"),
  target_content: string @description("Content to check for safety"),
  trust_level: string @description("Trust level: high, medium, or low"),
  safety_criteria: string[] @description("Specific safety criteria to check")
) -> SafetyCheck {
  client DefaultClient
  
  prompt #"
    You are a safety evaluator for a scientific research system.
    
    Item Type: {{ target_type }}
    Trust Level: {{ trust_level }}
    
    Content to evaluate:
    {{ target_content }}
    
    Safety Criteria to check:
    {{ safety_criteria }}
    
    Evaluate the content for:
    1. Ethical concerns
    2. Potential for harm
    3. Resource misuse
    4. Goal alignment
    5. Content appropriateness
    
    Provide a comprehensive safety assessment including:
    - Overall safety level (safe, concerning, or blocked)
    - Specific checks performed
    - Any violations found
    - Recommendations for addressing concerns
    - The primary category of any safety issues
    
    Be appropriately cautious based on the trust level, but avoid being overly restrictive
    for legitimate scientific research within ethical bounds.
  "#
}

// ============================================================================
// Hypothesis Comparison Functions
// ============================================================================

// Compare two hypotheses for ranking
function CompareHypotheses(
  hypothesis1: Hypothesis @description("First hypothesis"),
  hypothesis2: Hypothesis @description("Second hypothesis"),
  comparison_criteria: string[] @description("Criteria for comparison"),
  debate_context: string? @description("Context from ongoing debate if applicable")
) -> ComparisonResult {
  client DefaultClient
  
  prompt #"
    You are a scientific judge comparing two research hypotheses.
    
    Hypothesis 1 (ID: {{ hypothesis1.id }}):
    {{ hypothesis1.summary }}
    Novelty: {{ hypothesis1.novelty_claim }}
    
    Hypothesis 2 (ID: {{ hypothesis2.id }}):
    {{ hypothesis2.summary }}
    Novelty: {{ hypothesis2.novelty_claim }}
    
    Comparison Criteria:
    {{ comparison_criteria }}
    
    {% if debate_context %}
    Debate Context:
    {{ debate_context }}
    {% endif %}
    
    Compare these hypotheses and determine which is superior based on:
    1. Scientific merit and rigor
    2. Novelty and potential impact
    3. Feasibility and testability
    4. Evidence support
    5. The specified comparison criteria
    
    Provide a fair, thorough comparison with clear reasoning.
  "#
}

// ============================================================================
// Hypothesis Enhancement Functions
// ============================================================================

// Enhance or evolve a hypothesis
function EnhanceHypothesis(
  original_hypothesis: Hypothesis @description("Hypothesis to enhance"),
  enhancement_strategy: string @description("Strategy: refine, combine, simplify, or paradigm_shift"),
  feedback: string[]? @description("Feedback to incorporate"),
  complementary_hypothesis: Hypothesis? @description("For combination strategy")
) -> Hypothesis {
  client DefaultClient
  
  prompt #"
    You are a research scientist tasked with improving a hypothesis.
    
    Original Hypothesis:
    {{ original_hypothesis.summary }}
    {{ original_hypothesis.full_description }}
    
    Enhancement Strategy: {{ enhancement_strategy }}
    
    {% if feedback %}
    Feedback to address:
    {% for item in feedback %}
    - {{ item }}
    {% endfor %}
    {% endif %}
    
    {% if complementary_hypothesis %}
    Complementary Hypothesis (for combination):
    {{ complementary_hypothesis.summary }}
    {% endif %}
    
    Based on the {{ enhancement_strategy }} strategy:
    
    {% if enhancement_strategy == "refine" %}
    Refine the hypothesis by addressing weaknesses and incorporating feedback while
    maintaining its core insight.
    {% elif enhancement_strategy == "combine" %}
    Combine the original and complementary hypotheses into a unified, stronger hypothesis
    that leverages insights from both.
    {% elif enhancement_strategy == "simplify" %}
    Simplify the hypothesis to its essential components, making it more elegant and testable
    while preserving its key insights.
    {% elif enhancement_strategy == "paradigm_shift" %}
    Transform the hypothesis by challenging its fundamental assumptions and proposing
    a radically different perspective on the same problem.
    {% endif %}
    
    Generate an enhanced hypothesis that improves upon the original.
  "#
}

// ============================================================================
// Semantic Similarity Functions
// ============================================================================

// Calculate semantic similarity between hypotheses
function CalculateSimilarity(
  hypothesis1: Hypothesis @description("First hypothesis"),
  hypothesis2: Hypothesis @description("Second hypothesis"),
  similarity_aspects: string[] @description("Aspects to compare: mechanism, domain, methodology")
) -> SimilarityScore {
  client DefaultClient
  
  prompt #"
    You are analyzing the semantic similarity between two research hypotheses.
    
    Hypothesis 1:
    {{ hypothesis1.summary }}
    Category: {{ hypothesis1.category }}
    
    Hypothesis 2:
    {{ hypothesis2.summary }}
    Category: {{ hypothesis2.category }}
    
    Analyze similarity across these aspects:
    {{ similarity_aspects }}
    
    For each aspect, provide a similarity score (0-1) where:
    - 0 = completely different
    - 0.5 = some overlap
    - 1 = nearly identical
    
    Also identify:
    1. Shared concepts and mechanisms
    2. Key differences
    3. Overall semantic similarity
    
    Be precise in your similarity assessment.
  "#
}

// ============================================================================
// Meta-Review Functions
// ============================================================================

// Extract patterns across multiple hypotheses and reviews
function ExtractResearchPatterns(
  hypotheses: Hypothesis[] @description("All hypotheses to analyze"),
  reviews: Review[] @description("All reviews to analyze"),
  focus: string @description("Focus area: methodology, assumptions, or themes")
) -> ResearchPatterns {
  client DefaultClient
  
  prompt #"
    You are performing a meta-analysis of research hypotheses and their reviews.
    
    Number of hypotheses: {{ hypotheses | length }}
    Number of reviews: {{ reviews | length }}
    Analysis Focus: {{ focus }}
    
    Hypothesis Categories:
    {% for hyp in hypotheses %}
    - {{ hyp.category }}: {{ hyp.summary }}
    {% endfor %}
    
    Review Insights:
    {% for review in reviews %}
    - Type: {{ review.review_type }}, Decision: {{ review.decision }}
      Key feedback: {{ review.key_strengths[0] if review.key_strengths else "N/A" }}
    {% endfor %}
    
    Analyze the corpus to identify:
    1. Recurring patterns in {{ focus }}
    2. Common strengths that lead to positive reviews
    3. Common weaknesses that need addressing
    4. Emerging themes in the research
    5. Strategic recommendations for future hypothesis generation
    
    Provide actionable insights for improving the research process.
  "#
}

// ============================================================================
// Research Goal Parsing Functions
// ============================================================================

// Parse natural language research goal into structured format
function ParseResearchGoal(
  natural_language_goal: string @description("User's research goal in natural language"),
  domain_context: string? @description("Scientific domain if specified")
) -> ParsedResearchGoal {
  client DefaultClient
  
  prompt #"
    You are parsing a research goal into structured components.
    
    Research Goal: {{ natural_language_goal }}
    
    {% if domain_context %}
    Domain: {{ domain_context }}
    {% endif %}
    
    Analyze this goal and extract:
    1. The primary research objective (one clear statement)
    2. Sub-objectives that support the main goal
    3. Implied constraints (ethical, practical, scientific)
    4. Relevant hypothesis categories (mechanistic, therapeutic, etc.)
    5. Key scientific terms and concepts
    6. Success criteria - what outcomes would satisfy this goal
    
    Be thorough but concise in your analysis.
  "#
}

// Test blocks can be added later with correct BAML test syntax

// Test configurations
test TestClient {
    functions [GenerateHypothesis, EvaluateHypothesis, PerformSafetyCheck, CompareHypotheses]
    
    // Test data can be added here
}

test ErrorScenarios {
    client TestErrorClient
    functions [GenerateHypothesis]
}

test PerformanceScenarios {
    client TestSlowClient  
    functions [GenerateHypothesis]
}

test EdgeCaseScenarios {
    client TestContextClient
    functions [GenerateHypothesis]
}
