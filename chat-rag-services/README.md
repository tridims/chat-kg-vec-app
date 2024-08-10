# Chat RAG Services

## Description
FastAPI-based application that provides chat completion functionality using Retrieval-Augmented Generation (RAG). This project integrates various language models and vector search capabilities to provide context-aware chat responses.

## Features
- Chat completion with context retrieval
- Integration with multiple language models (Anthropic, OpenAI)
- Vector search using Neo4j
- Customizable document retrieval and compression
- FastAPI-based RESTful API

## Technologies Used
- Python 3.12+
- FastAPI
- LangChain
- Neo4j
- Google Vertex AI
- Azure OpenAI
- Poetry (for dependency management)
- Docker

## Project Structure
```
chat-rag-services/
│
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── chat.py
│   │   │   ├── document.py
│   │   │   └── graph.py
│   │   └── dependencies.py
│   ├── core/
│   ├── db/
│   │   └── llm.py
│   ├── models/
│   │   └── chat.py
│   ├── services/
│   │   ├── processor/
│   │   │   ├── completions.py
│   │   │   └── context_retriever.py
│   │   └── chat.py
│   └── main.py
├── tests/
├── Dockerfile
├── pyproject.toml
├── poetry.lock
└── README.md
```

## Installation and Setup
1. Clone the repository and navigate to the project directory:
2. Install Poetry (if not already installed):
3. Install dependencies:
   ```
   poetry install
   ```

4. Set up environment variables (create a .env file in the root directory):
   ```
   ANTHROPIC_REGION=your_anthropic_region
   ANTHROPIC_MODEL_NAME=your_anthropic_model_name
   AZURE_OPENAI_API_KEY=your_azure_openai_api_key
   AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
   NEO4J_URI=your_neo4j_uri
   NEO4J_USERNAME=your_neo4j_username
   NEO4J_PASSWORD=your_neo4j_password
   ```

5. Run the application:
   ```
   poetry run uvicorn app.main:app --reload
   ```

## Usage
Once the application is running, you can interact with it using HTTP requests to the provided API endpoints.

## API Endpoints
- `POST /chat/completions`: Send a chat completion request
  - Request body:
    ```json
    {
      "questions": "Your question here",
      "session": "unique_session_id"
    }
    ```
  - Response:
    ```json
    {
      "session_id": "unique_session_id",
      "message": "AI-generated response",
      "info": {
        "sources": ["list", "of", "sources"],
        "chunk_details": [
          {
            "content": "chunk content",
            "score": 0.9876
          }
        ]
      }
    }
    ```

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
MIT