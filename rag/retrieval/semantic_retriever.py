from abc import abstractmethod
from typing import List

from .evidence import EvidenceResult
from .retriever import Retriever


class SemanticRetriever(Retriever):
    """
    Base interface for semantic retrieval.

    Implementations must convert a natural-language query into
    semantically relevant EvidenceResult objects.
    """

    @abstractmethod
    def retrieve(
        self,
        query: str,
        limit: int = 5,
    ) -> List[EvidenceResult]:
        raise NotImplementedError
