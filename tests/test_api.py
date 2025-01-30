import pytest
# In all test files, change imports to:
from src.data_preprocessing import DataPreprocessor
from src.embed_store import VectorStore
from src.app import app, init_db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        init_db()  # Initialize test DB
        yield client

def test_chat_endpoint(client):
    response = client.post('/chat', json={'query': 'What is Apollo?'})
    assert response.status_code == 200
    assert 'answer' in response.json
    assert 'sources' in response.json

def test_history_endpoint(client):
    response = client.get('/history')
    assert response.status_code == 200
    assert isinstance(response.json, list)