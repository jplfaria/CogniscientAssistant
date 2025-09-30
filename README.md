# AI Co-Scientist

An autonomous multi-agent system for scientific hypothesis generation, research automation, and knowledge synthesis.

## 🔬 What It Does

The AI Co-Scientist accelerates scientific discovery by:
- **Generating Novel Hypotheses** - Creates research hypotheses from scientific literature and data
- **Automating Literature Review** - Searches and synthesizes relevant research papers
- **Multi-Perspective Analysis** - Uses specialized agents to evaluate ideas from different angles
- **Research Task Management** - Decomposes complex research goals into executable tasks
- **Quality Assurance** - Implements multi-layer validation and safety checks

## 🚀 Key Capabilities

### Multi-Agent Architecture
- **Supervisor Agent** - Orchestrates research workflows and resource allocation
- **Generation Agent** - Creates hypotheses using multiple strategies (literature-based, debate, etc.)
- **Reflection Agent** - Reviews and critiques generated hypotheses *(in development)*
- **Ranking Agent** - Evaluates and prioritizes research directions *(in development)*
- **Evolution Agent** - Enhances and refines promising hypotheses *(in development)*
- **Meta-Review Agent** - Synthesizes insights across multiple research threads *(in development)*

### Research Automation Features
- Web search integration for latest research
- Citation tracking and management
- Context memory for maintaining research state
- Natural language interface for intuitive interaction
- Export capabilities for research outputs

## 📦 Installation

### Prerequisites
- Python 3.11 or higher
- Access to LLM services (via Argo Gateway)

### Modern Development Setup (Recommended)

We use UV package manager for fast, reliable dependency management:

```bash
# Clone the repository
git clone https://github.com/yourusername/cogniscient-assistant.git
cd cogniscient-assistant

# Install UV package manager (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create and activate virtual environment
uv venv --python 3.11 .venv
source .venv/bin/activate  # On macOS/Linux
# OR on Windows: .venv\Scripts\activate

# Install all dependencies (development included)
uv pip install -e ".[dev]"

# Configure environment
cp .env.example .env
# Edit .env with your configuration
```

### Alternative Setup (Traditional pip)

```bash
# Clone and setup
git clone https://github.com/yourusername/cogniscient-assistant.git
cd cogniscient-assistant

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Configure environment
cp .env.example .env
```

### Argo Gateway Configuration

The system uses Argo Gateway for LLM access:

```bash
# Install argo-proxy (if not already installed)
pip install argo-proxy==2.7.7

# Start the proxy (requires VPN connection)
./scripts/argo-proxy.sh start

# Verify connection
./scripts/argo-proxy.sh status
```

For detailed setup, see [Argo Gateway Setup Guide](docs/argo-gateway-complete-guide.md).

## 🧪 Development Features

### Enhanced BAML Integration (v0.209.0)
- **6x Performance Improvement**: Faster debugging and trace uploads
- **Advanced Error Handling**: Enhanced debugging with fallback history
- **Multi-Model Support**: o3, GPT-4, Claude Opus 4.1, Gemini 2.5 Pro, Llama 4
- **Type-Safe LLM Interactions**: All AI interactions through structured BAML functions

### Parallel Testing Framework
- **4x+ Faster Testing**: Run 240 tests in 20 minutes vs 48 minutes sequential
- **Development Acceleration**: Rapid iteration during agent development
- **Comprehensive Coverage**: Unit, integration, and real LLM testing

```bash
# Run parallel tests (much faster)
pytest tests/integration/test_baml_parallel.py -v

# Traditional sequential tests
pytest tests/integration/ -v
```

See [Parallel Testing Guide](docs/baml/PARALLEL_TESTING_GUIDE.md) for detailed examples and benchmarks.

### Virtual Environment Benefits
- **Isolated Dependencies**: No conflicts with system packages
- **Reproducible Builds**: Exact dependency versions in `requirements-lock.txt`
- **Easy Cleanup**: Remove `.venv` directory to reset completely
- **Development Speed**: UV provides 10-100x faster package operations

## 💡 Usage

### Basic Research Session

```python
from src.agents.supervisor import SupervisorAgent
from src.core.models import ResearchGoal

# Initialize the supervisor
supervisor = SupervisorAgent()

# Define your research goal
goal = ResearchGoal(
    description="Investigate novel approaches to quantum error correction",
    constraints=["Focus on topological methods", "Consider near-term feasibility"]
)

# Start the research process
results = await supervisor.conduct_research(goal)

# Results include generated hypotheses, rankings, and synthesis
print(results.top_hypotheses)
print(results.literature_review)
print(results.recommendations)
```

### Command Line Interface

```bash
# Start interactive research session
python -m src.cli.research_assistant

# Generate hypotheses from a research question
python -m src.cli.generate_hypotheses "How can we improve battery energy density?"

# Analyze existing hypothesis
python -m src.cli.analyze_hypothesis hypothesis.json
```

### Development Workflow

```bash
# Activate virtual environment (always do this first)
source .venv/bin/activate

# Regenerate BAML client after changes
baml generate

# Run fast parallel tests
pytest tests/integration/test_baml_parallel.py -v

# Run full test suite
make test  # or pytest tests/ -v

# Update dependencies
uv pip install new_package
uv pip freeze > requirements-lock.txt
```

## 🛡️ Safety and Ethics

The AI Co-Scientist implements comprehensive safety measures:
- Multi-layer safety checks on all generated content
- Ethical review of research directions
- Configurable trust levels for different research domains
- Audit logging of all agent decisions (`.aicoscientist/safety_logs/`)
- Human-in-the-loop intervention points

## 🏗️ Architecture

The system uses:
- **BAML 0.209.0** for structured LLM interactions with enhanced performance
- **Async Python** for concurrent agent operations
- **Task Queue** for workflow orchestration
- **Context Memory** for maintaining research state
- **Circuit Breakers** for reliability
- **Virtual Environments** for isolated, reproducible development

### Technical Stack
- **Python 3.11+**: Core runtime with async/await
- **UV Package Manager**: Fast dependency management (10-100x speedup)
- **BAML-py 0.209.0**: Type-safe LLM integration
- **Argo Proxy 2.7.7**: Gateway for multiple LLM providers
- **pytest + asyncio**: Comprehensive testing with parallel execution

## 📚 Documentation

### User Documentation
- [Environment Setup Guide](docs/environment-setup.md) - Virtual environment and UV setup
- [Argo Gateway Guide](docs/argo-gateway-complete-guide.md) - LLM access configuration
- [User Guide](docs/USER_GUIDE.md) - Complete usage documentation
- [Safety Framework](docs/safety-framework.md) - Safety and ethics documentation

### Development Documentation
- [Development Guide](DEVELOPMENT.md) - Development setup and workflows
- [API Reference](docs/API_REFERENCE.md) - Detailed API documentation
- [BAML Testing Strategy](docs/baml/BAML_TESTING_STRATEGY.md) - BAML testing patterns
- [Parallel Testing Guide](docs/baml/PARALLEL_TESTING_GUIDE.md) - High-performance testing
- [Implementation Plan](IMPLEMENTATION_PLAN.md) - Current development roadmap

### Specifications
- [Agent Specifications](specs/) - Behavioral specifications for each agent
- [Integration Testing Plan](INTEGRATION_TESTING_PLAN.md) - Testing strategy

## 🧪 Current Status

**🚧 In Active Development**

The AI Co-Scientist is currently in development with core infrastructure and several agents operational.

### ✅ What's Working Now
- **Core Infrastructure**: Task queue, context memory, safety framework
- **BAML Integration**: 8 core functions with type-safe LLM interactions
- **Agent Foundation**: Supervisor and Generation agents fully operational
- **Development Workflow**: Virtual environments, parallel testing, enhanced debugging
- **Multi-Model Support**: Integration with o3, GPT-4, Claude, Gemini models

### 🔄 In Development (Phases 11-15)
- **Reflection Agent**: Hypothesis review and critique (Phase 11)
- **Ranking Agent**: Tournament-based evaluation (Phase 12)
- **Evolution Agent**: Hypothesis enhancement and refinement (Phase 13)
- **Proximity Agent**: Similarity analysis and clustering (Phase 14)
- **Meta-Review Agent**: Research synthesis and insights (Phase 15)

### 🔮 Future Enhancements
- **Streaming Integration**: Real-time hypothesis generation
- **AWS Bedrock Support**: Additional model capabilities
- **Advanced Optimizations**: Production-scale performance improvements

## 🧪 Testing

### Quick Testing
```bash
# Activate environment
source .venv/bin/activate

# Fast unit tests
pytest tests/unit/ -v

# Parallel integration tests (recommended)
pytest tests/integration/test_baml_parallel.py -v

# Test with real LLMs (requires API access)
pytest tests/integration/ --real-llm -v
```

### Performance Benchmarks
- **Sequential Testing**: ~120 seconds for 12 hypothesis generations
- **Parallel Testing**: ~12 seconds for 12 hypothesis generations (10x speedup)
- **Development Cycles**: 4x+ faster iteration with parallel testing

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup
1. Follow installation instructions above
2. Activate virtual environment: `source .venv/bin/activate`
3. Install development dependencies: `uv pip install -e ".[dev]"`
4. Run tests to verify setup: `pytest tests/unit/ -v`

For implementation details, see [DEVELOPMENT.md](DEVELOPMENT.md) and [Implementation Plan](IMPLEMENTATION_PLAN.md).

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

This project builds on research from:
- The AI Scientist paper (Lu et al., 2024)
- BAML framework for structured LLM interactions
- UV package manager for fast Python dependency management
- The broader AI research automation community

## 📧 Contact

For questions or collaboration opportunities, please open an issue or contact the maintainers.

---

**Note**: This is a research prototype. Always validate generated hypotheses and research directions with domain experts before proceeding with experimental work.

**Virtual Environment Reminder**: Always activate your virtual environment (`source .venv/bin/activate`) before development work.