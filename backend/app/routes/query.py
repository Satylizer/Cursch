from fastapi import APIRouter, HTTPException, Depends
from models.models import *
from dependencies.dependencies import get_chroma_service, ChromaService

router = APIRouter(
    prefix="/api/v1",
    tags=["RAG System"],
    responses={404: {"description": "Not found"}}
)

@router.post(
    "/add_context",
    summary="Добавление контекста",
    response_description="Количество добавленных фрагментов"
)
async def add_context(
    request: TextRequest,
    service: ChromaService = Depends(get_chroma_service)
) -> TextResponse:
    try:
        chunks_added = service.add_text(request.text)
        return TextResponse(
            status="success",
            message=f"Добавлено {chunks_added} чанков",
            data=None
        )
    except Exception as e:
        raise HTTPException(400, detail=str(e))

@router.post(
    "/query",
    summary="Запрос к RAG-системе",
    response_description="Ответ системы"
)
async def query(
    request: QueryRequest,
    service: ChromaService = Depends(get_chroma_service)
) -> TextResponse:
    try:
        answer = service.query(request.question)
        return TextResponse(
            status="success",
            message="Ответ получен",
            data=answer
        )
    except Exception as e:
        raise HTTPException(400, detail=str(e))