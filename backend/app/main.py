from fastapi import FastAPI
import uvicorn
from routes.query import router
from routes.purellm import llmrouter

app = FastAPI(
    title="RAG API Service",
    description="API для работы с RAG-системой",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to RAG API", 
        "endpoints": {
            "docs": "/docs",
            "add_context": "/api/v1/add_context",
            "query": "/api/v1/query"
        }
    }

app.include_router(router)
app.include_router(llmrouter)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)