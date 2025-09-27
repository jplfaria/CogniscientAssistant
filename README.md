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
- **Reflection Agent** - Reviews and critiques generated hypotheses
- **Ranking Agent** - Evaluates and prioritizes research directions
- **Evolution Agent** - Enhances and refines promising hypotheses
- **Meta-Review Agent** - Synthesizes insights across multiple research threads

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

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/cogniscient-assistant.git
cd cogniscient-assistant

# Set up development environment (uses uv for fast package management)
./scripts/development/setup-dev.sh

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Activate virtual environment
source .venv/bin/activate
```

### Argo Gateway Configuration

The system uses Argo Gateway for LLM access:

```bash
# Install argo-proxy
pip install argo-proxy

# Start the proxy (requires VPN connection)
./scripts/argo-proxy.sh start

# Verify connection
./scripts/argo-proxy.sh status
```

For detailed setup, see [Argo Gateway Setup Guide](docs/argo-gateway-complete-guide.md).

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

## 🛡️ Safety and Ethics

The AI Co-Scientist implements comprehensive safety measures:
- Multi-layer safety checks on all generated content
- Ethical review of research directions
- Configurable trust levels for different research domains
- Audit logging of all agent decisions
- Human-in-the-loop intervention points

## 🏗️ Architecture

The system uses:
- **BAML** for structured LLM interactions
- **Async Python** for concurrent agent operations
- **Task Queue** for workflow orchestration
- **Context Memory** for maintaining research state
- **Circuit Breakers** for reliability

## 📚 Documentation

- [User Guide](docs/USER_GUIDE.md) - Complete usage documentation
- [API Reference](docs/API_REFERENCE.md) - Detailed API documentation
- [Agent Specifications](specs/) - Behavioral specifications for each agent
- [Safety Framework](docs/safety-framework.md) - Safety and ethics documentation

## 🧪 Current Status

**🚧 In Active Development**

The AI Co-Scientist is currently in development with core infrastructure and several agents operational. See our [roadmap](ROADMAP.md) for upcoming features.

### What's Working Now
- ✅ Core task queue and memory systems
- ✅ Supervisor and Generation agents
- ✅ BAML-based LLM integration
- ✅ Safety framework
- ✅ Basic hypothesis generation

### Coming Soon
- 🔄 Reflection and Ranking agents
- 🔄 Evolution and Meta-Review capabilities
- 🔄 Advanced web search integration
- 🔄 Export and visualization tools

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

For development setup and implementation details, see [DEVELOPMENT.md](DEVELOPMENT.md).

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

This project builds on research from:
- The AI Scientist paper (Lu et al., 2024)
- BAML framework for structured LLM interactions
- The broader AI research automation community

## 📧 Contact

For questions or collaboration opportunities, please open an issue or contact the maintainers.

---

**Note**: This is a research prototype. Always validate generated hypotheses and research directions with domain experts before proceeding with experimental work.