from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
import json


# ============================================================
# Corpus Manifest
# ============================================================


@dataclass
class CorpusManifest:
    """
    Describes a religious corpus before it enters the
    FaithAI ingestion pipeline.

    The manifest stores provenance and licensing metadata.
    It does not contain the actual religious text.
    """

    corpus_id: str
    title: str
    religion: str
    tradition: Optional[str] = None

    source_type: str = "scripture"

    original_language: Optional[str] = None
    languages: List[str] = field(
        default_factory=list
    )

    author: Optional[str] = None
    translator: Optional[str] = None

    publisher: Optional[str] = None
    edition: Optional[str] = None
    publication_year: Optional[int] = None

    source_url: Optional[str] = None

    license: Optional[str] = None
    copyright_status: Optional[str] = None

    local_path: Optional[str] = None

    description: Optional[str] = None

    tags: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, str] = field(
        default_factory=dict
    )


# ============================================================
# Corpus Manifest Registry
# ============================================================


class CorpusManifestRegistry:
    """
    Registry containing all FaithAI corpus manifests.
    """

    def __init__(self) -> None:
        self.corpora: Dict[
            str, CorpusManifest
        ] = {}

    # ========================================================
    # Add
    # ========================================================

    def add_corpus(
        self,
        corpus: CorpusManifest,
    ) -> bool:
        """
        Validate and add a corpus manifest.
        """

        errors = self.validate(corpus)

        if errors:
            raise ValueError(
                "Invalid corpus manifest:\n"
                + "\n".join(errors)
            )

        if corpus.corpus_id in self.corpora:
            raise ValueError(
                f"Corpus already exists: "
                f"{corpus.corpus_id}"
            )

        self.corpora[
            corpus.corpus_id
        ] = corpus

        return True

    # ========================================================
    # Update
    # ========================================================

    def update_corpus(
        self,
        corpus: CorpusManifest,
    ) -> None:
        """
        Update an existing corpus manifest.
        """

        if corpus.corpus_id not in self.corpora:
            raise KeyError(
                f"Corpus does not exist: "
                f"{corpus.corpus_id}"
            )

        errors = self.validate(corpus)

        if errors:
            raise ValueError(
                "Invalid corpus manifest:\n"
                + "\n".join(errors)
            )

        self.corpora[
            corpus.corpus_id
        ] = corpus

    # ========================================================
    # Retrieve
    # ========================================================

    def get_corpus(
        self,
        corpus_id: str,
    ) -> Optional[CorpusManifest]:
        """
        Retrieve a corpus by ID.
        """

        return self.corpora.get(
            corpus_id
        )

    # ========================================================
    # Remove
    # ========================================================

    def remove_corpus(
        self,
        corpus_id: str,
    ) -> None:
        """
        Remove a corpus manifest.
        """

        if corpus_id not in self.corpora:
            raise KeyError(
                f"Corpus does not exist: "
                f"{corpus_id}"
            )

        del self.corpora[
            corpus_id
        ]

    # ========================================================
    # Filtering
    # ========================================================

    def list_by_religion(
        self,
        religion: str,
    ) -> List[CorpusManifest]:
        """
        Return corpora belonging to a religion.
        """

        religion = religion.strip().lower()

        return [
            corpus
            for corpus in self.corpora.values()
            if corpus.religion.lower()
            == religion
        ]

    def list_by_language(
        self,
        language: str,
    ) -> List[CorpusManifest]:
        """
        Return corpora containing a language.
        """

        language = language.strip().lower()

        return [
            corpus
            for corpus in self.corpora.values()
            if any(
                item.lower() == language
                for item in corpus.languages
            )
            or (
                corpus.original_language
                and corpus.original_language.lower()
                == language
            )
        ]

    # ========================================================
    # Validation
    # ========================================================

    def validate(
        self,
        corpus: CorpusManifest,
    ) -> List[str]:
        """
        Validate required corpus metadata.

        Returns a list of validation errors.
        An empty list means the manifest is valid.
        """

        errors: List[str] = []

        if not corpus.corpus_id.strip():
            errors.append(
                "corpus_id cannot be empty"
            )

        if not corpus.title.strip():
            errors.append(
                "title cannot be empty"
            )

        if not corpus.religion.strip():
            errors.append(
                "religion cannot be empty"
            )

        if not corpus.source_type.strip():
            errors.append(
                "source_type cannot be empty"
            )

        if not corpus.languages:
            errors.append(
                "languages must contain at least "
                "one language"
            )

        if corpus.publication_year is not None:
            if (
                corpus.publication_year < 0
                or corpus.publication_year > 2100
            ):
                errors.append(
                    "publication_year is outside "
                    "the supported range"
                )

        return errors

    # ========================================================
    # JSON Serialization
    # ========================================================

    def to_dict(
        self,
        corpus_id: str,
    ) -> Dict:
        """
        Convert a corpus manifest to a dictionary.
        """

        corpus = self.get_corpus(
            corpus_id
        )

        if corpus is None:
            raise KeyError(
                f"Corpus does not exist: "
                f"{corpus_id}"
            )

        return asdict(corpus)

    def save_json(
        self,
        path: str,
    ) -> None:
        """
        Save all corpus manifests to a JSON file.
        """

        output_path = Path(path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        data = {
            corpus_id: asdict(corpus)
            for corpus_id, corpus
            in self.corpora.items()
        }

        with output_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=4,
            )

    # ========================================================
    # Load JSON
    # ========================================================

    def load_json(
        self,
        path: str,
    ) -> None:
        """
        Load corpus manifests from a JSON file.
        """

        input_path = Path(path)

        if not input_path.exists():
            raise FileNotFoundError(
                f"Manifest file not found: "
                f"{path}"
            )

        with input_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        for corpus_id, values in data.items():
            corpus = CorpusManifest(
                **values
            )

            self.corpora[
                corpus_id
            ] = corpus

    # ========================================================
    # Statistics
    # ========================================================

    def statistics(
        self,
    ) -> Dict[str, int]:
        """
        Return registry statistics.
        """

        return {
            "total_corpora": len(
                self.corpora
            )
        }


# ============================================================
# Demonstration / Test
# ============================================================


if __name__ == "__main__":

    registry = CorpusManifestRegistry()

    # --------------------------------------------------------
    # Structural test corpus
    # --------------------------------------------------------

    quran_corpus = CorpusManifest(
        corpus_id="islam.quran.arabic",
        title="The Qur'an",
        religion="islam",
        tradition="islam",
        source_type="scripture",
        original_language="Arabic",
        languages=[
            "Arabic"
        ],
        copyright_status=(
            "To be verified before redistribution"
        ),
        local_path=(
            "data/islam/raw/quran"
        ),
        description=(
            "Manifest describing the Arabic "
            "Qur'an corpus."
        ),
        tags=[
            "islam",
            "quran",
            "arabic",
            "scripture",
        ],
    )

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    errors = registry.validate(
        quran_corpus
    )

    if errors:

        print(
            "Corpus validation failed:"
        )

        for error in errors:
            print(
                f"- {error}"
            )

    else:

        print(
            "✓ Corpus manifest is valid."
        )

        registry.add_corpus(
            quran_corpus
        )

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    print("=" * 60)
    print("FaithAI Corpus Manifest Registry")
    print("=" * 60)

    stats = registry.statistics()

    print(
        f"Total corpora: "
        f"{stats['total_corpora']}"
    )

    # --------------------------------------------------------
    # Display corpus
    # --------------------------------------------------------

    print("\nRegistered corpora:")

    for corpus in registry.corpora.values():

        print(
            f"- {corpus.title}"
            f" [{corpus.religion}]"
            f" ({corpus.corpus_id})"
        )

        print(
            f"  Original language: "
            f"{corpus.original_language}"
        )

        print(
            f"  Source type: "
            f"{corpus.source_type}"
        )

        print(
            f"  Local path: "
            f"{corpus.local_path}"
        )

    # --------------------------------------------------------
    # Religion filtering
    # --------------------------------------------------------

    print("\nIslamic corpora:")

    for corpus in registry.list_by_religion(
        "islam"
    ):

        print(
            f"- {corpus.title}"
        )

    # --------------------------------------------------------
    # JSON serialization test
    # --------------------------------------------------------

    test_path = (
        "data/islam/raw/manifest.json"
    )

    registry.save_json(
        test_path
    )

    print(
        f"\n✓ Manifest saved to: "
        f"{test_path}"
    )

    # --------------------------------------------------------
    # Load test
    # --------------------------------------------------------

    loaded_registry = (
        CorpusManifestRegistry()
    )

    loaded_registry.load_json(
        test_path
    )

    print(
        "✓ Manifest successfully "
        "loaded back from JSON."
    )

    print(
        "\nCorpus manifest test completed."
    )