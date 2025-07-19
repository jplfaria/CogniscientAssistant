// Core data models for AI Co-Scientist

// Enums

enum HypothesisCategory {
    mechanistic
    therapeutic
    diagnostic
    biomarker
    methodology
    other
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