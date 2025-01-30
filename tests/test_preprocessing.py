import pytest
from src.data_preprocessing import DataPreprocessor
from src.embed_store import VectorStore
from src.app import app, init_db

def test_chunking():
    preprocessor = DataPreprocessor()
    test_text = " ".join(["word"] * 500)  # 500-word text
    chunks = preprocessor.chunk_text(test_text)
    assert 2 <= len(chunks) <= 3, "Should create 2-3 chunks"
    assert all(200 <= len(chunk.split()) <= 300 for chunk in chunks)

def test_data_loading():
    preprocessor = DataPreprocessor()
    chunks = preprocessor.process_all_sources()
    assert len(chunks) > 20, "Should process reasonable number of chunks"