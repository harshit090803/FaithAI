
import math
import re
import unicodedata
from collections import Counter, defaultdict
from typing import Dict, List, Set

from rag.retrieval.evidence import EvidenceBuilder, EvidenceResult
from rag.retrieval.quran_repository import QuranRepository


class ArabicNormalizer:
    """
    Normalises Arabic for searching only.

    The original Qur'anic text is never modified.
    This is conservative surface-form normalisation,
    not a complete Arabic morphological analyser.
    """

    DIACRITICS = re.compile(
        r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]"
    )

    REPLACEMENTS = str.maketrans({
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ٱ": "ا",
        "ى": "ي",
        "ؤ": "و",
        "ئ": "ي",
    })

    @classmethod
    def normalize(cls, text: str) -> str:
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        text = unicodedata.normalize("NFC", text)
        text = cls.DIACRITICS.sub("", text)
        text = text.translate(cls.REPLACEMENTS)

        # Preserve Arabic letters and whitespace only.
        text = re.sub(
            r"[^\u0621-\u063A\u0641-\u064A\s]",
            " ",
            text,
        )

        return " ".join(text.split())

    @classmethod
    def tokenize(cls, text: str) -> List[str]:
        return cls.normalize(text).split()


class QuranLexicalRetriever:
    """
    Lightweight lexical retriever for the Arabic Qur'an corpus.

    Features:
    - Inverted index
    - Arabic diacritic normalisation
    - Conservative attached-prefix handling
    - Cached document tokens and term frequencies
    - IDF-weighted lexical scoring
    - Evidence results with citations

    Important:
    This implementation does not perform complete Arabic stemming,
    root extraction, or theological interpretation.
    """

    # Longer prefixes must be checked before shorter prefixes.
    PREFIXES = (
        "وال",
        "بال",
        "كال",
        "فال",
        "ولل",
        "لل",
        "ال",
        "و",
        "ف",
        "ب",
        "ك",
        "ل",
    )

    def __init__(
        self,
        repository=None,
    ):
        self.repository = repository or QuranRepository()

        self.inverted_index: Dict[str, Set[str]] = defaultdict(set)
        self.document_frequency: Counter = Counter()
        self.document_lengths: Dict[str, int] = {}
        self.document_tokens: Dict[str, List[str]] = {}
        self.term_frequencies: Dict[str, Counter] = {}

        self._build_index()

    @property
    def document_count(self) -> int:
        return self.repository.count()

    @property
    def vocabulary_size(self) -> int:
        return len(self.inverted_index)

    @classmethod
    def _token_variants(cls, token: str) -> Set[str]:
        """
        Generate conservative search variants.

        Example:
            بالصبر -> {بالصبر, الصبر, صبر}

        These variants improve surface-form matching. They do not
        establish that two forms are grammatically interchangeable.
        """
        variants = {token}
        current = token

        # Remove an attached prefix iteratively, but conservatively.
        # A minimum remaining length avoids stripping tiny fragments.
        changed = True

        while changed:
            changed = False

            for prefix in cls.PREFIXES:
                if (
                    current.startswith(prefix)
                    and len(current) - len(prefix) >= 3
                ):
                    current = current[len(prefix):]
                    variants.add(current)
                    changed = True
                    break

        # Include the form without the definite article.
        if current.startswith("ال") and len(current) > 4:
            variants.add(current[2:])

        return variants

    def _build_index(self) -> None:
        """Build the inverted index once and cache document statistics."""
        for passage in self.repository.all():
            passage_id = passage.passage_id
            tokens = ArabicNormalizer.tokenize(passage.text)
            frequencies = Counter(tokens)

            self.document_tokens[passage_id] = tokens
            self.term_frequencies[passage_id] = frequencies
            self.document_lengths[passage_id] = len(tokens)

            # Index each document once per searchable variant.
            indexed_terms = set()

            for token in tokens:
                indexed_terms.update(self._token_variants(token))

            for term in indexed_terms:
                self.inverted_index[term].add(passage_id)
                self.document_frequency[term] += 1

    def _idf(self, token: str) -> float:
        """Smoothed inverse document frequency."""
        document_frequency = self.document_frequency.get(token, 0)

        if document_frequency == 0:
            return 0.0

        return math.log(
            (self.document_count + 1)
            / (document_frequency + 1)
        ) + 1.0

    def _score_document(
        self,
        passage_id: str,
        query_tokens: List[str],
    ) -> float:
        """
        Score a candidate using cached document tokens.

        A document token contributes at most once per query token,
        avoiding duplicate boosts from overlapping search variants.
        """
        frequencies = self.term_frequencies[passage_id]
        document_tokens = self.document_tokens[passage_id]

        score = 0.0

        for query_token in query_tokens:
            query_variants = self._token_variants(query_token)
            best_term_score = 0.0

            for document_token in set(document_tokens):
                document_variants = self._token_variants(document_token)

                if query_variants.isdisjoint(document_variants):
                    continue

                term_frequency = frequencies[document_token]

                term_score = (
                    (1.0 + math.log(term_frequency))
                    * self._idf(document_token)
                )

                best_term_score = max(
                    best_term_score,
                    term_score,
                )

            score += best_term_score

        return score

    def retrieve(
        self,
        query: str,
        limit: int = 5,
    ) -> List[EvidenceResult]:
        """
        Retrieve passages matching an Arabic lexical query.

        Returns:
            EvidenceResult objects sorted by descending lexical score.
        """
        if not isinstance(query, str):
            raise TypeError("query must be a string")

        if not query.strip() or limit <= 0:
            return []

        query_tokens = ArabicNormalizer.tokenize(query)

        if not query_tokens:
            return []

        # Retrieve candidates through the same variant logic used
        # during index construction and document scoring.
        candidate_ids: Set[str] = set()

        for token in query_tokens:
            for variant in self._token_variants(token):
                candidate_ids.update(
                    self.inverted_index.get(variant, set())
                )

        scored = []

        for passage_id in candidate_ids:
            score = self._score_document(
                passage_id,
                query_tokens,
            )

            if score <= 0:
                continue

            passage = self.repository.get_required(passage_id)

            evidence = EvidenceBuilder.from_passage(
                passage,
                score=score,
                source_title="Tanzil Quran Text — Uthmani",
                provenance_id="provenance.islam.quran.arabic",
            )

            scored.append(evidence)

        scored.sort(
            key=lambda result: (
                -result.score,
                result.passage.passage_id,
            )
        )

        return scored[:limit]
