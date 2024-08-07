# File Ingestion Service

## Description

File Ingestion Service is a Python-based application that provides a RESTful API for extracting and processing information from files. It uses FastAPI for the web framework and integrates with Neo4j for graph-based data storage and analysis.

## Features

- PDF file extraction from remote URIs
- Extract information to graph and vector embedding using llm
- Store graph-based data in Neo4j

## Installation

To set up the project, you need to have Python 3.12 or later and Poetry installed.

1. Get into the project directory

2. Install dependencies using Poetry:
   ```
   poetry install
   ```

3. Set up environment variables:
   Copy the `.env.example` file to `.env` and fill in the necessary configuration values.

## Usage

To start the server, run:

```
./run_server.sh
```

Or use the following command:

```
poetry run uvicorn server:app --reload
```

The server will start on `http://localhost:8000` by default.

## API Endpoints

- `GET /`: Root endpoint, returns a simple "Hello World" message.
- `POST /extraction`: Extracts information from a file given its URI.

### Extraction Endpoint

To use the extraction endpoint, send a POST request with the file URI:

```
POST /extraction
{
    "file_uri": "https://example.com/path/to/file.pdf"
}
```

The service will download the file, process it, and store the extracted information in the Neo4j graph database.

## Dependencies

Major dependencies include:

- FastAPI
- Uvicorn
- LangChain
- Neo4j
- Python-dotenv
- Requests
- PyMuPDF

For a full list of dependencies, refer to the `pyproject.toml` file.

## Development

To contribute to the project:

1. Fork the repository
2. Create a new branch for your feature
3. Implement your changes
4. Write tests for your new features
5. Submit a pull request

## License

MIT License

## Contact

Dimas Tri Mustakim - me@dimastri.com

Project Link: [https://github.com/tridims](https://github.com/tridims)