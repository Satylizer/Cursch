from fastapi import Depends
from langchain_core.documents import Document
from rag_chain.rag_chain import RagChain

def json_to_string(self, data):
        if isinstance(data, dict):
            items = []
            for key, value in data.items():
                processed_value = self.json_to_string(value)
                items.append(f"{key}:{processed_value}")
            return "{" + ",".join(items) + "}"

        elif isinstance(data, list):
            items = [self.json_to_string(item) for item in data]
            return "[" + ",".join(items) + "]"

        else:
            return str(data)
      
class ChromaService:
    def __init__(self, rag_chain: RagChain):
         self.rag_chain = rag_chain
    
    def add_text(self, text: str) -> int:
        text = json_to_string(self, text)
        doc = Document(page_content=text)
        return self.rag_chain.add_document([doc])
    
    def query(self, question: str) -> str:
        question = json_to_string(self, question)
        return self.rag_chain.query(question)
    
