import time

from rag.embeddings.model_config import EmbeddingModelConfig
from rag.embeddings.multilingual_embedder import MultilingualEmbedder
from rag.embeddings.vector_store import InMemoryVectorStore
from rag.retrieval.quran_repository import QuranRepository
from rag.retrieval.quran_semantic_retriever import QuranSemanticRetriever


MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)


# We deliberately use a small, controlled benchmark first.
#
# The target verses are examples where the concept of patience
# is explicitly relevant.
#
# 2:153 -> patience and prayer
# 2:155-157 -> trials and patience
# 3:200 -> patience/perseverance
# 16:127 -> patience
# 94:5-6 -> hardship/ease
EXPECTED_TARGETS = {
    "english": {
        "query": "patience",
        "targets": {
            "quran.2.153",
            "quran.2.155",
            "quran.2.156",
            "quran.2.157",
            "quran.3.200",
            "quran.16.127",
        },
    },
    "hindi": {
        "query": "सब्र",
        "targets": {
            "quran.2.153",
            "quran.2.155",
            "quran.2.156",
            "quran.2.157",
            "quran.3.200",
            "quran.16.127",
        },
    },
    "arabic": {
        "query": "الصبر",
        "targets": {
            "quran.2.153",
            "quran.2.155",
            "quran.2.156",
            "quran.2.157",
            "quran.3.200",
            "quran.16.127",
        },
    },
}


def build_retriever():
    config = EmbeddingModelConfig(
        model_name=MODEL_NAME,
        dimension=384,
    )

    embedder = MultilingualEmbedder(config)
    repository = QuranRepository()

    vector_store = InMemoryVectorStore(dimension=384)

    # Small controlled candidate set.
    candidate_ids = set()

    for targets in EXPECTED_TARGETS.values():
        candidate_ids.update(targets["targets"])

    # Add some control verses from different topics.
    control_ids = {
        "quran.1.1",
        "quran.1.2",
        "quran.112.1",
        "quran.114.1",
        "quran.2.255",
    }

    candidate_ids.update(control_ids)

    passages = []

    for passage_id in sorted(candidate_ids):
        passage = repository.get_required(passage_id)
        passages.append(passage)

    start = time.perf_counter()

    vectors = embedder.embed_batch(
        [passage.text for passage in passages]
    )

    embedding_time = time.perf_counter() - start

    for passage, vector in zip(passages, vectors):
        vector_store.add(passage.passage_id, vector)

    retriever = QuranSemanticRetriever(
        embedder=embedder,
        vector_store=vector_store,
        repository=repository,
    )

    return retriever, embedding_time, len(passages)


def run_benchmark():
    print()
    print("FaithAI Qur'an Semantic Retrieval Benchmark")
    print("=" * 50)

    retriever, embedding_time, candidate_count = build_retriever()

    print(f"Candidate passages : {candidate_count}")
    print(f"Embedding time     : {embedding_time:.3f}s")
    print()

    for language, config in EXPECTED_TARGETS.items():
        query = config["query"]
        targets = config["targets"]

        start = time.perf_counter()

        results = retriever.retrieve(
            query=query,
            limit=10,
        )

        latency = time.perf_counter() - start

        retrieved_ids = [
            result.passage.passage_id
            for result in results
        ]

        hits_at_5 = sum(
            passage_id in targets
            for passage_id in retrieved_ids[:5]
        )

        hits_at_10 = sum(
            passage_id in targets
            for passage_id in retrieved_ids[:10]
        )

        print(f"[{language.upper()}]")
        print(f"Query       : {query}")
        print(f"Latency     : {latency:.4f}s")
        print(f"Hits@5      : {hits_at_5}")
        print(f"Hits@10     : {hits_at_10}")
        print("Results:")

        for rank, result in enumerate(results, start=1):
            marker = " <-- TARGET" if result.passage.passage_id in targets else ""

            print(
                f"  {rank:2d}. "
                f"{result.passage.passage_id:15s} "
                f"score={result.score:.4f}"
                f"{marker}"
            )

        print()


if __name__ == "__main__":
    run_benchmark()