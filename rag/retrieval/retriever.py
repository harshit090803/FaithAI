from abc import ABC, abstractmethod
from typing import List

from .evidence import EvidenceResult


class Retriever(ABC):
    """
    Generic retrieval interface for FaithAI.

    Every retrieval strategy must return EvidenceResult objects.
    """

    @abstractmethod
    def retrieve(
        self,
        query: str,
        limit: int = 5,
    ) -> List[EvidenceResult]:
        """
        Retrieve relevant evidence for a query.
        """
        raise NotImplementedError
