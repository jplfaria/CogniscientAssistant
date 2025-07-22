// BAML Function Template - CRITICAL FOR MODEL COMPATIBILITY
// 
// This template MUST be used for all new BAML functions to ensure compatibility
// with Claude and Gemini models, which require at least one user message.
//
// Created: 2025-01-22
// Reason: Claude/Gemini fail with system-only messages, returning content as dict

// Example 1: Simple Analysis Function Template
// function ExampleAnalyzeContent(
//   content: string @description("The content to analyze"),
//   criteria: string[] @description("Analysis criteria")  
// ) -> AnalysisResult {
//   client ProductionClient
//   
//   prompt #"
//     {{ _.role("system") }}
//     You are an expert analyst capable of examining content across multiple dimensions.
//     You provide structured, detailed analysis based on specified criteria.
//     
//     {{ _.role("user") }}
//     Please analyze the following content according to the specified criteria.
//     
//     Content to analyze:
//     {{ content }}
//     
//     Analysis criteria:
//     {{ criteria }}
//     
//     Provide a comprehensive analysis addressing each criterion.
//   "#
// }

// Example 2: Generation Function Template with Context
// function ExampleGenerateContent(
//   goal: string @description("The generation goal"),
//   context: Context @description("Additional context"),
//   strategy: string @description("Generation strategy to use")
// ) -> GeneratedContent {
//   client ProductionClient
//   
//   prompt #"
//     {{ _.role("system") }}
//     You are an expert content generator with deep knowledge across
//     multiple domains. You excel at creating novel, high-quality content
//     that meets specific requirements while being creative and insightful.
//     
//     {{ _.role("user") }}
//     Generate content for the following goal.
//     
//     Goal: {{ goal }}
//     
//     Context:
//     - Domain: {{ context.domain }}
//     - Constraints: {{ context.constraints }}
//     - Requirements: {{ context.requirements }}
//     
//     Strategy: {{ strategy }}
//     
//     Create content that is:
//     1. Novel and engaging
//     2. Accurate and well-researched
//     3. Aligned with the stated goal
//     4. Following all constraints
//   "#
// }

// Example 3: Evaluation Function Template
// function ExampleEvaluateContent(
//   content: Content @description("The content to evaluate"),
//   criteria: EvaluationCriteria @description("Criteria for evaluation")
// ) -> ContentReview {
//   client ProductionClient
//   
//   prompt #"
//     {{ _.role("system") }}
//     You are a rigorous reviewer with expertise in evaluating content.
//     You provide balanced, constructive feedback that identifies both
//     strengths and weaknesses while suggesting improvements.
//     
//     {{ _.role("user") }}
//     Please evaluate the following content.
//     
//     Content Summary: {{ content.summary }}
//     
//     Detailed Content: {{ content.details }}
//     
//     Evaluation Criteria:
//     - Quality weight: {{ criteria.quality_weight }}
//     - Accuracy weight: {{ criteria.accuracy_weight }}
//     - Relevance weight: {{ criteria.relevance_weight }}
//     
//     Provide a thorough evaluation addressing:
//     1. Overall quality and clarity
//     2. Accuracy and correctness
//     3. Relevance to objectives
//     4. Strengths and weaknesses
//     5. Suggested improvements
//   "#
// }

// TEMPLATE RULES:
// 1. ALWAYS use both {{ _.role("system") }} and {{ _.role("user") }}
// 2. System role: General capabilities and expertise
// 3. User role: Specific task request with parameters
// 4. Put input parameters in the user section
// 5. Be explicit about output format expectations
// 6. Test with multiple models before deployment

// Model-Specific Notes:
// - o3 models: Use max_completion_tokens (NOT max_tokens)
// - Claude models: Require user message, system content must be string
// - Gemini models: Also require user message
// - All models: Support both system and user roles

// Common Mistakes to Avoid:
// ❌ Using only system message
// ❌ Putting all content in system role
// ❌ Not including {{ _.role() }} markers
// ❌ Assuming all models have same requirements