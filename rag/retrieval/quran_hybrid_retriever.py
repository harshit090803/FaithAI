
"""Hybrid Qur'an retrieval with three ranking channels.

Channels:
1. Direct lexical retrieval.
2. Expanded lexical retrieval.
3. Reviewed concept-term retrieval.

Direct and expanded lexical rankings are merged into one lexical signal.
Concept retrieval contributes an independent ranking signal.
Original evidence objects are preserved for citation integrity.
"""

import math
from dataclasses import dataclass
from typing import Dict, List, Optional

from rag.retrieval.evidence import EvidenceResult
from rag.retrieval.quran_lexical_retriever import (
    ArabicNormalizer,
    QuranLexicalRetriever,
)


@dataclass(frozen=True)
class HybridQuranResult:
    """Retrieved evidence and hybrid ranking metadata."""

    evidence: EvidenceResult
    fusion_score: float
    lexical_rank: Optional[int]
    concept_rank: Optional[int]

    @property
    def passage(self):
        return self.evidence.passage

    @property
    def score(self) -> float:
        return self.fusion_score


class QuranHybridRetriever:
    """Combine lexical retrieval with reviewed concept-term retrieval."""

    CONCEPT_EXPANSIONS = {
        "المغفرة": {
            "العفو": 1.00,
            "الصفح": 1.00,
            "ليعفوا": 0.90,
            "ليصفحوا": 0.90,
            "يغفر": 0.80,
            "غفور": 0.70,
        },
        "الشدة": {
            "المصيبة": 0.90,
            "البلاء": 0.90,
            "الابتلاء": 0.85,
            "الضراء": 0.80,
            "العسر": 0.80,
            "الخوف": 0.60,
            "الجوع": 0.60,
            "النقص": 0.60,
        },
        "الصبر": {
            "الصابرين": 0.90,
            "الصابرون": 0.90,
            "صبروا": 0.85,
            "اصبر": 0.80,
            "تصبروا": 0.80,
        },
        # ArabicNormalizer canonicalizes الصلاة to الصلوة.
        "الصلوة": {
            "صلوة": 0.80,
            "يقيمون": 0.60,
        },
    }

    def __init__(
        self,
        lexical_retriever=None,
        concept_expansions=None,
        rrf_k: int = 60,
        lexical_weight: float = 1.0,
        concept_weight: float = 0.70,
    ):
        """Initialize the retriever.

        Args:
            lexical_retriever:
                Existing lexical retriever. Injectable for testing.
            concept_expansions:
                Optional mapping of query concepts to weighted terms.
            rrf_k:
                Positive RRF smoothing constant.
            lexical_weight:
                Weight for the merged lexical ranking.
            concept_weight:
                Weight for the concept ranking.
        """
        if (
            not isinstance(rrf_k, int)
            or isinstance(rrf_k, bool)
            or rrf_k < 1
        ):
            raise ValueError("rrf_k must be a positive integer")

        for name, weight in (
            ("lexical_weight", lexical_weight),
            ("concept_weight", concept_weight),
        ):
            if (
                isinstance(weight, bool)
                or not isinstance(weight, (int, float))
                or not math.isfinite(weight)
                or weight < 0
            ):
                raise ValueError(
                    f"{name} must be a finite, non-negative number"
                )

        self.lexical = (
            lexical_retriever
            if lexical_retriever is not None
            else QuranLexicalRetriever()
        )

        self.concept_expansions = (
            concept_expansions
            if concept_expansions is not None
            else self.CONCEPT_EXPANSIONS
        )

        self.rrf_k = rrf_k
        self.lexical_weight = float(lexical_weight)
        self.concept_weight = float(concept_weight)

    @staticmethod
    def _passage_id(result) -> str:
        """Extract a stable passage identifier."""
        passage = result.passage

        if isinstance(passage, dict):
            passage_id = (
                passage.get("id")
                or passage.get("passage_id")
            )
        else:
            passage_id = (
                getattr(passage, "passage_id", None)
                or getattr(passage, "id", None)
            )

        if passage_id is None:
            raise ValueError(
                "Retrieved passage has no id or passage_id"
            )

        return str(passage_id)

    @staticmethod
    def _query_tokens(query: str) -> List[str]:
        normalized = ArabicNormalizer.normalize(query)
        return normalized.split()

    def _concept_terms(self, query: str) -> Dict[str, float]:
        """Return reviewed expansion terms for concepts in the query."""
        query_tokens = set(self._query_tokens(query))
        terms: Dict[str, float] = {}

        for concept, expansions in self.concept_expansions.items():
            normalized_concept = ArabicNormalizer.normalize(concept)

            if normalized_concept not in query_tokens:
                continue

            for term, weight in expansions.items():
                normalized_term = ArabicNormalizer.normalize(term)

                if not normalized_term:
                    continue

                if (
                    isinstance(weight, bool)
                    or not isinstance(weight, (int, float))
                    or not math.isfinite(weight)
                    or weight < 0
                ):
                    raise ValueError(
                        f"Invalid weight for concept term {term!r}"
                    )

                if weight > 0:
                    terms[normalized_term] = max(
                        terms.get(normalized_term, 0.0),
                        float(weight),
                    )

        return terms

    def retrieve(
        self,
        query: str,
        limit: int = 5,
        candidate_limit: Optional[int] = None,
    ) -> List[HybridQuranResult]:
        """Retrieve candidates and fuse their rankings."""
        if not isinstance(query, str):
            raise TypeError("query must be a string")

        if (
            not isinstance(limit, int)
            or isinstance(limit, bool)
            or limit < 1
        ):
            raise ValueError("limit must be a positive integer")

        if not query.strip():
            return []

        if candidate_limit is None:
            pool_size = max(limit * 5, 20)
        else:
            if (
                not isinstance(candidate_limit, int)
                or isinstance(candidate_limit, bool)
                or candidate_limit < 1
            ):
                raise ValueError(
                    "candidate_limit must be a positive integer"
                )
            pool_size = candidate_limit

        evidence_by_id = {}
        direct_ranks = {}
        expanded_ranks = {}
        concept_scores: Dict[str, float] = {}

        # Channel A: direct lexical retrieval.
        direct_results = self.lexical.retrieve(
            query,
            limit=pool_size,
            include_expansions=False,
        )

        for rank, result in enumerate(direct_results, start=1):
            passage_id = self._passage_id(result)
            evidence_by_id.setdefault(passage_id, result)
            direct_ranks.setdefault(passage_id, rank)

        # Channel B: expanded lexical retrieval.
        expanded_results = self.lexical.retrieve(
            query,
            limit=pool_size,
            include_expansions=True,
        )

        for rank, result in enumerate(expanded_results, start=1):
            passage_id = self._passage_id(result)
            evidence_by_id.setdefault(passage_id, result)
            expanded_ranks.setdefault(passage_id, rank)

        # Channel C: independently search reviewed concept terms.
        # Each term contributes a weighted reciprocal-rank score.
        for term, weight in self._concept_terms(query).items():
            term_results = self.lexical.retrieve(
                term,
                limit=pool_size,
                include_expansions=False,
            )

            for rank, result in enumerate(term_results, start=1):
                passage_id = self._passage_id(result)
                evidence_by_id.setdefault(passage_id, result)

                contribution = weight / (self.rrf_k + rank)

                concept_scores[passage_id] = (
                    concept_scores.get(passage_id, 0.0)
                    + contribution
                )

        # Rank concept results by their accumulated weighted scores.
        ranked_concepts = sorted(
            concept_scores,
            key=lambda passage_id: (
                -concept_scores[passage_id],
                passage_id,
            ),
        )

        concept_ranks = {
            passage_id: rank
            for rank, passage_id in enumerate(
                ranked_concepts,
                start=1,
            )
        }

        # Final fusion: merge the two lexical rankings using the best
        # available rank, then add the independent concept contribution.
        fused = []

        for passage_id, evidence in evidence_by_id.items():
            direct_rank = direct_ranks.get(passage_id)
            expanded_rank = expanded_ranks.get(passage_id)
            concept_rank = concept_ranks.get(passage_id)

            lexical_candidates = [
                rank
                for rank in (direct_rank, expanded_rank)
                if rank is not None
            ]

            best_lexical_rank = (
                min(lexical_candidates)
                if lexical_candidates
                else None
            )

            fusion_score = 0.0

            if best_lexical_rank is not None:
                fusion_score += self.lexical_weight / (
                    self.rrf_k + best_lexical_rank
                )

            if concept_rank is not None:
                fusion_score += self.concept_weight / (
                    self.rrf_k + concept_rank
                )

            fused.append(
                HybridQuranResult(
                    evidence=evidence,
                    fusion_score=fusion_score,
                    lexical_rank=best_lexical_rank,
                    concept_rank=concept_rank,
                )
            )

        fused.sort(
            key=lambda result: (
                -result.fusion_score,
                self._passage_id(result.evidence),
            )
        )

        return fused[:limit]
