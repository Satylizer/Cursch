import httpx
import logging
from requests.schemes.schemes import LLMResponse

logger = logging.getLogger(__name__)

async def ask_llm(question: str) -> str:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/v1/llm/ask",
                json={"prompt": question},
                timeout=30.0
            )
            response_data = response.json()
            llm_response = LLMResponse(**response_data)
            
            if llm_response.status == "success":
                return llm_response.response
            else:
                raise ValueError(f"LLM error: {llm_response.status}")
                
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e.response.text}")
        return f"Ошибка сервера: {e.response.status_code}"
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return "Ошибка обработки запроса"