from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.services import documents
from app.api.dependencies import get_graph_db_dao
import requests

router = APIRouter()


@router.get("")
async def get_documents():
    return documents.get_documents(get_graph_db_dao())


@router.delete("/{file_name}")
async def delete_document(file_name: str):
    return documents.delete_document(get_graph_db_dao(), file_name)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()

        files = {
            "file": (file.filename, contents, file.content_type),
        }

        response = requests.post(settings.FILE_INGESTION_SERVICE_URL, files=files)

        # Check if the forward was successful                                                                                                                                                                                                                                                             │
        if response.status_code == 200:
            return JSONResponse(
                content={
                    "filename": file.filename,
                    "status": "success",
                    "message": "File uploaded successfully",
                    "forward_service_response": response.json(),
                },
                status_code=200,
            )
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to forward file to ingestion service",
            )
    finally:
        file.file.close()
