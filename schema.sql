-- schema.sql
CREATE DATABASE IF NOT EXISTS rag_chatbot;
USE rag_chatbot;

CREATE TABLE IF NOT EXISTS chat_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50),
    timestamp DATETIME NOT NULL,
    role VARCHAR(10) NOT NULL,
    content TEXT NOT NULL
);