from flask import Flask, request, jsonify
import mysql.connector
from datetime import datetime
import os
from dotenv import load_dotenv
from embed_store import VectorStore
from transformers import pipeline

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Database configuration
db_config = {
    'host': os.getenv('DB_HOST', 'mysql'),  # Match service name
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'rag_chatbot'),
    'port': 3306,
    'connect_timeout': 20  # Add timeout
}

# Initialize vector store
print("Initializing vector store...")
vector_store = VectorStore()
vector_store.load_data()
vector_store.load_index()
print("Vector store initialized!")

# Initialize GPT-2 text generation model
generator = pipeline('text-generation', model='gpt2')


def init_db():
    """Initialize database and create tables if they don't exist."""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(50),  # Add user ID support
                timestamp DATETIME,
                role VARCHAR(10),
                content TEXT
            )
        ''')

        conn.commit()
        cursor.close()
        conn.close()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")

def store_message(user_id: str, role: str, content: str):
    """Store a message in the database with user ID."""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute(
            'INSERT INTO chat_history (user_id, timestamp, role, content) VALUES (%s, %s, %s, %s)',
            (user_id, datetime.now(), role, content)
        )

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error storing message: {e}")

def generate_response(query: str, contexts: list) -> str:
    """Generate a response using GPT-2 based on retrieved contexts."""
    if not contexts:
        return "I couldn't find any relevant information. Please try another query."

    # Combine contexts with source attribution
    context_text = ""
    for chunk in contexts:
        source = chunk.get('title', 'Unknown Source')
        context_text += f"From {source}:\n{chunk['text']}\n\n"

    # Truncate context if too long
    if len(context_text) > 1000:
        context_text = context_text[:1000] + "..."

    # Construct prompt for GPT-2
    prompt = f"Query: {query}\nContext: {context_text}\nAnswer:"

    # Generate response using GPT-2
    try:
        response = generator(prompt, max_length=500, temperature=0.7)[0]['generated_text']
        return response.strip()
    except Exception as e:
        print(f"Error generating response: {e}")
        return "Sorry, I encountered an error while generating the response."

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    query = data.get('query')
    user_id = data.get('user_id', 'default_user')  # Default user ID if not provided
    
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    try:
        # Store user message
        store_message(user_id, 'user', query)
        
        # Retrieve relevant chunks
        relevant_chunks = vector_store.search(query, k=3)
        
        # Generate response
        response = generate_response(query, relevant_chunks)
        
        # Store system response
        store_message(user_id, 'system', response)
        
        return jsonify({
            "answer": response,
            "sources": [chunk['source'] for chunk in relevant_chunks]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/history', methods=['GET'])
def get_history():
    user_id = request.args.get('user_id', 'default_user')  # Default user ID if not provided
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            'SELECT * FROM chat_history WHERE user_id = %s ORDER BY timestamp',
            (user_id,)
        )
        history = cursor.fetchall()
        
        # Convert datetime objects to strings for JSON serialization
        for item in history:
            item['timestamp'] = item['timestamp'].isoformat()
        
        cursor.close()
        conn.close()
        
        return jsonify(history)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)