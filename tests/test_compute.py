from orbit.compute import (
    ComputeDevice,
    ComputeScheduler,
    HashEmbeddingProvider,
    ModelRequirement,
    Reranker,
)


def test_scheduler_falls_back_when_gpu_vram_is_insufficient() -> None:
    scheduler = ComputeScheduler(
        [
            ComputeDevice("cpu", "cpu", None, "python"),
            ComputeDevice("small-gpu", "gpu", 4.0, "cuda"),
        ]
    )

    selected = scheduler.select(ModelRequirement("large", 8.0))

    assert selected.kind == "cpu"


def test_hash_embeddings_and_reranking_are_deterministic() -> None:
    embeddings = HashEmbeddingProvider(dimensions=16)
    assert embeddings.embed("same text") == embeddings.embed("same text")

    ranked = Reranker().rank(
        "research source",
        ["unrelated text", "research source with evidence"],
    )
    assert ranked[0][1] == "research source with evidence"