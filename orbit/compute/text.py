"""Dependency-light embeddings and lexical reranking."""

from collections import Counter
import hashlib
import math


class HashEmbeddingProvider:
    """Deterministic CPU embeddings for offline indexing and tests."""

    def __init__(self, dimensions: int = 128) -> None:
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in text.lower().split():
            digest = hashlib.sha256(token.encode()).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            vector[index] += 1.0

        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]


class Reranker:
    """Rank documents by deterministic token overlap with a query."""

    def rank(self, query: str, documents: list[str]) -> list[tuple[float, str]]:
        query_tokens = Counter(query.lower().split())

        scored = []
        for document in documents:
            document_tokens = Counter(document.lower().split())
            overlap = sum(
                min(count, document_tokens[token])
                for token, count in query_tokens.items()
            )
            score = overlap / max(sum(query_tokens.values()), 1)
            scored.append((score, document))

        return sorted(scored, key=lambda result: result[0], reverse=True)