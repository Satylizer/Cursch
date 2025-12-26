from pydantic import BaseModel
from typing import Optional

class TextRequest(BaseModel):
    text: str
    
class QueryRequest(BaseModel):
    question: str

class TextResponse(BaseModel):
    status: str
    message: str
    data: Optional[str] = None
    
class LLMRequest(BaseModel):
    prompt: str

class LLMResponse(BaseModel):
    status: str
    response: str