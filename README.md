# Chat KG Vec App: Intelligent Document Processing and Conversational AI System

## Project Overview

Application designed to process documents, extract information and provide an interactive chat interface with knowledge graph visualisation capabilities. The application uses the LLM model to extract text into a knowledge graph and create a vector index that can be later retrieved to provide contextual answers and insightful data visualisations.

## Main Components

The project consists of four main services, each serving a specific purpose in the overall architecture:

1. **chat-rag-services**: A FastAPI-based application that provides chat completion functionality using Retrieval-Augmented Generation (RAG).

2. **file-ingestion-service**: A RESTful API service for extracting and processing information from PDF documents.

3. **chat-ui**: A Next.js-based frontend application that combines a chat interface with graph visualization and file upload capabilities.

4. **neo4j**: A graph database used for storing and querying the processed document information.

## Component Interactions

The components interact as follows:

1. The **file-ingestion-service** processes uploaded PDF documents, extracting information and generating graph and vector embeddings.

2. Extracted information is stored in the **neo4j** graph database.

3. The **chat-rag-services** utilizes the stored information in neo4j to provide context-aware responses to user queries.

4. The **chat-ui** serves as the user interface, allowing users to interact with the chat system, visualize graph data, and manage document uploads.

5. User queries from the chat-ui are sent to chat-rag-services, which processes them and returns responses.

6. Graph data for visualization is fetched from neo4j through the chat-rag-services API.

## Technology Stack

- Backend:
  - Python 3.12+
  - FastAPI
  - LangChain
  - Neo4j (Graph Database)
  - Google Vertex AI (serve anthropic model and embeddings)
  - Azure OpenAI (serve openai model)

- Frontend:
  - Next.js
  - React
  - TypeScript
  - Tailwind CSS
  - Shadcn UI components
  - React-Sigma (for graph visualization)

- DevOps:
  - Docker
  - Docker Compose

- Dependency Management:
  - Poetry (Python)
  - npm (Node.js)

## Setup and Installation

1. Clone the repository:
   ```
   git clone &lt;repository-url&gt;
   cd chat-kg-vec-app
   ```

2. Set up environment variables:
   - Copy the `.env.example` file to `.env` in the root directory.
   - Fill in the necessary configuration values, including Neo4j connection details and API keys for language models.

3. Set up a service account key for Google Cloud that have Vertex AI User role and download the key as `gcp-service-account.json` in the root directory.

3. Build and start the services using Docker Compose:
   ```
   docker-compose up --build
   ```

This will start all the services defined in the `docker-compose.yml` file.

## Usage

Once the services are up and running:

1. Access the chat interface by opening a web browser and navigating to `http://localhost:80`.

2. Use the chat interface to:
   - Upload PDF documents for processing
   - Engage in conversations with the AI system
   - Visualize graph data related to the processed documents

3. The system will process uploaded documents in the background, extract information, and make it available for future queries.

## API Endpoints

The following main API endpoints are available in port 8000:

- Chat Completions: `POST /chat/completions`
- Document Management:
  - List Documents: `GET /document`
  - Upload Document: `POST /document`
  - Delete Document: `DELETE /document/:filename`
- Graph Data: `GET /graph`

For detailed API documentation, refer to the individual service README files or API documentation pages (if available).

## Contributing

Contributions to the project are welcome. Please follow these steps:

1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Make your changes
4. Write or update tests as necessary
5. Submit a pull request with a clear description of your changes

## License

This project is licensed under the MIT License.

## Support

For questions, issues, or feature requests, please open an issue in the project's GitHub repository.