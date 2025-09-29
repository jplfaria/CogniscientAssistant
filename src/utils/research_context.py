"""Literature Context Scorer for ACE-FCA optimization.

This module implements intelligent literature relevance scoring to select the most
relevant papers for hypothesis generation, reducing context size while maintaining
research quality.
"""

import logging
import re
from dataclasses import dataclass
from typing import List, Set, Dict, Optional
from src.core.models import Hypothesis, Paper

logger = logging.getLogger(__name__)


@dataclass
class LiteratureSelection:
    """Result of literature relevance scoring."""
    papers: List[Paper]
    confidence_score: float
    reasoning: str
    fallback_needed: bool = False


class LiteratureRelevanceScorer:
    """Scores and selects relevant papers for research context optimization."""

    def __init__(self):
        """Initialize the scorer with domain weights."""
        self.domain_weights = {
            'methodology': 1.5,
            'results': 1.3,
            'theory': 1.0,
            'background': 0.7
        }

        # Keywords that indicate important content sections
        self.methodology_keywords = {
            'method', 'methodology', 'approach', 'technique', 'protocol',
            'procedure', 'experiment', 'analysis', 'measurement', 'assay'
        }

        self.results_keywords = {
            'result', 'finding', 'outcome', 'data', 'evidence', 'observation',
            'effect', 'impact', 'change', 'difference', 'significant'
        }

        self.theory_keywords = {
            'theory', 'hypothesis', 'model', 'mechanism', 'pathway',
            'framework', 'concept', 'principle', 'relationship'
        }

        self.background_keywords = {
            'background', 'introduction', 'review', 'previous', 'prior',
            'established', 'known', 'literature', 'context'
        }

    def select_relevant_papers(self, papers: List[Paper],
                             research_context: str,
                             hypothesis: Optional[Hypothesis] = None,
                             max_papers: int = 8) -> LiteratureSelection:
        """Select most relevant papers for research context.

        Args:
            papers: List of available papers
            research_context: The research goal or context description
            hypothesis: Optional existing hypothesis for additional context
            max_papers: Maximum number of papers to select

        Returns:
            LiteratureSelection with scored papers and metadata
        """
        if not papers:
            return LiteratureSelection(
                papers=[],
                confidence_score=1.0,  # High confidence in empty result
                reasoning="No papers available for selection",
                fallback_needed=False
            )

        if len(papers) <= max_papers:
            return LiteratureSelection(
                papers=papers,
                confidence_score=1.0,
                reasoning=f"All {len(papers)} papers included (below max limit)",
                fallback_needed=False
            )

        # Score each paper
        scored_papers = []
        for paper in papers:
            score = self._calculate_paper_relevance(paper, research_context, hypothesis)
            if score > 0.3:  # Conservative threshold
                scored_papers.append((paper, score))
                logger.debug(f"Paper '{paper.title[:50]}...' scored {score:.3f}")

        # Sort by relevance and select top papers
        scored_papers.sort(key=lambda x: x[1], reverse=True)
        selected_papers = [paper for paper, score in scored_papers[:max_papers]]

        # Calculate selection confidence
        confidence = self._calculate_selection_confidence(scored_papers, max_papers)

        return LiteratureSelection(
            papers=selected_papers,
            confidence_score=confidence,
            reasoning=f"Selected {len(selected_papers)} most relevant papers from {len(papers)} available",
            fallback_needed=confidence < 0.7
        )

    def _calculate_paper_relevance(self, paper: Paper, research_context: str,
                                  hypothesis: Optional[Hypothesis] = None) -> float:
        """Calculate relevance score for a single paper.

        Args:
            paper: Paper to score
            research_context: Research context to match against
            hypothesis: Optional hypothesis for additional context

        Returns:
            Relevance score between 0.0 and 1.0
        """
        total_score = 0.0
        weight_sum = 0.0

        # Combine text sources for analysis
        paper_text = self._combine_paper_text(paper)
        context_text = research_context.lower()

        if hypothesis:
            context_text += " " + hypothesis.summary.lower() + " " + hypothesis.full_description.lower()

        # Score different content types
        for content_type, keywords in [
            ('methodology', self.methodology_keywords),
            ('results', self.results_keywords),
            ('theory', self.theory_keywords),
            ('background', self.background_keywords)
        ]:
            content_score = self._score_content_overlap(
                paper_text, context_text, keywords
            )
            weight = self.domain_weights[content_type]

            total_score += content_score * weight
            weight_sum += weight

        # Normalize by total weights
        base_score = total_score / weight_sum if weight_sum > 0 else 0.0

        # Apply additional factors
        final_score = self._apply_relevance_factors(base_score, paper, research_context)

        return min(final_score, 1.0)

    def _combine_paper_text(self, paper: Paper) -> str:
        """Combine all paper text into a single lowercase string.

        Args:
            paper: Paper to extract text from

        Returns:
            Combined text string
        """
        text_parts = [paper.title, paper.abstract]

        # Add keywords if available
        if paper.keywords:
            text_parts.extend(paper.keywords)

        # Add methodology and domain info
        if paper.methodology_type:
            text_parts.append(paper.methodology_type)
        if paper.research_domain:
            text_parts.append(paper.research_domain)

        return " ".join(filter(None, text_parts)).lower()

    def _score_content_overlap(self, paper_text: str, context_text: str,
                              keywords: Set[str]) -> float:
        """Score overlap between paper content and research context.

        Args:
            paper_text: Paper content as lowercase string
            context_text: Research context as lowercase string
            keywords: Keywords to look for in the content

        Returns:
            Overlap score between 0.0 and 1.0
        """
        # Tokenize text
        paper_tokens = set(re.findall(r'\b\w+\b', paper_text))
        context_tokens = set(re.findall(r'\b\w+\b', context_text))

        # Find keyword matches
        paper_keywords = paper_tokens & keywords
        context_keywords = context_tokens & keywords

        # Score based on keyword presence and overlap
        keyword_overlap = len(paper_keywords & context_keywords)
        total_keywords = len(paper_keywords | context_keywords)

        if total_keywords == 0:
            return 0.0

        # Basic overlap score
        overlap_score = keyword_overlap / total_keywords

        # Boost for strong keyword presence in both
        if len(paper_keywords) > 0 and len(context_keywords) > 0:
            overlap_score *= 1.2

        # Boost for multiple matching keywords
        if keyword_overlap > 2:
            overlap_score *= 1.1

        return min(overlap_score, 1.0)

    def _apply_relevance_factors(self, base_score: float, paper: Paper,
                                research_context: str) -> float:
        """Apply additional relevance factors to the base score.

        Args:
            base_score: Base relevance score
            paper: Paper being scored
            research_context: Research context

        Returns:
            Adjusted relevance score
        """
        adjusted_score = base_score

        # Factor 1: Existing relevance score from paper
        if hasattr(paper, 'relevance_score') and paper.relevance_score > 0:
            adjusted_score = (adjusted_score + paper.relevance_score) / 2

        # Factor 2: Recent papers get slight boost
        if paper.year and paper.year >= 2020:
            adjusted_score *= 1.05

        # Factor 3: High-impact journals (simple heuristic)
        if paper.journal and any(term in paper.journal.lower() for term in
                                ['nature', 'science', 'cell', 'nejm']):
            adjusted_score *= 1.1

        # Factor 4: DOI presence indicates peer review
        if paper.doi:
            adjusted_score *= 1.02

        # Factor 5: Title similarity to research context
        if paper.title:
            title_similarity = self._calculate_text_similarity(
                paper.title.lower(), research_context.lower()
            )
            adjusted_score += title_similarity * 0.1

        return adjusted_score

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity between two strings.

        Args:
            text1: First text string
            text2: Second text string

        Returns:
            Similarity score between 0.0 and 1.0
        """
        tokens1 = set(re.findall(r'\b\w+\b', text1))
        tokens2 = set(re.findall(r'\b\w+\b', text2))

        if not tokens1 or not tokens2:
            return 0.0

        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)

        return intersection / union if union > 0 else 0.0

    def _calculate_selection_confidence(self, scored_papers: List[tuple],
                                       max_papers: int) -> float:
        """Calculate confidence in the paper selection.

        Args:
            scored_papers: List of (paper, score) tuples, sorted by score
            max_papers: Maximum number of papers to select

        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not scored_papers:
            return 1.0  # High confidence in empty selection

        if len(scored_papers) <= max_papers:
            return 1.0  # All papers included

        # Look at score distribution
        selected_scores = [score for _, score in scored_papers[:max_papers]]
        excluded_scores = [score for _, score in scored_papers[max_papers:]]

        if not selected_scores or not excluded_scores:
            return 0.9

        # High confidence if there's a clear gap between selected and excluded
        min_selected = min(selected_scores)
        max_excluded = max(excluded_scores)

        score_gap = min_selected - max_excluded

        # High confidence if selected papers have consistently high scores
        avg_selected = sum(selected_scores) / len(selected_scores)

        # Combine factors
        gap_confidence = min(score_gap * 2 + 0.5, 1.0)  # Score gap contribution
        quality_confidence = min(avg_selected * 1.2, 1.0)  # Average quality contribution

        # Final confidence is weighted average
        final_confidence = (gap_confidence * 0.6 + quality_confidence * 0.4)

        return max(final_confidence, 0.5)  # Minimum confidence of 0.5