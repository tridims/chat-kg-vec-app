from fastapi import APIRouter, Depends, HTTPException
from app.models.chat import ChatRequest
from app.api.dependencies import get_engine
from app.services.processor.completions import QAEngine
from app.services.chat import get_chat_completions

router = APIRouter()


@router.post("/completions")
async def get_completion(req: ChatRequest, qa_engine: QAEngine = Depends(get_engine)):
    try:
        result = get_chat_completions(qa_engine, req.questions, req.session)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
