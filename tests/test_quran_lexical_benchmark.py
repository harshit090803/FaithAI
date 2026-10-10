
import time

from rag.retrieval.quran_lexical_retriever import QuranLexicalRetriever


BENCHMARKS = [
    {
        "concept": "Patience",
        "query": "الصبر",
        "targets": {
            "quran.2.153",
            "quran.2.155",
            "quran.2.156",
            "quran.2.157",
            "quran.3.200",
            "quran.16.127",
            "quran.12.18",
            "quran.12.83",
            "quran.42.43",
            "quran.46.35",
            "quran.103.3",
        },
    },
    {
        "concept": "Hardship",
        "query": "الشدّة",
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
        "concept": "Forgiveness",
        "query": "المغفرة",
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
        "concept": "Prayer",
        "query": "الصلاة",
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


def evaluate(retriever, query, targets, limit=20):
    start = time.perf_counter()
    results = retriever.retrieve(query, limit=limit)
    latency_ms = (time.perf_counter() - start) * 1000

    result_ids = [
        result.passage.passage_id
        for result in results
    ]

    top5 = result_ids[:5]
    top10 = result_ids[:10]

    hits5 = sum(pid in targets for pid in top5)
    hits10 = sum(pid in targets for pid in top10)

    # Precision uses the number actually returned.
    precision5 = hits5 / 5
    precision10 = hits10 / 10

    # Recall is measured only against our listed target examples.
    recall5 = hits5 / len(targets)
    recall10 = hits10 / len(targets)

    reciprocal_rank = 0.0

    for rank, pid in enumerate(result_ids, start=1):
        if pid in targets:
            reciprocal_rank = 1.0 / rank
            break

    return {
        "results": results,
        "latency_ms": latency_ms,
        "hits5": hits5,
        "hits10": hits10,
        "precision5": precision5,
        "precision10": precision10,
        "recall5": recall5,
        "recall10": recall10,
        "mrr": reciprocal_rank,
    }


def run_benchmark():
    print()
    print("=" * 68)
    print("FaithAI — ARABIC LEXICAL RETRIEVAL BENCHMARK")
    print("=" * 68)

    start = time.perf_counter()
    retriever = QuranLexicalRetriever()
    build_time = time.perf_counter() - start

    print(f"Corpus passages : {retriever.document_count}")
    print(f"Index vocabulary: {retriever.vocabulary_size}")
    print(f"Index build time: {build_time:.2f}s")

    aggregate = {
        "precision5": [],
        "recall10": [],
        "mrr": [],
    }

    for benchmark in BENCHMARKS:
        concept = benchmark["concept"]
        query = benchmark["query"]
        targets = benchmark["targets"]

        report = evaluate(
            retriever,
            query,
            targets,
            limit=20,
        )

        aggregate["precision5"].append(report["precision5"])
        aggregate["recall10"].append(report["recall10"])
        aggregate["mrr"].append(report["mrr"])

        print()
        print("-" * 68)
        print(f"CONCEPT: {concept}")
        print(f"Arabic query: {query}")
        print(f"Known target examples: {len(targets)}")
        print(f"Latency: {report['latency_ms']:.2f} ms")
        print(f"Precision@5: {report['precision5']:.3f}")
        print(f"Precision@10: {report['precision10']:.3f}")
        print(f"Recall@5: {report['recall5']:.3f}")
        print(f"Recall@10: {report['recall10']:.3f}")
        print(f"Reciprocal rank: {report['mrr']:.3f}")

        print("\nTop 10 results:")

        for rank, result in enumerate(report["results"][:10], start=1):
            pid = result.passage.passage_id
            marker = " [KNOWN TARGET]" if pid in targets else ""

            print(
                f"{rank:2}. {result.reference:16} "
                f"score={result.score:.3f}{marker}"
            )

    print()
    print("=" * 68)
    print("AGGREGATE RESULTS")
    print("=" * 68)

    for metric, values in aggregate.items():
        average = sum(values) / len(values) if values else 0.0
        print(f"Mean {metric}: {average:.3f}")

    print()
    print(
        "Note: target sets are manually selected examples, "
        "not exhaustive lists of every relevant verse."
    )
    print(
        "Lexical scores measure ranking signals, "
        "not theological truth or certainty."
    )


if __name__ == "__main__":
    run_benchmark()
