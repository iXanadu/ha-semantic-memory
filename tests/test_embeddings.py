"""Test embedding quality and similarity thresholds."""

import numpy as np
import pytest

from server.embeddings import embed


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


@pytest.mark.asyncio
async def test_embedding_dimension(services):
    vec = await embed("test text")
    assert vec.shape == (768,)


@pytest.mark.asyncio
async def test_similar_concepts_high_similarity(services):
    """Semantically related texts should have high cosine similarity."""
    vec1 = await embed("my location Portland OR home address")
    vec2 = await embed("where do I live")
    sim = cosine_sim(vec1, vec2)
    assert sim > 0.35, f"Expected > 0.35, got {sim}"


@pytest.mark.asyncio
async def test_wife_name_similarity(services):
    vec1 = await embed("wife name Sarah spouse family")
    vec2 = await embed("what is my wife's name")
    sim = cosine_sim(vec1, vec2)
    assert sim > 0.35, f"Expected > 0.35, got {sim}"


@pytest.mark.asyncio
async def test_unrelated_concepts_low_similarity(services):
    """Unrelated texts should have lower similarity."""
    vec1 = await embed("my favorite pizza topping is pepperoni")
    vec2 = await embed("quantum mechanics wave function collapse")
    sim = cosine_sim(vec1, vec2)
    assert sim < 0.5, f"Expected < 0.5 for unrelated, got {sim}"
