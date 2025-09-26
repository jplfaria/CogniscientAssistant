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