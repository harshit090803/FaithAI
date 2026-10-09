from rag.embeddings.model_config import EmbeddingModelConfig
from rag.embeddings.multilingual_embedder import MultilingualEmbedder


MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)


def test_real_multilingual_embedder():
    config = EmbeddingModelConfig(
        model_name=MODEL_NAME,
        dimension=384,
    )

    embedder = MultilingualEmbedder(config)

    vector = embedder.embed("patience")

    assert len(vector) == 384
    assert vector


def test_real_multilingual_embedder_batch():
    config = EmbeddingModelConfig(
        model_name=MODEL_NAME,
        dimension=384,
    )

    embedder = MultilingualEmbedder(config)

    vectors = embedder.embed_batch(
        [
            "patience",
            "सब्र",
            "الصبر",
        ]
    )

    assert len(vectors) == 3

    for vector in vectors:
        assert len(vector) == 384
