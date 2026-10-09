import json
from pathlib import Path

from knowledge.sources.corpus_manifest import (
    CorpusManifest,
    CorpusManifestRegistry,
)


class ManifestLoader:
    """
    Loads and validates FaithAI CorpusManifest data from JSON.

    The current manifest.json format is a registry mapping:

        {
            "corpus.id": {
                "corpus_id": "corpus.id",
                ...
            }
        }
    """

    def __init__(self):
        self.registry = CorpusManifestRegistry()

    def _read_json(self, file_path: str | Path) -> dict:
        """Read and validate the JSON container."""
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Manifest file does not exist: {path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Manifest path is not a file: {path}"
            )

        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid JSON in manifest: {path}"
            ) from exc

        if not isinstance(data, dict):
            raise ValueError(
                "Manifest JSON must contain an object."
            )

        return data

    def load_all(
        self,
        file_path: str | Path,
    ) -> list[CorpusManifest]:
        """
        Load all corpus manifests from a registry-format JSON file.
        """
        data = self._read_json(file_path)

        manifests = []

        for corpus_id, manifest_data in data.items():

            if not isinstance(manifest_data, dict):
                raise ValueError(
                    f"Manifest entry '{corpus_id}' must be an object."
                )

            try:
                manifest = CorpusManifest(**manifest_data)
            except TypeError as exc:
                raise ValueError(
                    f"Invalid manifest fields for '{corpus_id}': {exc}"
                ) from exc

            if manifest.corpus_id != corpus_id:
                raise ValueError(
                    f"Manifest key '{corpus_id}' does not match "
                    f"corpus_id '{manifest.corpus_id}'."
                )

            errors = self.registry.validate(manifest)

            if errors:
                raise ValueError(
                    f"Invalid corpus manifest '{corpus_id}':\n"
                    + "\n".join(f"- {error}" for error in errors)
                )

            manifests.append(manifest)

        return manifests

    def load(
        self,
        file_path: str | Path,
    ) -> CorpusManifest:
        """
        Load a single corpus manifest.

        Raises ValueError if the file contains zero or multiple
        corpus manifests.
        """
        manifests = self.load_all(file_path)

        if len(manifests) == 0:
            raise ValueError(
                "Manifest file does not contain any corpus manifests."
            )

        if len(manifests) > 1:
            raise ValueError(
                "Manifest file contains multiple corpora. "
                "Use load_all() instead."
            )

        return manifests[0]

    def load_and_register(
        self,
        file_path: str | Path,
    ) -> list[CorpusManifest]:
        """
        Load all manifests and register them in the internal registry.
        """
        manifests = self.load_all(file_path)

        for manifest in manifests:
            added = self.registry.add_corpus(manifest)

            if not added:
                raise ValueError(
                    f"Corpus already registered: {manifest.corpus_id}"
                )

        return manifests