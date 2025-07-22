// Core data models for AI Co-Scientist

// Enums

enum HypothesisCategory {
    Mechanistic @alias("mechanistic")
    Therapeutic @alias("therapeutic")
    Diagnostic @alias("diagnostic")
    Biomarker @alias("biomarker")
    Methodology @alias("methodology")
    Other @alias("other")
}

enum ReviewType {
    Initial @alias("initial")
    Full @alias("full")
    DeepVerification @alias("deep_verification")
    Observation @alias("observation")
    Simulation @alias("simulation")
    Tournament @alias("tournament")
}

enum ReviewDecision {
    Accept @alias("accept")
    Reject @alias("reject")
    Revise @alias("revise")
}

enum ConfidenceLevel {
    High @alias("high")
    Medium @alias("medium")
    Low @alias("low")
}

enum Validity {
    Valid @alias("valid")
    Questionable @alias("questionable")
    Invalid @alias("invalid")
}

enum Criticality {
    Fundamental @alias("fundamental")
    Peripheral @alias("peripheral")
}

enum SafetyLevel {
    Safe @alias("safe")
    Concerning @alias("concerning")
    Blocked @alias("blocked")
}

enum SafetyCategory {
    ContentSafety @alias("content_safety")
    GoalViolation @alias("goal_violation")
    EthicalConcern @alias("ethical_concern")
    ResourceMisuse @alias("resource_misuse")
}

enum TaskType {
    GenerateHypothesis
    ReflectOnHypothesis
    RankHypotheses
    EvolveHypothesis
    FindSimilarHypotheses
    MetaReview
}

enum TaskState {
    Pending
    Assigned
    Executing
    Completed
    Failed
}

enum AgentType {
    Generation
    Reflection
    Ranking
    Evolution
    Proximity
    MetaReview
    Supervisor
}

enum RequestType {
    Generate
    Analyze
    Evaluate
    Compare
}

enum ResponseStatus {
    Success
    Error
    Partial
}

// Supporting Classes

class Citation {
    authors string[] @description("List of authors")
    title string @description("Title of the publication")
    journal string? @description("Journal name, if applicable")
    year int @description("Publication year")
    doi string? @description("DOI identifier")
    url string? @description("URL to the publication")
}

class ExperimentalProtocol {
    objective string @description("Main objective of the experiment")
    methodology string @description("Detailed methodology")
    required_resources string[] @description("Resources needed for the experiment")
    timeline string @description("Expected timeline for completion")
    success_metrics string[] @description("Metrics to measure success")
    potential_challenges string[] @description("Anticipated challenges")
    safety_considerations string[] @description("Safety considerations and precautions")
}

class HypothesisSummary {
    core_idea string @description("The central idea in one sentence")
    scientific_impact string @description("Potential scientific impact")
    feasibility_assessment string @description("Assessment of feasibility")
    next_steps string[] @description("Recommended next steps")
}

// Main Hypothesis Class

class Hypothesis {
    id string @description("Unique identifier for the hypothesis")
    summary string @description("Concise one-sentence description")
    category string @description("Category of the hypothesis")
    full_description string @description("Detailed description of the hypothesis")
    novelty_claim string @description("What makes this hypothesis novel")
    assumptions string[] @description("Key assumptions made")
    reasoning string @description("Reasoning process behind the hypothesis")
    experimental_protocol ExperimentalProtocol @description("Protocol for testing the hypothesis")
    supporting_evidence Citation[] @description("Supporting literature and evidence")
    confidence_score float @description("0-1 confidence score")
    generation_method string @description("Method used to generate this hypothesis")
    created_at string @description("Creation timestamp in ISO format")
    
    // Optional tracking fields
    elo_rating float? @description("Elo rating for tournament ranking")
    review_count int? @description("Number of reviews received")
    evolution_count int? @description("Number of times evolved")
}

// Review-related Classes

class ReviewScores {
    correctness float @description("0-1 score for scientific accuracy")
    quality float @description("0-1 score for rigor and completeness")
    novelty float @description("0-1 score for genuine advancement")
    safety float @description("0-1 score for ethical considerations")
    feasibility float @description("0-1 score for practical viability")
}

class AssumptionDecomposition {
    assumption string @description("The assumption being evaluated")
    validity string @description("Assessment: valid, questionable, or invalid")
    evidence string @description("Evidence supporting the assessment")
    criticality string @description("Impact level: fundamental or peripheral")
}

class FailurePoint {
    step string @description("Description of the step in the mechanism")
    probability float @description("0-1 probability of failure at this step")
    impact string @description("Description of impact if failure occurs")
}

class SimulationResults {
    mechanism_steps string[] @description("Step-by-step breakdown of the mechanism")
    failure_points FailurePoint[] @description("Identified points of potential failure")
    predicted_outcomes string[] @description("Predicted experimental outcomes")
}

// Main Review Class

class Review {
    id string @description("Unique identifier for the review")
    hypothesis_id string @description("ID of the hypothesis being reviewed")
    reviewer_agent_id string @description("ID of the agent performing the review")
    review_type ReviewType @description("Type of review performed")
    decision ReviewDecision @description("Review decision: accept, reject, or revise")
    scores ReviewScores @description("Quantitative scoring across dimensions")
    
    // Narrative components
    narrative_feedback string @description("Detailed narrative review feedback")
    key_strengths string[] @description("Major strengths identified")
    key_weaknesses string[] @description("Major weaknesses identified")
    improvement_suggestions string[] @description("Specific suggestions for improvement")
    confidence_level string @description("Reviewer confidence: high, medium, or low")
    
    // Optional review-type specific data
    assumption_decomposition AssumptionDecomposition[]? @description("Deep verification analysis")
    simulation_results SimulationResults? @description("Results from simulation review")
    literature_citations Citation[]? @description("Supporting literature references")
    
    // Metadata
    created_at string @description("Review creation timestamp in ISO format")
    time_spent_seconds float? @description("Time spent on review in seconds")
}

// Safety-related Classes

class SafetyCheck {
    id string @description("Unique identifier for the safety check")
    target_type string @description("Type of item being checked (hypothesis, task, etc)")
    target_id string @description("ID of the item being checked")
    safety_level SafetyLevel @description("Overall safety assessment level")
    passed bool @description("Whether the item passed safety checks")
    checks_performed string[] @description("List of checks that were performed")
    
    // Details about safety issues
    violations string[]? @description("Specific safety violations found")
    recommendations string[]? @description("Recommendations for addressing safety concerns")
    category SafetyCategory? @description("Primary category of safety concern if any")
    
    // Metadata
    timestamp string @description("When the safety check was performed (ISO format)")
    metadata map<string, string>? @description("Additional context like trust level")
}

// Task-related Classes

class Task {
    id string @description("Unique identifier for the task")
    task_type TaskType @description("Type of task to be performed")
    priority int @description("Priority level, higher = more important")
    state TaskState @description("Current state of the task")
    payload map<string, string> @description("Task-specific data and parameters")
    
    // Assignment info
    assigned_to string? @description("ID of the worker/agent assigned to this task")
    
    // Results
    result map<string, string>? @description("Task execution result data")
    error string? @description("Error message if task failed")
    
    // Timestamps
    created_at string @description("Task creation timestamp in ISO format")
    assigned_at string? @description("When task was assigned (ISO format)")
    completed_at string? @description("When task completed/failed (ISO format)")
}

// Agent Request/Response Classes

class RequestContent {
    prompt string @description("Natural language instruction for the agent")
    context map<string, string> @description("Additional context including previous results, domain knowledge, constraints")
    parameters map<string, string> @description("Request parameters like max_length, temperature, response_format")
}

class AgentRequest {
    request_id string @description("Unique identifier for the request")
    agent_type AgentType @description("Type of agent making the request")
    request_type RequestType @description("Type of request being made")
    content RequestContent @description("Request content and parameters")
}

class ResponseData {
    content string @description("Generated or analyzed content")
    metadata map<string, string> @description("Response metadata including model_used, tokens_used, processing_time")
}

class ErrorInfo {
    code string @description("Error type identifier")
    message string @description("Human-readable error description")
    recoverable bool @description("Whether the error is recoverable")
}

class AgentResponse {
    request_id string @description("Matching input request ID")
    status ResponseStatus @description("Response status")
    response ResponseData? @description("Response data if successful")
    error ErrorInfo? @description("Error information if failed")
}

// Additional classes for BAML functions

class ComparisonResult {
    winner_id string @description("ID of the winning hypothesis")
    confidence float @description("Confidence in the comparison (0-1)")
    reasoning string @description("Detailed reasoning for the decision")
    strengths_h1 string[] @description("Key strengths of hypothesis 1")
    strengths_h2 string[] @description("Key strengths of hypothesis 2")
    decisive_factors string[] @description("Factors that determined the winner")
}

class SimilarityScore {
    overall_similarity float @description("Overall similarity score (0-1)")
    aspect_scores map<string, float> @description("Similarity scores per aspect")
    shared_concepts string[] @description("Key concepts shared between hypotheses")
    key_differences string[] @description("Main differences identified")
}

class ResearchPatterns {
    identified_patterns string[] @description("Key patterns identified")
    common_strengths string[] @description("Recurring strengths across hypotheses")
    common_weaknesses string[] @description("Recurring weaknesses")
    emerging_themes string[] @description("Emerging research themes")
    recommendations string[] @description("Strategic recommendations")
    synthesis_summary string @description("High-level synthesis of findings")
}

class ParsedResearchGoal {
    primary_objective string @description("Main research objective")
    sub_objectives string[] @description("Broken down sub-objectives")
    implied_constraints string[] @description("Constraints inferred from the goal")
    suggested_categories string[] @description("Relevant hypothesis categories")
    key_terms string[] @description("Important scientific terms identified")
    success_criteria string[] @description("What would constitute success")
}