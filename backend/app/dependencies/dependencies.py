from fastapi import Depends
from config.config import ChromaDB
from rag_chain.rag_chain import RagChain
from database.chroma_service import ChromaService

def get_chroma_db() -> ChromaDB:
    return ChromaDB("./chroma_db")


def get_rag_chain(
    db: ChromaDB = Depends(get_chroma_db)
) -> RagChain:
    return RagChain(db)


def get_chroma_service(
    rag_chain: RagChain = Depends(get_rag_chain)
) -> ChromaService:
    return ChromaService(rag_chain)
