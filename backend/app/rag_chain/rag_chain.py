from langchain_text_splitters import RecursiveCharacterTextSplitter
from config.config import Agent, ChromaDB
from typing import List
from langchain_core.documents import Document
import hashlib

def make_doc_id(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

class RagChain:
    def __init__(self, chroma_db: ChromaDB):
        self.agent = Agent()
        self.vector_db = chroma_db
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
    def add_document(self, documents: List[Document]) -> int:
        splits = self.text_splitter.split_documents(documents)

        unique_docs = {}
        for doc in splits:
            doc_id = make_doc_id(doc.page_content)
            if doc_id not in unique_docs:
                unique_docs[doc_id] = doc

        self.vector_db.vectorstore.add_documents(
            documents=list(unique_docs.values()),
            ids=list(unique_docs.keys())
        )

        return len(unique_docs)

    
    def query(self, question: str) -> str:
        retrieved_docs = self.vector_db.vectorstore.similarity_search_with_score(
            question, 
            k=3
        )
        
        relevant_docs = [
            doc for doc, score in retrieved_docs 
            # if score < 1
        ]
        
        if not relevant_docs:
            return "Я не знаю"
            
        context = "\n\n".join([doc.page_content for doc in relevant_docs])
        
        prompt = self.agent.build_rag_prompt(context, question)
        answer = self.agent.llm.invoke(prompt)
        return answer.strip()
