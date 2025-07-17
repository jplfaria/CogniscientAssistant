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
- [ ] Add queue recovery on startup
- [ ] Write tests for recovery

## Phase 4: Context Memory Implementation

### Basic Storage
- [ ] Create ContextMemory class structure
- [ ] Implement file-based storage backend
- [ ] Write tests for storage operations
- [ ] Add key-value store methods
- [ ] Write tests for key-value operations

### Hierarchical Organization
- [ ] Implement iteration tracking
- [ ] Write tests for iteration management
- [ ] Add checkpoint functionality
- [ ] Write tests for checkpoints
- [ ] Implement aggregate storage
- [ ] Write tests for aggregates

### Advanced Features
- [ ] Add conflict resolution logic
- [ ] Write tests for conflict resolution
- [ ] Implement temporal guarantees
- [ ] Write tests for temporal operations
- [ ] Add memory cleanup/archival
- [ ] Write tests for cleanup

## Phase 5: Safety Framework

### Safety Models
- [ ] Create SafetyLevel enum
- [ ] Create SafetyCheck dataclass
- [ ] Write tests for safety models

### Safety Evaluators
- [ ] Implement research goal safety evaluator
- [ ] Write tests for goal evaluation
- [ ] Implement hypothesis safety evaluator
- [ ] Write tests for hypothesis evaluation
- [ ] Add pattern monitoring system
- [ ] Write tests for pattern monitoring
- [ ] Implement meta-review safety checks
- [ ] Write tests for meta-review safety

### Safety Integration
- [ ] Create safety middleware for agents
- [ ] Write tests for middleware
- [ ] Add safety logging system
- [ ] Write tests for safety logs

## Phase 6: LLM Abstraction Layer

### BAML Setup
- [ ] Create BAML schema for Hypothesis
- [ ] Create BAML schema for Review
- [ ] Create BAML schema for SafetyCheck
- [ ] Set up BAML client configuration

### LLM Interface
- [ ] Create base LLM abstraction class
- [ ] Write tests for abstraction interface
- [ ] Implement BAML-based LLM client
- [ ] Write tests for BAML client
- [ ] Add rate limiting logic
- [ ] Write tests for rate limiting
- [ ] Implement failover mechanism
- [ ] Write tests for failover

## Phase 7: BAML Infrastructure Setup

### Argo Gateway Setup
- [ ] Install argo-proxy package (`pip install argo-proxy`)
- [ ] Run initial configuration wizard
- [ ] Create startup helper script
- [ ] Test connectivity to Argo endpoints
- [ ] Verify model access (gpt4o, gpto3mini, claudeopus4, gemini25pro)
- [ ] Create .env.example with proxy configuration
- [ ] Document setup process in README

### Core BAML Configuration
- [ ] Set up baml_src directory structure
- [ ] Create clients.baml with Argo Gateway configuration
- [ ] Write tests for client connectivity
- [ ] Create generators.baml with retry logic
- [ ] Add environment variable configuration

### Agent BAML Schemas
- [ ] Create models.baml with core data types
- [ ] Define Hypothesis schema in BAML
- [ ] Define Review schema in BAML
- [ ] Define Task schema in BAML
- [ ] Write BAML tests for schema validation

### Base Agent Functions
- [ ] Create supervisor.baml with orchestration functions
- [ ] Create generation.baml with hypothesis generation
- [ ] Create reflection.baml with review functions
- [ ] Create ranking.baml with tournament functions
- [ ] Write BAML test blocks for each function

### Thread and Event System
- [ ] Implement thread-based state management
- [ ] Create event serialization format
- [ ] Write tests for thread persistence
- [ ] Add event replay functionality
- [ ] Write tests for event replay

### Integration Layer
- [ ] Create Python BAML wrapper functions
- [ ] Write integration tests with TaskQueue
- [ ] Add error handling and retries
- [ ] Write tests for error scenarios
- [ ] Implement logging and monitoring

## Phase 8: Supervisor Agent

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

## Phase 9: Generation Agent

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

## Phase 10: Reflection Agent

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

## Phase 11: Ranking Agent

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

## Phase 12: Evolution Agent

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

## Phase 13: Proximity Agent

### Agent Structure
- [ ] Create ProximityAgent class
- [ ] Write tests for initialization

### Similarity Calculation
- [ ] Implement semantic similarity
- [ ] Write tests for similarity
- [ ] Add clustering logic
- [ ] Write tests for clustering

## Phase 14: Meta-Review Agent

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

## Phase 15: Natural Language Interface

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

## Phase 16: Integration and Polish

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

## Phase 17: Final Validation

- [ ] Run full system tests
- [ ] Verify ≥80% test coverage
- [ ] Performance testing
- [ ] Safety validation
- [ ] User acceptance testing

## Notes

- Each checkbox represents an atomic, testable unit
- Tests must be written BEFORE implementation
- All tests must pass before moving to next item
- Coverage must remain ≥80% throughout
- Follow specs exactly for behavior
- Use BAML for all LLM interactions
- Implement safety checks at every level