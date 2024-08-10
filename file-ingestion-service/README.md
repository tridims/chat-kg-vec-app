# File Ingestion Service

## Table of Contents
1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Project Structure](#project-structure)
5. [Main Components](#main-components)
6. [API Endpoints](#api-endpoints)
7. [Configuration](#configuration)
8. [Deployment](#deployment)
9. [Development Guidelines](#development-guidelines)
10. [Testing](#testing)

## Project Overview

Provides a RESTful API for extracting and processing information from PDFs. It uses FastAPI as the web framework and integrates with Neo4j for graph-based data storage and analysis. The service is designed to extract information from documents, generate graph and vector embeddings using a language model, and store the processed data in a Neo4j graph database. The apis receive the file and immediately return a response, then the file is processed asynchronously in the background.

## Features

- PDF file extraction
- Information extraction to graph and vector embedding using a language model
- Storage of graph-based data in Neo4j
- Asynchronous processing of file extraction tasks (means to be job based)

## Installation

### Prerequisites
- Python 3.12 or later
- Poetry (for dependency management)
- Neo4j database (for graph storage)

### Steps

1. Clone the repository and navigate to the project directory.

2. Install dependencies using Poetry:
   ```
   poetry install
   ```

3. Set up environment variables:
   Copy the `.env.example` file to `.env` and fill in the necessary configuration values, including Neo4j connection details and any API keys required for the language model.

## Project Structure

```
file-ingestion-service/
│
├── src/
│   ├── client/
│   │   ├── graph_db.py
│   │   └── llm.py
│   ├── models/
│   ├── processor/
│   │   ├── document.py
│   │   ├── embedding.py
│   │   └── graph.py
│   ├── config.py
│   ├── controller.py
│   └── utils.py
│
├── tests/
├── app.py
├── Dockerfile
├── pyproject.toml
├── README.md
└── run_server.sh
```

## Main Components

### 1. FastAPI Application (app.py)
The main entry point of the application, defining API routes and handling HTTP requests.

### 2. Controller (src/controller.py)
Manages the flow of data processing, coordinating between different components of the system.

### 3. Document Processor (src/processor/document.py)
Handles the processing of documents, including extraction and analysis.

### 4. Embedding Generator (src/processor/embedding.py)
Generates vector embeddings for document chunks using a language model.

### 5. Graph Generator (src/processor/graph.py)
Creates graph representations of the processed document information.

### 6. Neo4j Graph Database Client (src/client/graph_db.py)
Manages interactions with the Neo4j graph database for storing and retrieving processed data.

### 7. Language Model Client (src/client/llm.py)
Interfaces with the chosen language model for text processing and analysis.

## API Endpoints

- `GET /`: Root endpoint, returns a simple "Hello World" message.
- `POST /extract`: Extracts information from a locally uploaded file. Accepts a file upload (multipart form).
- `POST /extraction-remote-file`: Extracts information from a file given its URI.

### Extraction Endpoint Example

To use the remote file extraction endpoint, send a POST request with the file URI:

```json
POST /extract
Content-Type: multipart/form-data
```

The service will download the file, return a response, process it, and store the extracted information in the Neo4j graph database.

## Configuration

Configuration settings are managed in `src/config.py`. Key configuration options include:

- `KNN_MIN_SCORE`: Minimum score for K-Nearest Neighbors search
- `CHUNK_BATCH_SIZE`: Batch size for processing document chunks
- `MAX_PARALLEL_EMBEDDING_SIZE`: Maximum size for parallel embedding generation
- `VECTOR_EMBEDDING_DIMENSION`: Dimension of vector embeddings
- `TEMP_STORAGE`: Directory for temporary file storage

Ensure that you set the appropriate environment variables for database connections and API keys in the `.env` file.

## Deployment

The application can be deployed using Docker. A Dockerfile is provided for containerization.

1. Build the Docker image:
   ```
   docker build -t file-ingestion-service .
   ```

2. Run the container:
   ```
   docker run -p 8001:8001 -e NEO4J_URI=bolt://neo4j:7687 -e NEO4J_USER=neo4j -e NEO4J_PASSWORD=password file-ingestion-service
   ```

Ensure that you set the correct environment variables for your Neo4j instance and any other required configurations.

## Development Guidelines

1. Use Poetry for dependency management.
2. Follow PEP 8 style guide for Python code.
3. Write unit tests for new features and bug fixes.
4. Use type hints to improve code readability and catch potential errors.
5. Document new functions and classes using docstrings.
6. Use async/await for I/O-bound operations to improve performance.

## Testing (Not implemented yet, but when it does it will look like this)

To run the tests:

```
poetry run pytest
```

Ensure that you have a test Neo4j instance set up and configured in your test environment variables.

## License

This project is licensed under the MIT License.

## Contact

For any queries or contributions, please contact:

Dimas Tri Mustakim - me@dimastri.com

Project Link: [https://github.com/tridims/chat-kg-vec-app](https://github.com/tridims/chat-kg-vec-app)