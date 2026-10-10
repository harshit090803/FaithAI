
import math
import re
import unicodedata
from collections import Counter, defaultdict
from typing import Dict, List, Set

from rag.retrieval.evidence import EvidenceBuilder, EvidenceResult
from rag.retrieval.quran_repository import QuranRepository


class ArabicNormalizer:
    """
    Search-only Arabic normalisation.

    Original Tanzil text is never modified.
    Canonical forms are used only for indexing and querying.
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

    # Search-only spelling mappings.
    CANONICAL_TOKEN_FORMS = {
        "الصلاة": "الصلوة",
        "صلاة": "صلوة",
    }

    @classmethod
    def normalize(cls, text: str) -> str:
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        text = unicodedata.normalize("NFC", text)
        text = cls.DIACRITICS.sub("", text)
        text = text.translate(cls.REPLACEMENTS)

        text = re.sub(
            r"[^\u0621-\u063A\u0641-\u064A\s]",
            " ",
            text,
        )

        return " ".join(text.split())

    @classmethod
    def canonicalize_token(cls, token: str) -> str:
        """Map reviewed spelling variants to search forms."""
        return cls.CANONICAL_TOKEN_FORMS.get(token, token)

    @classmethod
    def tokenize(cls, text: str) -> List[str]:
        normalized = cls.normalize(text)

        return [
            cls.canonicalize_token(token)
            for token in normalized.split()
        ]


class QuranLexicalRetriever:
    """
    Lightweight Arabic lexical retriever for the Qur'an corpus.

    Features:
    - Search-only Arabic normalisation
    - Explicit canonical spelling forms
    - Conservative attached-prefix variants
    - Inverted index and cached term frequencies
    - Precomputed document-token variant mappings
    - IDF-weighted lexical scoring
    - Controlled query expansion
    - Cited evidence results

    This is not a full Arabic morphological analyser.
    Expansion weights are heuristic retrieval signals,
    not theological certainty or proof of synonymy.
    """

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

    # Prototype search expansions.
    # These are retrieval hints, not exact synonym declarations.
    # Weights require evaluation against reviewed relevance judgments.
    QUERY_EXPANSIONS = {
        "الشدة": {
            "المصيبة": 0.45,
            "الباساء": 0.45,
            "الضراء": 0.45,
            "العسر": 0.45,
            "البلاء": 0.35,
            "الابتلاء": 0.35,
            "تبلون": 0.35,
            "يخفف": 0.30,
            "الخوف": 0.25,
            "الجوع": 0.25,
            "النقص": 0.25,
            "تصبروا": 0.25,
        },
        "المغفرة": {
            "مغفرة": 0.45,
            "غفور": 0.40,
            "غفورا": 0.40,
            "استغفروا": 0.40,
            "يستغفر": 0.40,
            "يستغفروا": 0.40,
            "يغفر": 0.40,
            "العفو": 0.35,
            "عفوا": 0.35,
            "العافين": 0.35,
            "ليعفوا": 0.35,
            "ليصفحوا": 0.35,
            "الصفح": 0.30,
        },
    }

    def __init__(self, repository=None):
        self.repository = repository or QuranRepository()

        self.inverted_index: Dict[str, Set[str]] = defaultdict(set)
        self.document_frequency: Counter = Counter()
        self.document_lengths: Dict[str, int] = {}
        self.document_tokens: Dict[str, List[str]] = {}
        self.term_frequencies: Dict[str, Counter] = {}

        # IMPORTANT: initialise this BEFORE _build_index().
        self.document_variant_tokens: Dict[
            str, Dict[str, Set[str]]
        ] = {}

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
        Generate conservative attached-prefix variants.

        Example:
            بالصبر -> {"بالصبر", "صبر"}

        These are search variants, not a guarantee that
        every generated form is grammatically equivalent.
        """
        variants = {token}
        current = token

        while True:
            matched_prefix = None

            for prefix in cls.PREFIXES:
                if (
                    current.startswith(prefix)
                    and len(current) - len(prefix) >= 3
                ):
                    matched_prefix = prefix
                    break

            if matched_prefix is None:
                break

            current = current[len(matched_prefix):]
            variants.add(current)

        return variants

    def _build_index(self) -> None:
        """Build search indexes without modifying source passages."""
        for passage in self.repository.all():
            passage_id = passage.passage_id

            # Search-normalized tokens; source text remains untouched.
            tokens = ArabicNormalizer.tokenize(passage.text)
            frequencies = Counter(tokens)

            self.document_tokens[passage_id] = tokens
            self.term_frequencies[passage_id] = frequencies
            self.document_lengths[passage_id] = len(tokens)

            indexed_terms = set()
            variant_to_tokens = defaultdict(set)

            # Build each document's variant map and index terms.
            for token in frequencies:
                variants = self._token_variants(token)
                indexed_terms.update(variants)

                for variant in variants:
                    # Add the individual token, not the whole tokens list.
                    variant_to_tokens[variant].add(token)

            self.document_variant_tokens[passage_id] = dict(
                variant_to_tokens
            )

            # Each term's document frequency increments once per passage.
            for term in indexed_terms:
                self.inverted_index[term].add(passage_id)
                self.document_frequency[term] += 1

    def _idf(self, token: str) -> float:
        df = self.document_frequency.get(token, 0)

        if df == 0:
            return 0.0

        return math.log(
            (self.document_count + 1) / (df + 1)
        ) + 1.0
    def _score_document(
    self,
    passage_id: str,
    query_terms,
) -> float:
        frequencies = self.term_frequencies[passage_id]
        variant_map = self.document_variant_tokens[passage_id]

    # Track the strongest contribution assigned to each
    # underlying document token.
        token_contributions = {}

        for query_token, query_weight in query_terms:
            query_variants = self._token_variants(query_token)
            matched_tokens = set()

            for variant in query_variants:
                matched_tokens.update(
                variant_map.get(variant, ())
            )

            for document_token in matched_tokens:
                tf = frequencies[document_token]

                term_score = (
                    (1.0 + math.log(tf))
                    * self._idf(document_token)
                )

                contribution = query_weight * term_score

                token_contributions[document_token] = max(
                token_contributions.get(document_token, 0.0),
                contribution,
                )

        return sum(token_contributions.values())
    def retrieve(
        self,
        query: str,
        limit: int = 5,
        include_expansions : bool = True,
    ) -> List[EvidenceResult]:
        if not isinstance(query, str):
            raise TypeError("query must be a string")

        if not query.strip() or limit <= 0:
            return []

        query_tokens = ArabicNormalizer.tokenize(query)

        if not query_tokens:
            return []

        # Original query terms retain full weight.
        weighted_terms = {
            token: 1.0
            for token in query_tokens
        }
        if include_expansions:
        # Add explicitly reviewed expansion terms at lower weights.
            for token in query_tokens:
                expansions = self.QUERY_EXPANSIONS.get(token, {})
            

                for expansion, weight in expansions.items():
                    normalized_terms = ArabicNormalizer.tokenize(
                    expansion
                )

                    for normalized_term in normalized_terms:
                        weighted_terms[normalized_term] = max(
                        weighted_terms.get(normalized_term, 0.0),
                        weight,
                    )

        query_terms = list(weighted_terms.items())

        # Find candidate passages through the inverted index.
        candidate_ids = set()

        for token, _weight in query_terms:
            for variant in self._token_variants(token):
                candidate_ids.update(
                    self.inverted_index.get(variant, set())
                )

        scored = []

        for passage_id in candidate_ids:
            score = self._score_document(
                passage_id,
                query_terms,
            )

            if score <= 0:
                continue

            passage = self.repository.get_required(passage_id)

            scored.append(
                EvidenceBuilder.from_passage(
                    passage,
                    score=score,
                    source_title="Tanzil Quran Text — Uthmani",
                    provenance_id="provenance.islam.quran.arabic",
                )
            )

        scored.sort(
            key=lambda result: (
                -result.score,
                result.passage.passage_id,
            )
        )

        return scored[:limit]
