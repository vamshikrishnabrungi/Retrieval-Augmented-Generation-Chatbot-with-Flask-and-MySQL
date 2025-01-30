# RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot that provides information about space exploration and NASA missions. The system uses a vector database for semantic search and stores chat history in MySQL and retrives information using llm

## Setup

1. Clone the repository
2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3.Install these in your env
conda create -n ragbot python=3.9
conda activate ragbot
conda install -c conda-forge faiss-cpu
pip install scikit-learn

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Set up MySQL:
- Create a new database named `rag_chatbot`
- Create a `.env` file with the following variables:
```
DB_HOST=localhost
DB_USER=your_username
DB_PASSWORD=dd123
DB_NAME=rag_chatbot
```

## Running the Application

1. First, run the data preprocessing:
```bash
python data_preprocessing.py
```

2. Create and save the vector index:
```bash
python embed_store.py
```
3. Run the Sql commands
mysql -u root -p
enter the password
CREATE DATABASE rag_chatbot;
SHOW DATABASES;
USE rag_chatbot;
SHOW TABLES;
Exit


4. Start the Flask application:
```bash
python app.py
```

## API Endpoints

### POST /chat
Send a chat message:

Open another terminal 

```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Tell me about the Apollo missions"}'
```

### GET /history
Retrieve chat history:
```bash
curl http://localhost:5000/history
```

## Testing

The application includes basic testing in each module. You can run individual files to test their functionality:

- `data_preprocessing.py`: Tests data fetching and processing
- `embed_store.py`: Tests vector storage and retrieval
- `app.py`: Tests the Flask API endpoints

## Project Structure

- `data_preprocessing.py`: Handles fetching and processing of NASA mission data
- `embed_store.py`: Manages vector embeddings and FAISS index
- `app.py`: Main Flask application with RAG chatbot implementation
- `requirements.txt`: Project dependencies
- `.env`: Environment variables (not included in repository)

## Notes

- The chatbot uses NASA mission data as its knowledge base
- Embeddings are created using the `all-MiniLM-L6-v2` model
- Text generation uses the GPT-2 model for lightweight local inference
- FAISS is used for efficient vector similarity search
