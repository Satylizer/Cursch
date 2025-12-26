from typing import List
import httpx
import logging
from requests.schemes.schemes import TextResponse
from database.models.models import Document
from services.service_manager import ServiceManager


logger = logging.getLogger(__name__)

def format_documents_for_rag(documents: List[Document]) -> str:
    return " ".join(doc.content for doc in documents)

async def ask_rag(question: str, service_manager: ServiceManager) -> str: # type: ignore
    try:
        async with httpx.AsyncClient(timeout=100.0) as client:
            response = await client.post(
                "http://localhost:8000/api/v1/query",
                json={
                    "question": question,
                }
            )
            
            if response.status_code == 200:
                response_data = response.json()
                if "data" in response_data:
                    return response_data["data"]
                elif "message" in response_data:
                    return response_data["message"]
            else:
                return f"Ошибка сервера: {response.status_code} - {response.text}"
            
    except httpx.ReadTimeout:
        return "Превышено время ожидания ответа от RAG-системы"
    except Exception as e:
        logger.error(f"RAG error: {str(e)}")
        return "Ошибка при обработке запроса"