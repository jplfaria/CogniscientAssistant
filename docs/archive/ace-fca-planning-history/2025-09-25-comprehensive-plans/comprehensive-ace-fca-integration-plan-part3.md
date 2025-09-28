# Comprehensive ACE-FCA Integration Plan - Part 3
*Semantic Agent Tools and Human-like Interfaces*

## Part 3: Semantic Agent Tools

### Overview

Semantic agent tools replace generic memory access patterns with human-like semantic interfaces, making agent interactions more intuitive and context-aware. This represents a fundamental shift from technical memory operations to cognitive-inspired interactions.

### Key Principles

1. **Human-like Semantics**: Tools mirror how humans interact with information
2. **Context Awareness**: Tools understand task context and adapt behavior accordingly
3. **Cognitive Metaphors**: Research calendar, hypothesis inbox, literature library patterns
4. **Intelligent Filtering**: Automatic relevance filtering based on current task
5. **Learning Adaptation**: Tools improve based on usage patterns and effectiveness

### 1. Core Semantic Tool Framework

#### Base Semantic Tool Interface
**Location**: `src/core/semantic_tools.py`

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class SemanticQuery:
    """Represents a semantic query with context."""
    query_text: str
    task_context: str
    agent_type: str
    intent: str  # "search", "browse", "review", "analyze"
    filters: Dict[str, Any]
    temporal_scope: Optional[tuple] = None
    relevance_threshold: float = 0.3

@dataclass
class SemanticResult:
    """Result from a semantic tool operation."""
    items: List[Any]
    relevance_scores: List[float]
    context_summary: str
    metadata: Dict[str, Any]
    query_interpretation: str
    suggestions: List[str]

class SemanticTool(ABC):
    """Abstract base for semantic agent tools."""

    def __init__(self, context_memory, baml_wrapper):
        self.context_memory = context_memory
        self.baml_wrapper = baml_wrapper
        self.usage_patterns = {}
        self.effectiveness_tracker = None

    @abstractmethod
    async def semantic_operation(self, query: SemanticQuery) -> SemanticResult:
        """Perform semantic operation with human-like interface."""
        pass

    async def learn_from_usage(self, query: SemanticQuery, result: SemanticResult,
                              effectiveness: float) -> None:
        """Learn from usage patterns to improve future operations."""
        usage_key = f"{query.agent_type}_{query.intent}"
        if usage_key not in self.usage_patterns:
            self.usage_patterns[usage_key] = []

        self.usage_patterns[usage_key].append({
            'query': query,
            'result_quality': effectiveness,
            'timestamp': datetime.now(),
            'result_count': len(result.items)
        })

    async def suggest_improvements(self, query: SemanticQuery) -> List[str]:
        """Suggest query improvements based on learned patterns."""
        suggestions = []

        # Analyze similar past queries
        similar_queries = await self._find_similar_queries(query)

        for past_query, effectiveness in similar_queries:
            if effectiveness > 0.8:  # High effectiveness
                suggestions.append(
                    f"Consider filtering by '{past_query.filters}' like in previous successful searches"
                )

        return suggestions
```

#### Research Calendar Tool
**Location**: `src/agents/tools/research_calendar.py`

```python
class ResearchCalendarTool(SemanticTool):
    """Semantic interface for managing research timeline and schedules."""

    async def check_research_calendar(self, time_scope: str = "current_week") -> List[ResearchEvent]:
        """Check research calendar with natural time expressions."""
        query = SemanticQuery(
            query_text=f"research events in {time_scope}",
            task_context="timeline_planning",
            agent_type="supervisor",
            intent="browse"
        )

        # Parse natural time expressions
        time_range = await self._parse_time_scope(time_scope)

        # Retrieve relevant research events
        events = await self.context_memory.get_time_range_data(
            "research_events",
            time_range[0],
            time_range[1]
        )

        # Apply semantic filtering
        filtered_events = await self._filter_events_semantically(events, query)

        return [ResearchEvent.from_dict(event) for event in filtered_events]

    async def schedule_research_activity(self, activity_description: str,
                                       priority: str = "normal") -> ResearchEvent:
        """Schedule research activity with natural language description."""
        # Extract timing and dependencies from description
        scheduling_info = await self.baml_wrapper.extract_scheduling_info(
            activity_description,
            priority
        )

        # Create research event
        event = ResearchEvent(
            title=scheduling_info.title,
            description=activity_description,
            start_time=scheduling_info.suggested_start,
            duration=scheduling_info.estimated_duration,
            priority=priority,
            dependencies=scheduling_info.dependencies,
            resources_needed=scheduling_info.resources
        )

        # Store in calendar
        await self.context_memory.append_to_aggregate("research_events", event.to_dict())

        return event

    async def find_research_conflicts(self, proposed_activity: str) -> List[ResearchConflict]:
        """Find potential conflicts with proposed research activity."""
        conflicts = []

        # Parse proposed activity
        activity_info = await self.baml_wrapper.parse_activity_requirements(proposed_activity)

        # Check resource conflicts
        existing_events = await self.check_research_calendar("next_month")

        for event in existing_events:
            if self._has_resource_conflict(activity_info, event):
                conflicts.append(ResearchConflict(
                    type="resource",
                    conflicting_event=event,
                    description=f"Resource conflict: both need {activity_info.resources}"
                ))

            if self._has_timing_conflict(activity_info, event):
                conflicts.append(ResearchConflict(
                    type="timing",
                    conflicting_event=event,
                    description=f"Timing conflict with {event.title}"
                ))

        return conflicts

    async def _parse_time_scope(self, time_scope: str) -> tuple:
        """Parse natural language time expressions."""
        time_mappings = {
            "today": (datetime.now().date(), datetime.now().date() + timedelta(days=1)),
            "current_week": (
                datetime.now().date() - timedelta(days=datetime.now().weekday()),
                datetime.now().date() + timedelta(days=7-datetime.now().weekday())
            ),
            "next_week": (
                datetime.now().date() + timedelta(days=7-datetime.now().weekday()),
                datetime.now().date() + timedelta(days=14-datetime.now().weekday())
            ),
            "current_month": (
                datetime.now().replace(day=1).date(),
                (datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1).date()
            )
        }

        return time_mappings.get(time_scope, time_mappings["current_week"])
```

#### Hypothesis Inbox Tool
**Location**: `src/agents/tools/hypothesis_inbox.py`

```python
class HypothesisInboxTool(SemanticTool):
    """Semantic interface for managing hypothesis workflow like an email inbox."""

    async def check_hypothesis_inbox(self, folder: str = "unread") -> List[HypothesisMessage]:
        """Check hypothesis inbox with folder-like organization."""
        query = SemanticQuery(
            query_text=f"hypotheses in {folder} folder",
            task_context="hypothesis_management",
            agent_type="reflection",
            intent="browse"
        )

        # Get hypotheses based on folder
        folder_filters = {
            "unread": lambda h: not h.get("reviewed", False),
            "flagged": lambda h: h.get("priority") == "high",
            "drafts": lambda h: h.get("status") == "draft",
            "reviewed": lambda h: h.get("reviewed", False),
            "needs_work": lambda h: h.get("needs_revision", False),
            "ready": lambda h: h.get("status") == "ready_for_testing"
        }

        all_hypotheses = await self.context_memory.get("hypotheses", [])
        folder_filter = folder_filters.get(folder, folder_filters["unread"])
        filtered_hypotheses = [h for h in all_hypotheses if folder_filter(h)]

        # Convert to inbox messages
        messages = []
        for hypothesis in filtered_hypotheses:
            message = HypothesisMessage(
                id=hypothesis["id"],
                subject=hypothesis["description"][:80] + "...",
                sender=hypothesis.get("generated_by", "GenerationAgent"),
                received_date=hypothesis.get("created_at"),
                priority=hypothesis.get("priority", "normal"),
                has_attachments=bool(hypothesis.get("supporting_evidence")),
                tags=hypothesis.get("tags", []),
                content=hypothesis
            )
            messages.append(message)

        return sorted(messages, key=lambda m: m.received_date, reverse=True)

    async def search_hypothesis_inbox(self, search_query: str) -> List[HypothesisMessage]:
        """Search hypothesis inbox with intelligent query understanding."""
        query = SemanticQuery(
            query_text=search_query,
            task_context="hypothesis_search",
            agent_type="generation",
            intent="search"
        )

        # Use BAML for intelligent search
        search_results = await self.baml_wrapper.semantic_hypothesis_search(
            search_query=search_query,
            available_hypotheses=await self.context_memory.get("hypotheses", [])
        )

        messages = []
        for result in search_results.results:
            hypothesis = result.hypothesis_data
            message = HypothesisMessage(
                id=hypothesis["id"],
                subject=hypothesis["description"][:80] + "...",
                sender=hypothesis.get("generated_by", "GenerationAgent"),
                received_date=hypothesis.get("created_at"),
                priority=hypothesis.get("priority", "normal"),
                relevance_score=result.relevance_score,
                search_highlights=result.highlights,
                content=hypothesis
            )
            messages.append(message)

        return messages

    async def organize_hypotheses(self, organization_criteria: str) -> Dict[str, List[HypothesisMessage]]:
        """Organize hypotheses based on natural language criteria."""
        all_hypotheses = await self.context_memory.get("hypotheses", [])

        # Use BAML to understand organization criteria and group hypotheses
        organization_result = await self.baml_wrapper.organize_hypotheses(
            hypotheses=all_hypotheses,
            criteria=organization_criteria
        )

        organized_folders = {}
        for folder_name, hypothesis_ids in organization_result.folders.items():
            folder_hypotheses = [h for h in all_hypotheses if h["id"] in hypothesis_ids]
            messages = []

            for hypothesis in folder_hypotheses:
                message = HypothesisMessage(
                    id=hypothesis["id"],
                    subject=hypothesis["description"][:80] + "...",
                    sender=hypothesis.get("generated_by", "GenerationAgent"),
                    received_date=hypothesis.get("created_at"),
                    folder=folder_name,
                    content=hypothesis
                )
                messages.append(message)

            organized_folders[folder_name] = messages

        return organized_folders

    async def batch_process_hypotheses(self, selection_criteria: str,
                                     action: str) -> List[ProcessingResult]:
        """Batch process hypotheses like email operations."""
        # Find hypotheses matching criteria
        matching_hypotheses = await self._find_hypotheses_by_criteria(selection_criteria)

        results = []
        for hypothesis in matching_hypotheses:
            try:
                if action == "mark_reviewed":
                    await self._mark_hypothesis_reviewed(hypothesis["id"])
                    results.append(ProcessingResult(hypothesis["id"], "success", "Marked as reviewed"))

                elif action == "flag_for_revision":
                    await self._flag_for_revision(hypothesis["id"])
                    results.append(ProcessingResult(hypothesis["id"], "success", "Flagged for revision"))

                elif action == "archive":
                    await self._archive_hypothesis(hypothesis["id"])
                    results.append(ProcessingResult(hypothesis["id"], "success", "Archived"))

                elif action == "priority_high":
                    await self._set_priority(hypothesis["id"], "high")
                    results.append(ProcessingResult(hypothesis["id"], "success", "Set to high priority"))

            except Exception as e:
                results.append(ProcessingResult(hypothesis["id"], "error", str(e)))

        return results
```

#### Research Literature Library Tool
**Location**: `src/agents/tools/literature_library.py`

```python
class LiteratureLibraryTool(SemanticTool):
    """Semantic interface for research literature like a personal library."""

    async def browse_literature_shelves(self, section: str = "recent_additions") -> List[LiteratureItem]:
        """Browse literature organized like library sections."""
        query = SemanticQuery(
            query_text=f"literature in {section} section",
            task_context="literature_review",
            agent_type="generation",
            intent="browse"
        )

        # Define library sections
        section_filters = {
            "recent_additions": lambda lit: self._is_recent(lit.get("added_date")),
            "frequently_cited": lambda lit: lit.get("citation_count", 0) > 10,
            "highly_relevant": lambda lit: lit.get("relevance_score", 0) > 0.8,
            "methodology": lambda lit: "methodology" in lit.get("tags", []),
            "foundational": lambda lit: "foundational" in lit.get("tags", []),
            "current_research": lambda lit: self._is_current_research(lit),
            "bookmarked": lambda lit: lit.get("bookmarked", False)
        }

        all_literature = await self.context_memory.get("literature", [])
        section_filter = section_filters.get(section, section_filters["recent_additions"])
        filtered_literature = [lit for lit in all_literature if section_filter(lit)]

        return [LiteratureItem.from_dict(lit) for lit in filtered_literature]

    async def search_literature_catalog(self, search_terms: str,
                                      search_type: str = "semantic") -> List[LiteratureItem]:
        """Search literature catalog with different search strategies."""
        query = SemanticQuery(
            query_text=search_terms,
            task_context="literature_search",
            agent_type="generation",
            intent="search"
        )

        if search_type == "semantic":
            # Semantic search using BAML
            search_results = await self.baml_wrapper.semantic_literature_search(
                query=search_terms,
                literature_database=await self.context_memory.get("literature", [])
            )

            return [LiteratureItem.from_dict(result.literature_data)
                   for result in search_results.results]

        elif search_type == "citation":
            # Citation-based search
            return await self._search_by_citations(search_terms)

        elif search_type == "author":
            # Author-based search
            return await self._search_by_author(search_terms)

        elif search_type == "temporal":
            # Time-based search
            return await self._search_by_timeframe(search_terms)

    async def get_reading_recommendations(self, research_focus: str,
                                        reading_goal: str = "comprehensive") -> List[ReadingRecommendation]:
        """Get personalized reading recommendations."""
        current_literature = await self.context_memory.get("literature", [])

        # Use BAML to generate reading recommendations
        recommendations = await self.baml_wrapper.generate_reading_recommendations(
            research_focus=research_focus,
            reading_goal=reading_goal,
            current_knowledge=current_literature,
            reading_history=await self._get_reading_history()
        )

        reading_recs = []
        for rec in recommendations.recommendations:
            reading_rec = ReadingRecommendation(
                literature_item=rec.literature,
                relevance_score=rec.relevance,
                reading_priority=rec.priority,
                estimated_reading_time=rec.time_estimate,
                key_insights_preview=rec.key_insights,
                connection_to_focus=rec.connection_explanation,
                prerequisites=rec.prerequisites,
                follow_up_reading=rec.follow_up_suggestions
            )
            reading_recs.append(reading_rec)

        return reading_recs

    async def create_literature_collection(self, collection_name: str,
                                         selection_criteria: str) -> LiteratureCollection:
        """Create curated literature collections like playlists."""
        # Use BAML to understand selection criteria and curate collection
        curation_result = await self.baml_wrapper.curate_literature_collection(
            collection_name=collection_name,
            criteria=selection_criteria,
            available_literature=await self.context_memory.get("literature", [])
        )

        collection = LiteratureCollection(
            name=collection_name,
            description=curation_result.description,
            items=[LiteratureItem.from_dict(item) for item in curation_result.selected_items],
            selection_rationale=curation_result.rationale,
            recommended_reading_order=curation_result.reading_order,
            estimated_total_time=curation_result.total_reading_time,
            tags=curation_result.tags,
            created_date=datetime.now()
        )

        # Store collection
        await self.context_memory.append_to_aggregate("literature_collections", collection.to_dict())

        return collection
```

### 2. Agent Integration Framework

#### Semantic Tool Manager
**Location**: `src/agents/semantic_tool_manager.py`

```python
class SemanticToolManager:
    """Manages semantic tools for agents with intelligent routing."""

    def __init__(self, context_memory, baml_wrapper):
        self.context_memory = context_memory
        self.baml_wrapper = baml_wrapper

        # Initialize semantic tools
        self.tools = {
            "research_calendar": ResearchCalendarTool(context_memory, baml_wrapper),
            "hypothesis_inbox": HypothesisInboxTool(context_memory, baml_wrapper),
            "literature_library": LiteratureLibraryTool(context_memory, baml_wrapper),
            "experiment_lab": ExperimentLabTool(context_memory, baml_wrapper),
            "analysis_workbench": AnalysisWorkbenchTool(context_memory, baml_wrapper)
        }

        self.usage_analytics = SemanticToolAnalytics()

    async def route_semantic_request(self, request: str,
                                   agent_context: str) -> SemanticResult:
        """Intelligently route semantic requests to appropriate tools."""

        # Use BAML to understand intent and route to best tool
        routing_analysis = await self.baml_wrapper.analyze_semantic_request(
            request=request,
            agent_context=agent_context,
            available_tools=list(self.tools.keys())
        )

        primary_tool = self.tools[routing_analysis.primary_tool]

        # Create semantic query
        query = SemanticQuery(
            query_text=request,
            task_context=agent_context,
            agent_type=routing_analysis.agent_type,
            intent=routing_analysis.intent,
            filters=routing_analysis.suggested_filters
        )

        # Execute primary operation
        result = await primary_tool.semantic_operation(query)

        # If confidence is low, try complementary tools
        if routing_analysis.confidence < 0.8 and routing_analysis.complementary_tools:
            complementary_results = []
            for tool_name in routing_analysis.complementary_tools:
                tool = self.tools[tool_name]
                comp_result = await tool.semantic_operation(query)
                complementary_results.append(comp_result)

            # Synthesize results
            result = await self._synthesize_results(result, complementary_results)

        # Track usage for learning
        await self.usage_analytics.record_usage(query, result, routing_analysis)

        return result

    async def suggest_semantic_operations(self, agent_type: str,
                                        current_task: str) -> List[SemanticSuggestion]:
        """Suggest helpful semantic operations based on context."""
        suggestions = []

        # Analyze current context
        context_analysis = await self.baml_wrapper.analyze_work_context(
            agent_type=agent_type,
            current_task=current_task
        )

        # Generate tool-specific suggestions
        for tool_name, tool in self.tools.items():
            tool_suggestions = await tool.suggest_operations_for_context(context_analysis)

            for suggestion in tool_suggestions:
                semantic_suggestion = SemanticSuggestion(
                    tool_name=tool_name,
                    operation=suggestion.operation,
                    description=suggestion.description,
                    expected_benefit=suggestion.benefit,
                    confidence=suggestion.confidence,
                    estimated_time=suggestion.time_estimate
                )
                suggestions.append(semantic_suggestion)

        # Sort by relevance and confidence
        suggestions.sort(key=lambda s: (s.confidence, s.expected_benefit), reverse=True)

        return suggestions[:5]  # Return top 5 suggestions
```

#### Enhanced Agent Base with Semantic Tools
**Location**: `src/agents/semantic_agent_base.py`

```python
class SemanticAgentBase:
    """Enhanced agent base class with semantic tool integration."""

    def __init__(self, context_memory, baml_wrapper):
        self.context_memory = context_memory
        self.baml_wrapper = baml_wrapper
        self.semantic_tools = SemanticToolManager(context_memory, baml_wrapper)
        self.semantic_shortcuts = self._initialize_shortcuts()

    def _initialize_shortcuts(self) -> Dict[str, str]:
        """Initialize semantic shortcuts for common operations."""
        return {
            # Research calendar shortcuts
            "check_schedule": "research_calendar.check_research_calendar",
            "schedule_task": "research_calendar.schedule_research_activity",
            "find_conflicts": "research_calendar.find_research_conflicts",

            # Hypothesis inbox shortcuts
            "check_hypotheses": "hypothesis_inbox.check_hypothesis_inbox",
            "search_hypotheses": "hypothesis_inbox.search_hypothesis_inbox",
            "organize_hypotheses": "hypothesis_inbox.organize_hypotheses",

            # Literature library shortcuts
            "browse_literature": "literature_library.browse_literature_shelves",
            "search_papers": "literature_library.search_literature_catalog",
            "get_reading_recs": "literature_library.get_reading_recommendations"
        }

    async def semantic_request(self, request: str) -> SemanticResult:
        """Make a semantic request using natural language."""
        agent_context = f"{self.__class__.__name__} working on {getattr(self, 'current_task', 'general_research')}"
        return await self.semantic_tools.route_semantic_request(request, agent_context)

    # Convenience methods with natural language interfaces
    async def check_my_schedule(self, timeframe: str = "today") -> List[ResearchEvent]:
        """Natural language interface: 'What's on my schedule today?'"""
        return await self.semantic_request(f"What's on my research schedule for {timeframe}?")

    async def find_relevant_papers(self, topic: str, focus: str = "recent") -> List[LiteratureItem]:
        """Natural language interface: 'Find papers about X'"""
        return await self.semantic_request(f"Find {focus} papers about {topic}")

    async def check_hypothesis_status(self, filter_criteria: str = "needs attention") -> List[HypothesisMessage]:
        """Natural language interface: 'Which hypotheses need attention?'"""
        return await self.semantic_request(f"Show me hypotheses that {filter_criteria}")

    async def plan_research_session(self, research_goal: str, duration: str = "2 hours") -> ResearchPlan:
        """Natural language interface: 'Plan a research session on X'"""
        result = await self.semantic_request(
            f"Plan a {duration} research session focused on {research_goal}"
        )
        return result.research_plan

    async def get_context_recommendations(self) -> List[SemanticSuggestion]:
        """Get AI recommendations for current context."""
        current_task = getattr(self, 'current_task', 'general_research')
        return await self.semantic_tools.suggest_semantic_operations(
            self.__class__.__name__,
            current_task
        )
```

### 3. BAML Functions for Semantic Operations

#### Semantic Understanding Functions
**Location**: `baml_src/functions.baml` (additions)

```baml
function AnalyzeSemanticRequest(
    request: string,
    agent_context: string,
    available_tools: string[]
) -> SemanticRoutingAnalysis {
    client ProductionClient

    prompt #"
        {{ _.role("system") }}
        You are an expert at understanding research workflow requests and routing them to appropriate semantic tools.
        You excel at interpreting natural language research intentions and mapping them to tool capabilities.

        {{ _.role("user") }}
        Analyze this semantic request and determine the best tool routing:

        Request: {{ request }}
        Agent Context: {{ agent_context }}
        Available Tools: {{ available_tools | join(", ") }}

        Tool Capabilities:
        - research_calendar: Schedule management, timeline planning, conflict detection
        - hypothesis_inbox: Hypothesis organization, review workflows, status tracking
        - literature_library: Paper discovery, reading recommendations, collection curation
        - experiment_lab: Experiment design, protocol management, result tracking
        - analysis_workbench: Data analysis, statistical operations, visualization

        Provide routing analysis with:
        1. Primary tool (most appropriate for the request)
        2. Intent classification (search, browse, organize, analyze, schedule)
        3. Confidence level (0.0-1.0)
        4. Suggested filters or parameters
        5. Complementary tools if primary confidence < 0.8
        6. Agent type inference from context
    "#
}

function GenerateReadingRecommendations(
    research_focus: string,
    reading_goal: string,
    current_knowledge: LiteratureItem[],
    reading_history: ReadingHistory[]
) -> ReadingRecommendations {
    client ProductionClient

    prompt #"
        {{ _.role("system") }}
        You are an expert research librarian who provides personalized reading recommendations.
        You excel at understanding research goals and suggesting optimal reading sequences.

        {{ _.role("user") }}
        Generate reading recommendations for this researcher:

        Research Focus: {{ research_focus }}
        Reading Goal: {{ reading_goal }}

        Current Knowledge Base:
        {% for item in current_knowledge %}
        - {{ item.title }} ({{ item.year }}) - Relevance: {{ item.relevance_score }}
        {% endfor %}

        Reading History Pattern:
        {% for history in reading_history %}
        - {{ history.topic }}: {{ history.papers_read }} papers, avg rating {{ history.avg_rating }}
        {% endfor %}

        Reading Goals:
        - comprehensive: Thorough coverage of the field
        - targeted: Focused on specific aspects
        - foundational: Building basic understanding
        - cutting_edge: Latest developments only
        - methodology: Focus on research methods

        Provide recommendations with:
        1. Prioritized reading list with rationale
        2. Estimated reading times
        3. Key insights preview
        4. Connection to research focus
        5. Reading sequence optimization
        6. Prerequisites and follow-up suggestions
    "#
}

function OrganizeHypotheses(
    hypotheses: Hypothesis[],
    criteria: string
) -> HypothesisOrganization {
    client ProductionClient

    prompt #"
        {{ _.role("system") }}
        You are an expert at organizing scientific hypotheses using intelligent categorization.
        You excel at understanding organizational criteria and creating logical groupings.

        {{ _.role("user") }}
        Organize these hypotheses based on the specified criteria:

        Organization Criteria: {{ criteria }}

        Hypotheses to organize:
        {% for hypothesis in hypotheses %}
        - ID: {{ hypothesis.id }}
        - Description: {{ hypothesis.description }}
        - Status: {{ hypothesis.status }}
        - Priority: {{ hypothesis.priority }}
        - Tags: {{ hypothesis.tags | join(", ") }}
        - Generated: {{ hypothesis.created_at }}
        {% endfor %}

        Common organization criteria:
        - by_topic: Group by research domain or subject area
        - by_priority: Group by urgency and importance
        - by_status: Group by current workflow status
        - by_methodology: Group by experimental approach
        - by_timeline: Group by expected completion time
        - by_complexity: Group by difficulty and resource requirements

        Create logical folders with:
        1. Meaningful folder names
        2. Clear selection rationale
        3. Hypothesis ID assignments
        4. Folder descriptions
        5. Suggested processing order
    "#
}
```

### 4. Data Models for Semantic Tools

#### Semantic Tool Data Models
**Location**: `src/core/semantic_models.py`

```python
@dataclass
class ResearchEvent:
    """Research calendar event."""
    id: str
    title: str
    description: str
    start_time: datetime
    duration: timedelta
    priority: str
    dependencies: List[str]
    resources_needed: List[str]
    status: str = "scheduled"

    @classmethod
    def from_dict(cls, data: dict) -> 'ResearchEvent':
        return cls(**data)

    def to_dict(self) -> dict:
        return asdict(self)

@dataclass
class HypothesisMessage:
    """Hypothesis as inbox message."""
    id: str
    subject: str
    sender: str
    received_date: datetime
    priority: str
    has_attachments: bool
    tags: List[str]
    folder: str = "inbox"
    read: bool = False
    flagged: bool = False
    relevance_score: Optional[float] = None
    search_highlights: List[str] = field(default_factory=list)
    content: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LiteratureItem:
    """Literature as library item."""
    id: str
    title: str
    authors: List[str]
    year: int
    journal: str
    abstract: str
    keywords: List[str]
    citation_count: int
    relevance_score: float
    tags: List[str]
    added_date: datetime
    bookmarked: bool = False
    reading_status: str = "unread"
    personal_notes: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> 'LiteratureItem':
        return cls(**data)

@dataclass
class SemanticSuggestion:
    """Suggestion for semantic operation."""
    tool_name: str
    operation: str
    description: str
    expected_benefit: str
    confidence: float
    estimated_time: int  # minutes
    context_relevance: float = 1.0
```

## Benefits and Integration

### Enhanced Agent Capabilities

1. **Natural Interaction**: Agents interact with information using human-like patterns
2. **Context Intelligence**: Tools adapt behavior based on current task and agent type
3. **Cognitive Metaphors**: Familiar interfaces (calendar, inbox, library) reduce cognitive load
4. **Learning Adaptation**: Tools improve based on usage patterns and effectiveness

### Development Workflow Enhancement

1. **Intuitive Information Access**: Developers can request information naturally
2. **Intelligent Filtering**: Automatic relevance filtering reduces information overload
3. **Contextual Recommendations**: AI suggests relevant operations based on current work
4. **Seamless Integration**: Works with existing context memory and BAML infrastructure

### Long-term Benefits

1. **Productivity Multiplication**: Natural interfaces accelerate information access
2. **Knowledge Discovery**: Semantic organization reveals hidden connections
3. **Workflow Optimization**: Learning algorithms optimize information presentation
4. **Cognitive Offloading**: Agents handle information management complexity

---

*This is Part 3 of the Comprehensive ACE-FCA Integration Plan. Continue with Part 4 for Implementation Timeline and Integration.*