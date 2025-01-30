import pytest

from src.data_preprocessing import DataPreprocessor
from src.embed_store import VectorStore
from src.app import app, init_db

@pytest.fixture
def vector_store():
    vs = VectorStore()
    vs.load_data()
    vs.create_index()
    return vs

def test_retrieval(vector_store):
    results = vector_store.search("moon landing", k=2)
    assert len(results) == 2, "Should return 2 results"
    assert all('apollo' in result['title'].lower() for result in results), "Should return Apollo-related content"