# AI Co-Scientist Implementation Plan

This plan breaks down the implementation into atomic, testable units following TDD principles.

## Phase 1: Project Setup and Structure

- [x] Create project directory structure
- [x] Create pyproject.toml with dependencies
- [x] Set up development tools (pytest, mypy, ruff, coverage)
- [x] Create __init__.py files for all packages
- [x] Set up basic logging configuration
- [x] Create .gitignore for Python project

## Phase 2: Core Data Models

### Task Model
- [x] Create Task dataclass with id, type, priority fields
- [x] Add Task state enum (Pending, Assigned, Executing, Completed, Failed)
- [x] Add Task validation methods
- [x] Write comprehensive tests for Task model

### Hypothesis Model
- [x] Create Hypothesis dataclass with required fields from specs
- [x] Add hypothesis validation logic
- [x] Add serialization/deserialization methods
- [x] Write tests for Hypothesis model

### Review Model
- [x] Create Review dataclass for storing agent reviews
- [x] Add review type enum
- [x] Add review scoring methods
- [x] Write tests for Review model

## Phase 3: Task Queue Implementation

### Basic Queue Operations
- [x] Create TaskQueue class with basic structure
- [x] Implement enqueue method
- [x] Write tests for enqueue
- [x] Implement dequeue method with priority handling
- [x] Write tests for dequeue
- [x] Implement peek method
- [x] Write tests for peek

### Worker Management
- [x] Add worker registration methods
- [x] Write tests for worker registration
- [x] Implement task assignment logic
- [x] Write tests for task assignment
- [x] Add worker heartbeat tracking
- [x] Write tests for heartbeat tracking
- [x] Implement failure detection and recovery
- [x] Write tests for failure scenarios

### Queue State Management
- [x] Add queue statistics methods
- [x] Write tests for statistics
- [x] Implement queue persistence
- [x] Write tests for persistence
- [x] Add queue recovery on startup
- [x] Write tests for recovery

### Phase 3 Integration Test Updates
- [x] Update tests/integration/phase3_task_queue_workflow.py with expanded tests
- [x] Implement test_queue_capacity_limits
- [x] Implement test_task_overflow_handling  
- [x] Implement test_worker_heartbeat_timeout
- [x] Implement test_dead_letter_queue
- [x] Implement test_task_reassignment_on_failure
- [x] Implement test_starvation_prevention

## Phase 4: Context Memory Implementation

### Basic Storage
- [x] Create ContextMemory class structure
- [x] Implement file-based storage backend
- [x] Write tests for storage operations
- [x] Add key-value store methods
- [x] Write tests for key-value operations

### Hierarchical Organization
- [x] Implement iteration tracking
- [x] Write tests for iteration management
- [x] Add checkpoint functionality
- [x] Write tests for checkpoints
- [x] Implement aggregate storage
- [x] Write tests for aggregates

### Advanced Features
- [x] Add conflict resolution logic
- [x] Write tests for conflict resolution
- [x] Implement temporal guarantees
- [x] Write tests for temporal operations
- [x] Add memory cleanup/archival
- [x] Write tests for cleanup

### Integration Tests
- [x] Create tests/integration/test_phase4_memory_queue.py
- [x] Implement test_memory_storage_and_retrieval
- [x] Implement test_context_thread_isolation
- [x] Implement test_checkpoint_creation_and_recovery
- [x] Implement test_concurrent_write_conflict_resolution
- [x] Implement test_memory_version_history
- [x] Implement test_storage_overflow_handling
- [x] Implement test_agent_memory_integration (may_fail)
- [x] Implement test_memory_retrieval_performance (may_fail)
- [x] Implement test_periodic_archive_rotation (may_fail)
- [x] Implement test_garbage_collection (may_fail)

## Phase 5: Safety Framework

**Note**: Transitioned to lightweight safety system on 2025-01-18. Original heavy-handed 
specification archived due to API safety filter issues. See ADR-001 for details.

### Safety Models
- [x] Create SafetyLevel enum
- [x] Create SafetyCheck dataclass
- [x] Write tests for safety models

### Lightweight Safety System
- [x] Create SafetyConfig dataclass
- [x] Implement SafetyLogger for monitoring
- [x] Write tests for safety logger
- [x] Add configurable trust levels
- [x] Write tests for trust configuration
- [x] Create safety metrics collector
- [x] Write tests for metrics collection

### Safety Integration
- [x] Create optional safety middleware
- [x] Write tests for middleware
- [x] Add safety logging directory structure
- [x] Implement log rotation and cleanup

### Integration Tests  
- [x] Create tests/integration/test_phase5_safety_framework.py
- [x] Implement test_research_goal_logging
- [x] Implement test_hypothesis_monitoring
- [x] Implement test_trust_level_configuration
- [x] Implement test_safety_logger_disable
- [x] Implement test_pattern_report_generation
- [x] Implement test_audit_trail_creation
- [x] Implement test_safety_metrics_collection
- [x] Implement test_log_rotation (may_fail)
- [x] Implement test_performance_impact (may_fail)

## Phase 6: LLM Abstraction Layer

### Provider-Agnostic Interface
- [x] Create base LLMProvider abstract class
- [x] Define standard request/response formats
- [x] Write tests for abstraction interface
- [x] Implement request validation
- [x] Write tests for request validation

### Mock Provider Implementation
- [x] Create MockLLMProvider for testing
- [x] Implement configurable mock responses
- [x] Write tests for mock provider
- [x] Add response delay simulation
- [x] Write tests for async behavior

### Core Abstraction Features
- [x] Implement rate limiting logic
- [x] Write tests for rate limiting
- [x] Add model capability tracking
- [x] Write tests for capability management
- [x] Implement context window management
- [x] Write tests for context handling
- [x] Add provider-agnostic error handling
- [x] Write tests for error scenarios

### Phase 6 Integration Tests
- [x] Create tests/integration/test_phase6_llm_abstraction.py
- [x] Implement test_llm_abstraction_interface
- [x] Implement test_rate_limiting
- [x] Implement test_model_capability_tracking
- [x] Implement test_context_management
- [x] Implement test_provider_failover
- [x] Implement test_request_transformation
- [x] Implement test_smart_context_truncation (may_fail)
- [x] Implement test_llm_response_caching (may_fail)

## Phase 7: BAML Infrastructure Setup

### BAML Schemas (Data Models)
- [x] Set up baml_src directory structure
- [x] Create models.baml with core data types
- [x] Create BAML schema for Hypothesis
- [x] Create BAML schema for Review
- [x] Create BAML schema for SafetyCheck
- [ ] Create BAML schema for Task
- [ ] Create BAML schema for AgentRequest/Response
- [x] Write unit tests for Hypothesis schema
- [x] Write unit tests for Review schema
- [x] Write unit tests for SafetyCheck schema

### BAML Configuration
- [x] Create clients.baml with mock configuration
- [ ] Add test client configurations
- [ ] Set up environment variable mappings
- [ ] Configure retry policies in BAML
- [ ] Add timeout configurations

### BAML Functions
- [ ] Create functions.baml file
- [ ] Define GenerateHypothesis function
- [ ] Define EvaluateHypothesis function
- [ ] Define PerformSafetyCheck function
- [ ] Define CompareHypotheses function
- [ ] Write BAML test blocks for each function

### BAML Client Generation
- [ ] Install BAML CLI tools
- [ ] Generate Python clients from BAML
- [ ] Create Python wrapper for BAML clients
- [ ] Write tests for generated clients
- [ ] Integrate with LLM abstraction layer

### Phase 7 Integration Tests
- [ ] Create tests/integration/test_phase7_baml_infrastructure.py
- [ ] Implement test_baml_schema_compilation
- [ ] Implement test_baml_client_connectivity
- [ ] Implement test_baml_mock_responses
- [ ] Implement test_real_llm_calls (may_fail)

## Phase 8: Argo Gateway Integration

### Argo Proxy Setup
- [ ] Install argo-proxy package (`pip install argo-proxy`)
- [ ] Run initial configuration wizard
- [ ] Create startup helper script
- [ ] Test connectivity to Argo endpoints
- [ ] Verify model access (gpt4o, gpt3.5-turbo, claude-opus-4, gemini-2.5-pro)
- [ ] Create .env.example with proxy configuration
- [ ] Document Argo setup process in README

### Argo Provider Implementation
- [ ] Create ArgoLLMProvider class (implements LLMProvider)
- [ ] Implement model mapping (logical → Argo names)
- [ ] Add authentication header handling
- [ ] Write tests for Argo provider
- [ ] Implement Argo-specific error handling
- [ ] Write tests for error scenarios

### Model Routing and Selection
- [ ] Implement model selection logic
- [ ] Add cost tracking per model
- [ ] Create routing rules based on task type
- [ ] Write tests for model routing
- [ ] Implement usage monitoring
- [ ] Write tests for cost tracking

### Reliability Features
- [ ] Implement circuit breaker pattern
- [ ] Add failover to alternate models
- [ ] Create request queuing during outages
- [ ] Write tests for reliability features
- [ ] Add health check monitoring
- [ ] Write tests for failover scenarios

### Integration with Abstraction Layer
- [ ] Register ArgoProvider with abstraction layer
- [ ] Map Argo models to capability matrix
- [ ] Configure rate limits per model
- [ ] Write integration tests
- [ ] Test end-to-end LLM calls via Argo

### Phase 8 Integration Tests
- [ ] Create tests/integration/test_phase8_argo_gateway.py
- [ ] Implement test_argo_connectivity
- [ ] Implement test_model_routing
- [ ] Implement test_failover_behavior
- [ ] Implement test_cost_tracking
- [ ] Implement test_circuit_breaker
- [ ] Implement test_request_queuing
- [ ] Implement test_concurrent_requests
- [ ] Implement test_proxy_failover (may_fail)
- [ ] Implement test_rate_limiting (may_fail)

## Phase 9: Supervisor Agent

### Agent Structure
- [ ] Create SupervisorAgent class
- [ ] Implement agent initialization
- [ ] Write tests for initialization

### Core Functions
- [ ] Implement task distribution logic
- [ ] Write tests for task distribution
- [ ] Add resource allocation methods
- [ ] Write tests for resource allocation
- [ ] Implement progress monitoring
- [ ] Write tests for progress monitoring

### Advanced Features
- [ ] Add adaptive agent weighting
- [ ] Write tests for adaptive weighting
- [ ] Implement termination detection
- [ ] Write tests for termination
- [ ] Add recovery mechanisms
- [ ] Write tests for recovery

### Phase 9 Integration Tests
- [ ] Create tests/integration/test_phase9_supervisor_agent.py
- [ ] Implement test_supervisor_initialization
- [ ] Implement test_task_distribution_logic
- [ ] Implement test_resource_allocation
- [ ] Implement test_progress_monitoring
- [ ] Implement test_adaptive_agent_weighting
- [ ] Implement test_termination_detection
- [ ] Implement test_supervisor_recovery
- [ ] Implement test_multi_agent_coordination (may_fail)
- [ ] Implement test_supervisor_performance (may_fail)

## Phase 10: Generation Agent

### Agent Structure
- [ ] Create GenerationAgent class
- [ ] Implement agent initialization
- [ ] Write tests for initialization

### Generation Strategies
- [ ] Implement literature-based generation
- [ ] Write tests for literature generation
- [ ] Add simulated debate generation
- [ ] Write tests for debate generation
- [ ] Implement assumption-based generation
- [ ] Write tests for assumption generation
- [ ] Add feedback-based generation
- [ ] Write tests for feedback generation

### Integration
- [ ] Connect to web search interface
- [ ] Write integration tests
- [ ] Add safety checks to generation
- [ ] Write tests for safety integration

### Phase 10 Integration Tests
- [ ] Create tests/integration/test_phase10_generation_agent.py
- [ ] Implement test_generation_agent_initialization
- [ ] Implement test_literature_based_generation
- [ ] Implement test_simulated_debate_generation
- [ ] Implement test_assumption_based_generation
- [ ] Implement test_feedback_based_generation
- [ ] Implement test_generation_safety_checks
- [ ] Implement test_web_search_integration
- [ ] Implement test_hypothesis_diversity (may_fail)
- [ ] Implement test_generation_creativity_metrics (may_fail)

## Phase 11: Reflection Agent

### Agent Structure
- [ ] Create ReflectionAgent class
- [ ] Implement agent initialization
- [ ] Write tests for initialization

### Review Types
- [ ] Implement initial review
- [ ] Write tests for initial review
- [ ] Add full review with literature
- [ ] Write tests for full review
- [ ] Implement deep verification
- [ ] Write tests for deep verification
- [ ] Add observation review
- [ ] Write tests for observation review
- [ ] Implement simulation review
- [ ] Write tests for simulation review
- [ ] Add tournament review
- [ ] Write tests for tournament review

### Phase 11 Integration Tests
- [ ] Create tests/integration/test_phase11_reflection_agent.py
- [ ] Implement test_reflection_agent_initialization
- [ ] Implement test_initial_review_process
- [ ] Implement test_full_review_with_literature
- [ ] Implement test_deep_verification_review
- [ ] Implement test_observation_review
- [ ] Implement test_simulation_review
- [ ] Implement test_tournament_review
- [ ] Implement test_review_consistency (may_fail)
- [ ] Implement test_review_quality_metrics (may_fail)

## Phase 12: Ranking Agent

### Agent Structure
- [ ] Create RankingAgent class
- [ ] Implement Elo rating system
- [ ] Write tests for Elo calculations

### Tournament System
- [ ] Implement pairwise comparison
- [ ] Write tests for comparisons
- [ ] Add multi-turn debates
- [ ] Write tests for debates
- [ ] Implement convergence detection
- [ ] Write tests for convergence

### Phase 12 Integration Tests
- [ ] Create tests/integration/test_phase12_ranking_agent.py
- [ ] Implement test_ranking_agent_initialization
- [ ] Implement test_elo_rating_calculations
- [ ] Implement test_pairwise_comparison
- [ ] Implement test_multi_turn_debates
- [ ] Implement test_convergence_detection
- [ ] Implement test_tournament_fairness
- [ ] Implement test_ranking_stability
- [ ] Implement test_large_scale_tournament (may_fail)
- [ ] Implement test_ranking_performance (may_fail)

## Phase 13: Evolution Agent

### Agent Structure
- [ ] Create EvolutionAgent class
- [ ] Write tests for initialization

### Evolution Strategies
- [ ] Implement enhancement strategy
- [ ] Write tests for enhancement
- [ ] Add combination strategy
- [ ] Write tests for combination
- [ ] Implement simplification strategy
- [ ] Write tests for simplification
- [ ] Add paradigm shift strategy
- [ ] Write tests for paradigm shifts

### Phase 13 Integration Tests
- [ ] Create tests/integration/test_phase13_evolution_agent.py
- [ ] Implement test_evolution_agent_initialization
- [ ] Implement test_enhancement_strategy
- [ ] Implement test_combination_strategy
- [ ] Implement test_simplification_strategy
- [ ] Implement test_paradigm_shift_strategy
- [ ] Implement test_evolution_constraints
- [ ] Implement test_hypothesis_lineage_tracking
- [ ] Implement test_evolution_diversity (may_fail)
- [ ] Implement test_evolution_quality_metrics (may_fail)

## Phase 14: Proximity Agent

### Agent Structure
- [ ] Create ProximityAgent class
- [ ] Write tests for initialization

### Similarity Calculation
- [ ] Implement semantic similarity
- [ ] Write tests for similarity
- [ ] Add clustering logic
- [ ] Write tests for clustering

### Phase 14 Integration Tests
- [ ] Create tests/integration/test_phase14_proximity_agent.py
- [ ] Implement test_proximity_agent_initialization
- [ ] Implement test_semantic_similarity_calculation
- [ ] Implement test_hypothesis_clustering
- [ ] Implement test_cluster_visualization
- [ ] Implement test_similarity_threshold_tuning
- [ ] Implement test_large_scale_clustering (may_fail)
- [ ] Implement test_clustering_performance (may_fail)

## Phase 15: Meta-Review Agent

### Agent Structure
- [ ] Create MetaReviewAgent class
- [ ] Write tests for initialization

### Synthesis Functions
- [ ] Implement pattern extraction
- [ ] Write tests for patterns
- [ ] Add feedback generation
- [ ] Write tests for feedback
- [ ] Implement research overview
- [ ] Write tests for overview

### Phase 15 Integration Tests
- [ ] Create tests/integration/test_phase15_meta_review_agent.py
- [ ] Implement test_meta_review_initialization
- [ ] Implement test_pattern_extraction
- [ ] Implement test_feedback_generation
- [ ] Implement test_research_overview_synthesis
- [ ] Implement test_meta_review_safety_audit
- [ ] Implement test_cross_agent_pattern_detection
- [ ] Implement test_meta_review_quality (may_fail)
- [ ] Implement test_synthesis_performance (may_fail)

## Phase 16: Natural Language Interface

### CLI Interface
- [ ] Create main CLI entry point
- [ ] Add command parsing
- [ ] Write tests for CLI parsing
- [ ] Implement interactive mode
- [ ] Write tests for interactive mode

### Input Processing
- [ ] Add research goal parsing
- [ ] Write tests for goal parsing
- [ ] Implement constraint handling
- [ ] Write tests for constraints

### Phase 16 Integration Tests
- [ ] Create tests/integration/test_phase16_natural_language_interface.py
- [ ] Implement test_cli_entry_point
- [ ] Implement test_command_parsing
- [ ] Implement test_interactive_mode
- [ ] Implement test_research_goal_parsing
- [ ] Implement test_constraint_handling
- [ ] Implement test_user_feedback_loop
- [ ] Implement test_natural_language_understanding (may_fail)
- [ ] Implement test_interface_responsiveness (may_fail)

## Phase 17: Integration and Polish

### System Integration
- [ ] Create full system integration tests
- [ ] Add end-to-end workflow tests
- [ ] Implement monitoring dashboard
- [ ] Add performance benchmarks

### Output Formatting
- [ ] Implement NIH Specific Aims formatter
- [ ] Write tests for formatting
- [ ] Add export functionality
- [ ] Write tests for export

### Documentation
- [ ] Create user documentation
- [ ] Add API documentation
- [ ] Write deployment guide
- [ ] Create example workflows

### Phase 17 Integration Tests
- [ ] Create tests/integration/test_phase17_system_integration.py
- [ ] Implement test_full_system_workflow
- [ ] Implement test_end_to_end_hypothesis_generation
- [ ] Implement test_monitoring_dashboard
- [ ] Implement test_nih_specific_aims_formatter
- [ ] Implement test_export_functionality
- [ ] Implement test_performance_benchmarks
- [ ] Implement test_system_resilience (may_fail)
- [ ] Implement test_scalability_limits (may_fail)

## Phase 18: Final Validation

- [ ] Run full system tests
- [ ] Verify ≥80% test coverage
- [ ] Performance testing
- [ ] Safety validation
- [ ] User acceptance testing

### Phase 18 Integration Tests
- [ ] Create tests/integration/test_phase18_final_validation.py
- [ ] Implement test_full_system_test_suite
- [ ] Implement test_code_coverage_validation
- [ ] Implement test_performance_validation
- [ ] Implement test_safety_validation
- [ ] Implement test_user_acceptance_scenarios
- [ ] Implement test_deployment_readiness
- [ ] Implement test_stress_testing (may_fail)
- [ ] Implement test_production_simulation (may_fail)

## Notes

- Each checkbox represents an atomic, testable unit
- Tests must be written BEFORE implementation
- All tests must pass before moving to next item
- Coverage must remain ≥80% throughout
- Follow specs exactly for behavior
- Use BAML for all LLM interactions
- Implement safety checks at every level