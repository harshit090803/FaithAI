import time
from pathlib import Path

from rag.embeddings.model_config import EmbeddingModelConfig
from rag.embeddings.multilingual_embedder import MultilingualEmbedder
from rag.embeddings.vector_store import InMemoryVectorStore
from rag.retrieval.quran_repository import QuranRepository
from rag.retrieval.quran_semantic_retriever import QuranSemanticRetriever


MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)

# These are evaluation queries, not theological judgments.
#
# Each target set contains verses that are expected to be relevant
# to the concept being tested.
BENCHMARKS = [
    {
        "name": "patience",
        "queries": {
            "english": "patience",
            "hindi": "सब्र",
            "arabic": "الصبر",
        },
        "targets": {
            "quran.2.153",
            "quran.2.155",
            "quran.2.156",
            "quran.2.157",
            "quran.3.200",
            "quran.16.127",
        },
    },
    {
        "name": "hardship",
        "queries": {
            "english": "hardship",
            "hindi": "कठिनाई",
            "arabic": "الشدّة",
        },
        "targets": {
            "quran.2.155",
            "quran.2.156",
            "quran.2.214",
            "quran.3.186",
            "quran.4.28",
            "quran.94.5",
            "quran.94.6",
        },
    },
    {
        "name": "forgiveness",
        "queries": {
            "english": "forgiveness",
            "hindi": "माफी",
            "arabic": "المغفرة",
        },
        "targets": {
            "quran.2.199",
            "quran.3.133",
            "quran.3.134",
            "quran.4.110",
            "quran.7.199",
            "quran.24.22",
            "quran.39.53",
        },
    },
    {
        "name": "prayer",
        "queries": {
            "english": "prayer",
            "hindi": "नमाज़",
            "arabic": "الصلاة",
        },
        "targets": {
            "quran.2.43",
            "quran.2.110",
            "quran.2.238",
            "quran.4.103",
            "quran.11.114",
            "quran.17.78",
            "quran.29.45",
        },
    },
]


def build_full_index():
    print("Loading Qur'an repository...")
    repository = QuranRepository()

    print(f"Verses loaded: {repository.count()}")

    config = EmbeddingModelConfig(
        model_name=MODEL_NAME,
        dimension=384,
        batch_size=32,
    )

    print("Loading embedding model...")
    embedder = MultilingualEmbedder(config)

    passages = repository.all()

    print()
    print("Generating embeddings for full corpus...")
    print("-----------------------------------------")

    start = time.perf_counter()

    vectors = embedder.embed_batch(
        [passage.text for passage in passages]
    )

    embedding_time = time.perf_counter() - start

    print(f"Embedding time: {embedding_time:.2f}s")
    print(f"Embeddings generated: {len(vectors)}")

    vector_store = InMemoryVectorStore(
        dimension=384
    )

    print("Building in-memory vector index...")

    index_start = time.perf_counter()

    vector_store.add_batch(
        [
            (passage.passage_id, vector)
            for passage, vector in zip(passages, vectors)
        ]
    )

    index_time = time.perf_counter() - index_start

    print(f"Index build time: {index_time:.2f}s")
    print(f"Vector count: {vector_store.count()}")

    retriever = QuranSemanticRetriever(
        embedder=embedder,
        vector_store=vector_store,
        repository=repository,
    )

    return retriever, embedding_time, index_time


def evaluate_query(
    retriever,
    query,
    targets,
    limit,
):
    start = time.perf_counter()

    results = retriever.retrieve(
        query=query,
        limit=limit,
    )

    latency = time.perf_counter() - start

    retrieved_ids = [
        result.passage.passage_id
        for result in results
    ]

    hits = sum(
        passage_id in targets
        for passage_id in retrieved_ids
    )

    reciprocal_rank = 0.0

    for rank, passage_id in enumerate(
        retrieved_ids,
        start=1,
    ):
        if passage_id in targets:
            reciprocal_rank = 1.0 / rank
            break

    return {
        "results": results,
        "hits": hits,
        "latency": latency,
        "mrr": reciprocal_rank,
    }


def print_results(
    language,
    query,
    evaluation,
):
    results = evaluation["results"]

    print()
    print(f"  [{language.upper()}]")
    print(f"  Query    : {query}")
    print(
        f"  Latency  : "
        f"{evaluation['latency'] * 1000:.2f} ms"
    )
    print(
        f"  MRR      : "
        f"{evaluation['mrr']:.4f}"
    )

    print("  Top 10:")

    for rank, result in enumerate(
        results[:10],
        start=1,
    ):
        print(
            f"    {rank:2d}. "
            f"{result.passage.reference:14s} "
            f"score={result.score:.4f}"
        )


def run_benchmark():
    print()
    print("=" * 70)
    print("FaithAI — FULL QUR'AN SEMANTIC RETRIEVAL BENCHMARK")
    print("=" * 70)

    retriever, embedding_time, index_time = build_full_index()

    print()
    print("=" * 70)
    print("RETRIEVAL EVALUATION")
    print("=" * 70)

    total_queries = 0
    total_mrr = 0.0

    for benchmark in BENCHMARKS:
        print()
        print("-" * 70)
        print(f"CONCEPT: {benchmark['name'].upper()}")
        print("-" * 70)

        targets = benchmark["targets"]

        print(
            "Expected target verses:",
            ", ".join(sorted(targets)),
        )

        for language, query in benchmark["queries"].items():
            total_queries += 1

            evaluation = evaluate_query(
                retriever=retriever,
                query=query,
                targets=targets,
                limit=20,
            )

            total_mrr += evaluation["mrr"]

            print_results(
                language,
                query,
                evaluation,
            )

    average_mrr = (
        total_mrr / total_queries
        if total_queries
        else 0.0
    )

    print()
    print("=" * 70)
    print("BENCHMARK SUMMARY")
    print("=" * 70)

    print(f"Corpus verses       : 6236")
    print(f"Embedding dimension : 384")
    print(f"Embedding time      : {embedding_time:.2f}s")
    print(f"Index build time    : {index_time:.2f}s")
    print(f"Queries tested      : {total_queries}")
    print(f"Average MRR         : {average_mrr:.4f}")

    print()
    print(
        "NOTE: Retrieval scores are ranking signals, "
        "not theological confidence."
    )


if __name__ == "__main__":
    run_benchmark()