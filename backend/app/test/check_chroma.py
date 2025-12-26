import shutil
import pytest
from pathlib import Path
from langchain_core.documents import Document
from rag_chain.rag_chain import RagChain
from config.config import ChromaDB


TEST_DB_PATH = Path("./test_chroma_db")


@pytest.fixture(scope="function")
def rag():
    db = ChromaDB(persist_directory=str(TEST_DB_PATH))
    chain = RagChain(db)
    yield chain
    if TEST_DB_PATH.exists():
        shutil.rmtree(TEST_DB_PATH, ignore_errors=True)
        
def test_duplicate_not_duplicated(rag):
    text = "Срок уведомления при увольнении — 2 недели"
    doc = Document(page_content=text)

    rag.add_document([doc])
    rag.add_document([doc])

    all_docs = rag.vector_db.vectorstore.get()

    print("Документы в базе после добавления:")
    for doc in all_docs["documents"]:
        print(doc)

    assert len(all_docs["documents"]) == 1 


def test_add_document_to_chroma(rag):
    doc = Document(page_content="Компания предоставляет 28 дней отпуска")

    count = rag.add_document([doc])

    assert count == 1


def test_document_is_retrievable(rag):
    text = "Больничный оплачивается работодателем"
    rag.add_document([Document(page_content=text)])

    results = rag.vector_db.vectorstore.similarity_search("больничный", k=1)

    assert results
    assert "Больничный" in results[0].page_content

def test_multiple_documents(rag):
    docs = [
        Document(page_content="Отпуск составляет 28 дней"),
        Document(page_content="Больничный оплачивается полностью"),
        Document(page_content="Испытательный срок 3 месяца"),
    ]

    count = rag.add_document(docs)

    assert count == 3

    results = rag.vector_db.vectorstore.similarity_search("больничный", k=1)

    assert "Больничный" in results[0].page_content
