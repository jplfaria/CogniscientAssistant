// BAML Function Definitions for AI Co-Scientist
// This file defines all LLM-based functions used by agents

// Import models from models.baml
use models from "./models.baml"

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
  context: map<string, any>? @description("Additional context for evaluation")
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
) -> class ComparisonResult {
  winner_id: string @description("ID of the winning hypothesis")
  confidence: float @description("Confidence in the comparison (0-1)")
  reasoning: string @description("Detailed reasoning for the decision")
  strengths_h1: string[] @description("Key strengths of hypothesis 1")
  strengths_h2: string[] @description("Key strengths of hypothesis 2")
  decisive_factors: string[] @description("Factors that determined the winner")
} {
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
) -> class SimilarityScore {
  overall_similarity: float @description("Overall similarity score (0-1)")
  aspect_scores: map<string, float> @description("Similarity scores per aspect")
  shared_concepts: string[] @description("Key concepts shared between hypotheses")
  key_differences: string[] @description("Main differences identified")
} {
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
) -> class ResearchPatterns {
  identified_patterns: string[] @description("Key patterns identified")
  common_strengths: string[] @description("Recurring strengths across hypotheses")
  common_weaknesses: string[] @description("Recurring weaknesses")
  emerging_themes: string[] @description("Emerging research themes")
  recommendations: string[] @description("Strategic recommendations")
  synthesis_summary: string @description("High-level synthesis of findings")
} {
  client DefaultClient
  
  prompt #"
    You are performing a meta-analysis of research hypotheses and their reviews.
    
    Number of hypotheses: {{ hypotheses.length }}
    Number of reviews: {{ reviews.length }}
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
) -> class ParsedResearchGoal {
  primary_objective: string @description("Main research objective")
  sub_objectives: string[] @description("Broken down sub-objectives")
  implied_constraints: string[] @description("Constraints inferred from the goal")
  suggested_categories: string[] @description("Relevant hypothesis categories")
  key_terms: string[] @description("Important scientific terms identified")
  success_criteria: string[] @description("What would constitute success")
} {
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

// ============================================================================
// Test Blocks for Function Validation
// ============================================================================

test TestGenerateHypothesis {
  function GenerateHypothesis(
    goal="Develop new treatments for antibiotic-resistant bacteria",
    constraints=["Must not involve human subjects", "Limited to in-vitro experiments"],
    existing_hypotheses=[],
    generation_method="literature_based"
  )
  
  assert {
    _.id != null
    _.summary != null
    _.category in ["therapeutic", "mechanistic"]
    _.assumptions.length > 0
    _.experimental_protocol.objective != null
  }
}

test TestEvaluateHypothesis {
  function EvaluateHypothesis(
    hypothesis={
      id: "hyp_test_001",
      summary: "Novel antibiotic compounds from deep-sea microorganisms",
      category: "therapeutic",
      full_description: "Exploration of deep-sea microorganism metabolites...",
      novelty_claim: "First systematic exploration of abyssal zone organisms",
      assumptions: ["Deep-sea organisms produce unique metabolites"],
      experimental_protocol: {
        objective: "Isolate and test novel compounds",
        methodology: "Culture and extraction methods",
        required_resources: ["Deep-sea samples", "Culture facilities"],
        timeline: "12 months",
        success_metrics: ["Compound activity against resistant strains"],
        potential_challenges: ["Sample collection difficulty"],
        safety_considerations: ["BSL-2 containment required"]
      },
      supporting_evidence: [],
      confidence_score: 0.7,
      generation_method: "literature_based",
      created_at: "2025-01-19T10:00:00Z"
    },
    review_type="initial",
    evaluation_criteria=["Scientific merit", "Feasibility", "Novelty"]
  )
  
  assert {
    _.id != null
    _.hypothesis_id == "hyp_test_001"
    _.review_type == "initial"
    _.decision in ["accept", "reject", "revise"]
    _.scores.correctness >= 0.0
    _.scores.correctness <= 1.0
    _.key_strengths.length > 0
  }
}

test TestPerformSafetyCheck {
  function PerformSafetyCheck(
    target_type="hypothesis",
    target_content="Research into bacteriophage therapy for resistant infections",
    trust_level="medium",
    safety_criteria=["No human experimentation", "Ethical use of resources"]
  )
  
  assert {
    _.id != null
    _.target_type == "hypothesis"
    _.safety_level in ["safe", "concerning", "blocked"]
    _.passed != null
    _.checks_performed.length > 0
    _.timestamp != null
  }
}

test TestCompareHypotheses {
  function CompareHypotheses(
    hypothesis1={
      id: "hyp_001",
      summary: "Phage therapy approach",
      category: "therapeutic",
      full_description: "Using bacteriophages to target resistant bacteria",
      novelty_claim: "Novel phage cocktail design",
      assumptions: ["Phages can be engineered for specificity"],
      experimental_protocol: {
        objective: "Test phage effectiveness",
        methodology: "In-vitro phage assays",
        required_resources: ["Phage library"],
        timeline: "6 months",
        success_metrics: ["Bacterial kill rate"],
        potential_challenges: ["Phage resistance"],
        safety_considerations: ["Containment protocols"]
      },
      supporting_evidence: [],
      confidence_score: 0.8,
      generation_method: "literature_based",
      created_at: "2025-01-19T10:00:00Z"
    },
    hypothesis2={
      id: "hyp_002",
      summary: "Antimicrobial peptide approach",
      category: "therapeutic",
      full_description: "Synthetic antimicrobial peptides design",
      novelty_claim: "AI-designed peptide sequences",
      assumptions: ["Peptides can penetrate bacterial membranes"],
      experimental_protocol: {
        objective: "Test peptide activity",
        methodology: "Peptide synthesis and testing",
        required_resources: ["Peptide synthesizer"],
        timeline: "9 months",
        success_metrics: ["MIC values"],
        potential_challenges: ["Peptide stability"],
        safety_considerations: ["Toxicity testing required"]
      },
      supporting_evidence: [],
      confidence_score: 0.7,
      generation_method: "debate",
      created_at: "2025-01-19T10:00:00Z"
    },
    comparison_criteria=["Feasibility", "Potential impact", "Time to implementation"]
  )
  
  assert {
    _.winner_id in ["hyp_001", "hyp_002"]
    _.confidence >= 0.0
    _.confidence <= 1.0
    _.reasoning != null
    _.decisive_factors.length > 0
  }
}