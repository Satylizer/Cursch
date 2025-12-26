from fastapi import APIRouter, HTTPException
from models.models import LLMRequest, LLMResponse
from config.config import Agent 

llmrouter = APIRouter(
    prefix="/api/v1/llm",
    tags=["Pure LLM"],
    responses={404: {"description": "Not found"}}
)

@llmrouter.post("/ask", response_model=LLMResponse)
async def ask_llm(request: LLMRequest):
    try:
        agent = Agent()
        
        formatted_prompt = agent.llm_prompt.format(prompt=request.prompt)
        
        response = agent.llm.invoke(formatted_prompt).strip()
        
        return {
            "status": "success",
            "response": response
        }
    except Exception as e:
        raise HTTPException(500, detail=str(e))