import os
import re
from typing import List, Tuple, Dict, Set
from dataclasses import dataclass

@dataclass
class ContextRecommendation:
    specs: List[str]
    confidence_score: float
    reasoning: str
    fallback_needed: bool = False

class SpecificationRelevanceScorer:
    def __init__(self, specs_directory: str = "specs/"):
        self.specs_dir = specs_directory
        self.cache = {}
        # Always include foundational specs
        self.critical_specs = ["001-system-overview.md", "002-core-principles.md", "003-research-workflow.md"]

        # Domain keyword mappings for relevance scoring
        self.domain_keywords = {
            'agent': ['agent', 'supervisor', 'generation', 'reflection', 'ranking', 'evolution', 'proximity', 'meta-review'],
            'baml': ['baml', 'llm', 'function', 'prompt', 'model', 'client'],
            'testing': ['test', 'mock', 'pytest', 'integration', 'unit', 'coverage'],
            'infrastructure': ['queue', 'memory', 'context', 'safety', 'task', 'worker'],
            'phase': [f'phase {i}' for i in range(1, 18)]
        }

    def extract_task_keywords(self, task_description: str) -> Set[str]:
        """Extract domain-relevant keywords from task description."""
        words = set(re.findall(r'\b\w+\b', task_description.lower()))

        # Handle CamelCase by splitting it
        for word in list(words):
            # Split CamelCase words like "ReflectionAgent" -> ["reflection", "agent"]
            if len(word) > 5:  # Only split longer words
                # Insert spaces before capital letters and split
                camel_split = re.sub(r'([a-z])([A-Z])', r'\1 \2', task_description)
                extra_words = set(re.findall(r'\b\w+\b', camel_split.lower()))
                words.update(extra_words)

        # Add compound concepts
        if 'reflection' in words and 'agent' in words:
            words.add('reflection-agent')
            words.add('reflection')  # Ensure individual words are there too
            words.add('agent')
        if 'baml' in words and any(w in words for w in ['function', 'integration']):
            words.add('baml-integration')

        return words

    def score_specification(self, task_keywords: Set[str], spec_path: str) -> float:
        """Score a single specification for relevance to task."""
        if spec_path in self.cache:
            spec_content = self.cache[spec_path]
        else:
            try:
                with open(os.path.join(self.specs_dir, spec_path), 'r') as f:
                    spec_content = f.read().lower()
                self.cache[spec_path] = spec_content
            except FileNotFoundError:
                return 0.0

        # Check spec filename for keywords
        filename_score = 0.0
        spec_name_lower = spec_path.lower()
        for keyword in task_keywords:
            if keyword in spec_name_lower:
                filename_score += 0.3

        spec_words = set(re.findall(r'\b\w+\b', spec_content))

        # Calculate keyword coverage (what % of task keywords appear in spec)
        # This is better than Jaccard for large documents
        intersection = task_keywords.intersection(spec_words)
        if len(task_keywords) > 0:
            base_score = len(intersection) / len(task_keywords)
        else:
            base_score = 0.0

        # Combine filename and content scores
        combined_score = min(1.0, base_score + filename_score)

        # Apply domain weighting
        weighted_score = self.apply_domain_weighting(combined_score, task_keywords, spec_path)

        return min(1.0, weighted_score)

    def apply_domain_weighting(self, base_score: float, task_keywords: Set[str], spec_path: str) -> float:
        """Apply domain-specific weighting to relevance scores."""
        weight_multiplier = 1.0

        # Boost agent-related specs for agent tasks
        if any(kw in task_keywords for kw in self.domain_keywords['agent']):
            if any(agent_type in spec_path for agent_type in ['supervisor', 'generation', 'reflection', 'ranking']):
                weight_multiplier += 0.3

        # Boost BAML specs for BAML-related tasks
        if any(kw in task_keywords for kw in self.domain_keywords['baml']):
            if 'baml' in spec_path or 'llm' in spec_path:
                weight_multiplier += 0.4

        # Boost testing specs for test implementation
        if any(kw in task_keywords for kw in self.domain_keywords['testing']):
            if 'test' in spec_path:
                weight_multiplier += 0.2

        return base_score * weight_multiplier

    def select_optimal_specs(self, task_description: str, max_specs: int = 5) -> ContextRecommendation:
        """Select optimal specifications for current task."""
        task_keywords = self.extract_task_keywords(task_description)

        # Always include critical specs
        selected_specs = list(self.critical_specs)

        # Score all available specs
        spec_scores = []
        for spec_file in os.listdir(self.specs_dir):
            if spec_file.endswith('.md') and spec_file not in self.critical_specs:
                score = self.score_specification(task_keywords, spec_file)
                spec_scores.append((spec_file, score))

        # Sort by relevance and select top specs
        spec_scores.sort(key=lambda x: x[1], reverse=True)

        remaining_slots = max_specs - len(selected_specs)
        relevance_threshold = 0.15  # Lowered from 0.3

        for spec_file, score in spec_scores:
            if remaining_slots <= 0:
                break
            if score >= relevance_threshold:
                selected_specs.append(spec_file)
                remaining_slots -= 1

        # Calculate confidence based on whether we found relevant specs
        if len(spec_scores) > 0:
            top_scores = [score for _, score in spec_scores[:3]]
            avg_top_score = sum(top_scores) / len(top_scores) if top_scores else 0
            confidence = min(1.0, avg_top_score * 2)  # Scale up the confidence
        else:
            confidence = 0.0

        # Generate reasoning
        reasoning = f"Selected {len(selected_specs)} specs based on task keywords: {', '.join(list(task_keywords)[:5])}"

        return ContextRecommendation(
            specs=selected_specs,
            confidence_score=confidence,
            reasoning=reasoning,
            fallback_needed=confidence < 0.4  # Lowered from 0.6
        )

    def analyze_task_context(self, task_description: str, current_phase: int) -> Dict[str, any]:
        """Analyze task for enhanced context understanding."""

        analysis = {
            'phase': current_phase,
            'task_type': self.detect_task_type(task_description),
            'components': self.extract_components(task_description),
            'domain': self.identify_domain(task_description),
            'complexity': self.assess_complexity(task_description)
        }

        return analysis

    def detect_task_type(self, task_description: str) -> str:
        """Detect the type of implementation task."""
        task_lower = task_description.lower()

        if any(keyword in task_lower for keyword in ['test', 'testing', 'unit test', 'integration test']):
            return 'testing'
        elif any(keyword in task_lower for keyword in ['agent', 'supervisor', 'generation', 'reflection']):
            return 'agent_implementation'
        elif any(keyword in task_lower for keyword in ['baml', 'function', 'client']):
            return 'baml_integration'
        elif any(keyword in task_lower for keyword in ['queue', 'memory', 'context']):
            return 'infrastructure'
        else:
            return 'general'

    def extract_components(self, task_description: str) -> List[str]:
        """Extract system components mentioned in task."""
        components = []
        component_patterns = {
            'TaskQueue': ['queue', 'task queue', 'worker'],
            'ContextMemory': ['memory', 'context memory', 'storage'],
            'SupervisorAgent': ['supervisor', 'orchestration', 'coordination'],
            'GenerationAgent': ['generation', 'hypothesis'],
            'ReflectionAgent': ['reflection', 'review', 'critique'],
            'RankingAgent': ['ranking', 'tournament'],
            'EvolutionAgent': ['evolution', 'mutation'],
            'ProximityAgent': ['proximity', 'clustering'],
            'MetaReviewAgent': ['meta-review', 'meta review'],
            'BAML': ['baml', 'llm', 'function'],
            'Safety': ['safety', 'validation', 'check']
        }

        task_lower = task_description.lower()
        for component, keywords in component_patterns.items():
            if any(keyword in task_lower for keyword in keywords):
                components.append(component)

        return components

    def identify_domain(self, task_description: str) -> str:
        """Identify the primary domain of the task."""
        task_lower = task_description.lower()

        # Count matches for each domain
        domain_scores = {}
        for domain, keywords in self.domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword in task_lower)
            if score > 0:
                domain_scores[domain] = score

        if not domain_scores:
            return 'general'

        # Return domain with highest score
        return max(domain_scores, key=domain_scores.get)

    def assess_complexity(self, task_description: str) -> str:
        """Assess the complexity level of the task."""
        task_lower = task_description.lower()

        # High complexity indicators
        high_indicators = ['integration', 'coordination', 'multiple', 'complex', 'comprehensive']
        # Medium complexity indicators
        medium_indicators = ['implement', 'create', 'add', 'enhance', 'update']
        # Low complexity indicators
        low_indicators = ['test', 'fix', 'update', 'simple', 'basic']

        high_count = sum(1 for indicator in high_indicators if indicator in task_lower)
        medium_count = sum(1 for indicator in medium_indicators if indicator in task_lower)
        low_count = sum(1 for indicator in low_indicators if indicator in task_lower)

        if high_count >= 2 or 'integration' in task_lower:
            return 'high'
        elif medium_count > low_count:
            return 'medium'
        else:
            return 'low'

    def select_optimal_specs_with_analysis(self, task_description: str, task_analysis: Dict[str, any], max_specs: int = 6) -> ContextRecommendation:
        """Select optimal specifications using enhanced task analysis."""
        task_keywords = self.extract_task_keywords(task_description)

        # Always include critical specs
        selected_specs = list(self.critical_specs)

        # Score all available specs with enhanced analysis
        spec_scores = []
        for spec_file in os.listdir(self.specs_dir):
            if spec_file.endswith('.md') and spec_file not in self.critical_specs:
                base_score = self.score_specification(task_keywords, spec_file)

                # Apply enhanced scoring based on analysis
                enhanced_score = self.enhance_score_with_analysis(base_score, spec_file, task_analysis)
                spec_scores.append((spec_file, enhanced_score))

        # Sort by relevance and select top specs
        spec_scores.sort(key=lambda x: x[1], reverse=True)

        remaining_slots = max_specs - len(selected_specs)
        relevance_threshold = 0.15

        for spec_file, score in spec_scores:
            if remaining_slots <= 0:
                break
            if score >= relevance_threshold:
                selected_specs.append(spec_file)
                remaining_slots -= 1

        # Calculate enhanced confidence
        if len(spec_scores) > 0:
            top_scores = [score for _, score in spec_scores[:3]]
            avg_top_score = sum(top_scores) / len(top_scores) if top_scores else 0

            # Boost confidence for phase-appropriate selections
            phase_boost = self.get_phase_confidence_boost(task_analysis['phase'], selected_specs)
            confidence = min(1.0, (avg_top_score * 2) + phase_boost)
        else:
            confidence = 0.0

        # Generate enhanced reasoning
        components_str = ', '.join(task_analysis['components'][:3]) if task_analysis['components'] else 'general'
        reasoning = f"Selected {len(selected_specs)} specs for {task_analysis['task_type']} task (Phase {task_analysis['phase']}) involving {components_str}"

        return ContextRecommendation(
            specs=selected_specs,
            confidence_score=confidence,
            reasoning=reasoning,
            fallback_needed=confidence < 0.4
        )

    def enhance_score_with_analysis(self, base_score: float, spec_file: str, task_analysis: Dict[str, any]) -> float:
        """Enhance spec score based on task analysis."""
        enhanced_score = base_score

        # Component-based enhancement
        for component in task_analysis['components']:
            if component.lower() in spec_file.lower():
                enhanced_score += 0.4

        # Phase-specific enhancement
        phase_specs = self.get_phase_specific_specs(task_analysis['phase'])
        if spec_file in phase_specs:
            enhanced_score += 0.3

        # Domain-specific enhancement
        domain = task_analysis['domain']
        if domain == 'agent' and 'agent' in spec_file:
            enhanced_score += 0.2
        elif domain == 'baml' and ('baml' in spec_file or 'llm' in spec_file):
            enhanced_score += 0.2
        elif domain == 'infrastructure' and any(infra in spec_file for infra in ['queue', 'memory', 'context']):
            enhanced_score += 0.2

        return min(1.0, enhanced_score)

    def get_phase_specific_specs(self, phase: int) -> List[str]:
        """Get specifications most relevant to specific phases."""
        phase_spec_map = {
            1: ['001-system-overview.md'],
            2: ['002-core-principles.md'],
            3: ['006-task-queue-behavior.md'],
            4: ['015-context-memory.md'],
            5: ['020-safety-mechanisms.md'],
            6: ['023-llm-abstraction.md'],
            7: ['024-argo-gateway-integration.md'],
            8: ['005-supervisor-agent.md'],
            9: ['007-generation-agent.md'],
            10: ['007-generation-agent.md'],
            11: ['008-reflection-agent.md'],
            12: ['009-ranking-agent.md'],
            13: ['010-evolution-agent.md'],
            14: ['011-proximity-agent.md'],
            15: ['012-meta-review-agent.md'],
            16: ['013-agent-interaction-protocols.md'],
            17: ['021-validation-criteria.md']
        }

        return phase_spec_map.get(phase, [])

    def get_phase_confidence_boost(self, phase: int, selected_specs: List[str]) -> float:
        """Calculate confidence boost based on phase-appropriate spec inclusion."""
        phase_specs = self.get_phase_specific_specs(phase)
        if not phase_specs:
            return 0.0

        # Boost if we included phase-specific specs
        included_phase_specs = [spec for spec in selected_specs if spec in phase_specs]
        if included_phase_specs:
            return 0.1 * len(included_phase_specs)
        else:
            return 0.0

    def validate_context_selection(self, task: str, selected_specs: List[str],
                                 current_phase: int) -> Dict[str, any]:
        """Validate that context selection meets quality requirements."""

        validation_result = {
            'is_valid': True,
            'warnings': [],
            'critical_issues': [],
            'confidence_adjustment': 0.0
        }

        # Check critical spec inclusion
        missing_critical = set(self.critical_specs) - set(selected_specs)
        if missing_critical:
            validation_result['critical_issues'].append(
                f"Missing critical specs: {missing_critical}"
            )
            validation_result['is_valid'] = False

        # Check phase-appropriate specs
        phase_requirements = self.get_phase_requirements(current_phase)
        for requirement in phase_requirements:
            if not any(req in spec for spec in selected_specs for req in requirement['keywords']):
                validation_result['warnings'].append(
                    f"Phase {current_phase} may need {requirement['spec_type']} specification"
                )
                validation_result['confidence_adjustment'] -= 0.1

        # Check minimum specs threshold
        if len(selected_specs) < 3:
            validation_result['warnings'].append(
                "Very few specifications selected - may lack context"
            )
            validation_result['confidence_adjustment'] -= 0.2

        # Check maximum specs threshold
        if len(selected_specs) > 10:
            validation_result['warnings'].append(
                f"Too many specifications selected ({len(selected_specs)}) - may reduce optimization benefit"
            )
            validation_result['confidence_adjustment'] -= 0.1

        return validation_result

    def get_phase_requirements(self, phase: int) -> List[Dict[str, any]]:
        """Get specification requirements for specific phases."""

        phase_map = {
            1: [{'spec_type': 'system-setup', 'keywords': ['setup', 'structure', 'dependencies']}],
            2: [{'spec_type': 'core-models', 'keywords': ['model', 'dataclass', 'structure']}],
            3: [{'spec_type': 'task-queue', 'keywords': ['queue', 'task', 'worker']}],
            4: [{'spec_type': 'context-memory', 'keywords': ['memory', 'context', 'storage']}],
            5: [{'spec_type': 'safety-framework', 'keywords': ['safety', 'validation', 'check']}],
            6: [{'spec_type': 'llm-abstraction', 'keywords': ['llm', 'provider', 'abstraction']}],
            7: [{'spec_type': 'baml-infrastructure', 'keywords': ['baml', 'function', 'client']}],
            8: [{'spec_type': 'supervisor-agent', 'keywords': ['supervisor', 'orchestration']}],
            9: [{'spec_type': 'generation-agent', 'keywords': ['generation', 'hypothesis']}],
            10: [{'spec_type': 'generation-agent', 'keywords': ['generation', 'hypothesis']}],
            11: [{'spec_type': 'reflection-agent', 'keywords': ['reflection', 'review', 'critique']}],
            12: [{'spec_type': 'ranking-agent', 'keywords': ['ranking', 'tournament']}],
            13: [{'spec_type': 'evolution-agent', 'keywords': ['evolution', 'mutation']}],
            14: [{'spec_type': 'proximity-agent', 'keywords': ['proximity', 'clustering']}],
            15: [{'spec_type': 'meta-review-agent', 'keywords': ['meta-review', 'synthesis']}],
            16: [{'spec_type': 'integration', 'keywords': ['integration', 'coordination']}],
            17: [{'spec_type': 'validation', 'keywords': ['validation', 'testing', 'final']}]
        }

        return phase_map.get(phase, [])