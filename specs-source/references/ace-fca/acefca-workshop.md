# Workshop: Advanced Context Engineering for Coding Agents

> Downloaded from: https://gist.githubusercontent.com/dexhorthy/c5d2113621d17178b29ae4c31028bdc2/raw/8cbd263be9effb2ad5299ab4f946af0d0904045b/acefca-workshop.md
> Date: September 19, 2025

This is a workshop to learn how to use some advanced context engineering techniques with Claude Code.

Watch the video: https://hlyr.dev/ace

More links and info: https://github.com/ai-that-works/ai-that-works/tree/main/2025-08-05-advanced-context-engineering-for-coding-agents

## Pre-Requisites

- Claude Code account and logged in on your workstation
- A way to view/edit markdown files (Cursor, VSCode, vim, go-grip, etc)
- A chosen issue to work on, ideally on an OSS repo that you have some familiarity with / understanding of

**COST NOTE** - we recommend using Opus for this workshop as its the best at reliably understanding and working in large codebases.

## Objectives / Outcomes

- Familiarity with managing Claude Code subagents and commands
- Understanding of advanced context engineering patterns
- Practical experience with modular prompt systems
- Ability to systematically approach complex coding issues

## Workshop Outline

This workshop follows a systematic approach to using AI for coding assistance with advanced context engineering techniques.

## Step-by-step Guide

### 1. Choose an Issue to Work On

You should pick an issue to work on. It should be somewhat small just to help you focus on learning the system.

You can use these techniques in your own private repos, but if you want help/etc I recommend using an open source repo that you have some familiarity with / understanding of.

A good bar to set, is to pick the OSS repo for a tool you use often enough that if you read a bug ticket, you can understand and reproduce the issue yourself.

### 2. Clone the Repository

Whatever issue you choose to work on, you will need to clone the repository to your workstation. This will be your "working repository"

### 3. Clone the HumanLayer Repo

To get the example prompts and agents, you will need to clone the humanlayer repo.

This should be cloned at the same level as your working repository (i.e. DO NOT clone it inside your working repository)

```bash
git clone https://github.com/humanlayer/humanlayer.git
```

### 4. Borrow the Prompts

Copy the prompts and agents from humanlayer to your home directory.

```bash
mkdir -p ~/.claude/commands
cp -r humanlayer/.claude/commands/* ~/.claude/commands/
```

### 5. Research Phase

Before implementing anything, use the research commands to understand the codebase:

```bash
# Use Claude Code to research the codebase structure
claude research-codebase
```

**Key Research Activities:**
- Understand the overall architecture
- Identify key components and their relationships
- Map out the information flows
- Understand the specific issue you're trying to solve

### 6. Planning Phase

Create a detailed implementation plan:

```bash
# Use Claude Code to create an implementation plan
claude create-plan
```

**Planning Best Practices:**
- Break down the problem into small, manageable steps
- Identify dependencies between steps
- Define success criteria for each step
- Consider potential risks and mitigation strategies

### 7. Implementation Phase

Execute your plan systematically:

```bash
# Use Claude Code to implement each step
claude implement-step
```

**Implementation Guidelines:**
- Follow your plan step-by-step
- Validate each step before proceeding
- Adjust your approach based on what you learn
- Keep your context window optimized

### 8. Review and Commit

Review your changes and create a commit:

```bash
# Review changes
claude review-changes

# Create commit message
claude create-commit
```

## Advanced Context Engineering Patterns

### Modular Prompt System

The workshop uses a modular approach to prompts and agents:

- **Specialized commands** for different phases (research, planning, implementation)
- **Context-aware prompts** that adapt to the current situation
- **Reusable patterns** that can be applied across different projects

### Staged Workflow

The workflow is broken into distinct stages:

1. **Research codebase** - Understand the problem domain
2. **Create strategic plan** - Develop systematic approach
3. **Implement solution** - Execute plan with validation
4. **Review and commit** - Ensure quality and create records

### Flexible Command-Based Interaction

- **Granular command control** for precise AI direction
- **Context preservation** across command invocations
- **Iterative refinement** of understanding and approach

### Subagent Coordination

- **Specialized subagents** for different types of tasks
- **Coordinated workflow** across multiple AI agents
- **Consistent context sharing** between agents

## Tools and Methodologies

### Claude Code AI
- **Primary interface** for AI-assisted coding
- **Subagent management** for complex workflows
- **Context window optimization** for large codebases

### Custom Command Prompts
- **Pre-built commands** for common workflows
- **Customizable prompts** for specific use cases
- **Template-based approach** for consistency

### GitHub-Based Workflow
- **Standard git operations** integrated with AI assistance
- **Pull request creation** with AI-generated descriptions
- **Issue tracking** and resolution workflows

## Coding Agent Improvements

### Contextual Understanding
- **Deep codebase analysis** before making changes
- **Architecture-aware implementations** that fit existing patterns
- **Cross-component impact analysis** for complex changes

### Systematic Issue Resolution
- **Structured problem-solving approach** for consistent results
- **Evidence-based decision making** using codebase analysis
- **Incremental validation** to catch issues early

### Granular Command Control
- **Precise AI direction** through specialized commands
- **Context-sensitive operations** based on current state
- **Flexible workflow adaptation** as understanding evolves

### Reproducible Development Process
- **Documented workflows** that can be repeated
- **Consistent quality standards** across different projects
- **Knowledge capture** for future reference

## Real-world Examples

### Open-source Repository Debugging
- **Complex bug identification** in unfamiliar codebases
- **Cross-file impact analysis** for comprehensive fixes
- **Integration testing** to validate solutions

### Collaborative Development Workflow
- **Team-friendly documentation** of changes and rationale
- **Review-ready pull requests** with comprehensive descriptions
- **Knowledge sharing** through documented decision processes

## Success Metrics

### Ability to Navigate Complex Codebases
- **Rapid understanding** of large, unfamiliar codebases
- **Effective information filtering** to focus on relevant components
- **Accurate mental model construction** of system architecture

### Effective Issue Resolution
- **Comprehensive problem analysis** before implementing solutions
- **Appropriate solution scoping** that addresses root causes
- **Quality implementation** that follows project conventions

### Improved AI-Human Collaboration
- **Clear communication** between human intent and AI execution
- **Effective context management** for sustained collaboration
- **Productive iteration** on complex problems

## Key Practical Techniques

### Modular Prompt Engineering
- **Component-based prompts** for different workflow stages
- **Reusable prompt patterns** across projects
- **Context-aware prompt selection** based on current needs

### Systematic Research and Planning
- **Structured codebase analysis** before implementation
- **Evidence-based planning** using discovered information
- **Risk-aware implementation** with mitigation strategies

### Granular AI Command Structure
- **Precise control** over AI operations
- **Context preservation** across command sequences
- **Flexible workflow adaptation** based on discoveries

### Reproducible Development Workflow
- **Documented processes** for consistent results
- **Standardized quality gates** for reliable outcomes
- **Knowledge capture** for continuous improvement

## Recommended Best Practices

### Use Familiar Repositories
- **Start with codebases** you have some understanding of
- **Choose appropriate issue scope** for learning objectives
- **Leverage existing knowledge** to validate AI understanding

### Start with Small, Manageable Issues
- **Focus on learning** the workflow rather than complex problems
- **Build confidence** with successful small implementations
- **Establish patterns** that can scale to larger problems

### Review and Customize Prompts
- **Understand the provided prompts** before using them
- **Adapt prompts** to your specific use case and preferences
- **Iterate on prompt effectiveness** based on results

### Leverage Specialized Subagents
- **Use appropriate subagents** for different types of tasks
- **Understand subagent capabilities** and limitations
- **Coordinate subagent workflows** for complex operations

---

*This workshop provides hands-on experience with cutting-edge AI-assisted development techniques, focusing on practical skills that can immediately improve development productivity and code quality.*