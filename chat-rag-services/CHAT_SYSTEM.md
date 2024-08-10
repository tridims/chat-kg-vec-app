# Chat System Architecture

This document provides an in-depth explanation of the chat system architecture used in the Chat RAG Services project.

## Overview

The chat system is built on a Retrieval-Augmented Generation (RAG) approach, which combines the power of large language models with a knowledge base to provide context-aware and accurate responses. It uses both vector and graph-based search techniques to retrieve relevant context for user queries.

## Key Components

### 1. QAEngine (app/services/processor/completions.py)

The QAEngine is the core component of the chat system. It orchestrates the entire process of generating responses to user queries. Its main responsibilities include:

- Initializing and managing the database connection (Neo4jGraph)
- Utilizing the language model (LLMModel) for processing
- Coordinating with the DataRetriever to fetch relevant context
- Processing chat history and generating responses using the RAG approach

Key method:
- `get_answer(question: str, history: BaseChatMessageHistory)`: Processes a user question and chat history to generate a response.

### 2. DataRetriever (app/services/processor/context_retriever.py)

The DataRetriever is responsible for fetching relevant context for user queries. It utilizes vector search capabilities to find the most relevant information from the knowledge base. Key features include:

- Integration with Neo4jVector for efficient vector storage and retrieval
- Use of embedding models for text vectorization
- Implementation of a custom DocumentRetrieverChain for advanced document processing and retrieval

Key classes:
- `DataRetriever`: Manages the retrieval of relevant context data
- `DocumentRetrieverChain`: Creates a chain of operations for document retrieval, including query transformation, document compression, and contextual retrieval

### 3. LLMModel (app/db/llm.py)

The LLMModel class manages different language models and embeddings used in the chat system. It provides a flexible interface to work with various AI models:

- VertexAIEmbeddings for text embeddings
- ChatAnthropicVertex for the Anthropic language model
- AzureChatOpenAI for the OpenAI language model

Key methods:
- `get_embedding_model()`: Returns the embedding model instance
- `get_chat_anthropic()`: Returns the Anthropic language model instance
- `get_chat_openai()`: Returns the OpenAI language model instance

### 4. Chat Service (app/services/chat.py)

The chat service ties all the components together and provides the main interface for processing chat completions. It handles:

- Creation and management of chat sessions
- Invocation of the QAEngine to process user queries
- Error handling and response formatting

Key function:
- `get_chat_completions(qa_engine: QAEngine, question: str, session_id: str)`: Processes a chat completion request and returns the response.

## Flow of Operation

1. A user sends a chat completion request to the API endpoint.
2. The request is received by the chat endpoint (app/api/endpoints/chat.py).
3. The chat service (app/services/chat.py) is invoked with the user's question and session ID.
4. The chat service creates or retrieves a chat history for the session.
5. The QAEngine is called to process the question:
   a. The DataRetriever fetches relevant context.
   b. The LLMModel processes the question, context, and chat history.
   c. A response is generated using the RAG approach.
6. The response, along with metadata (sources, chunk details), is returned to the user.

## Customization and Extensibility

- Different language models can be integrated by modifying the LLMModel class.
- The vector search and retrieval process can be optimized or replaced by modifying the DataRetriever class.
- Additional preprocessing or postprocessing steps can be added to the QAEngine or chat service.