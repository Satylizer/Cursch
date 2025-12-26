from langchain_community.llms import LlamaCpp
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

class Agent:
    llm = LlamaCpp(
        model_path="../../mistral/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
        n_ctx=4096,
        n_threads=4,
        temperature=0.1,
        max_tokens=200,
        verbose=True
    )
    
    def build_rag_prompt(self, context: str, question: str) -> str:
        return f"""
        Ты отвечаешь СТРОГО на основе контекста.

        Контекст:
        {context}

        Вопрос: {question}

        Дай короткий, прямой ответ без списков, без повторов, без дополнительных вопросов.
        Ответ:
        """
    
    llm_prompt = ChatPromptTemplate.from_template("""
    Ты — помощник HR. Отвечай кратко и по делу. 

    Если спрашивают про:
    - Отпуск → говори сколько дней положено и какие документы нужны
    - Больничный → объясни как оформить и оплатят ли
    - Увольнение → расскажи про сроки и документы
    - Оформление → перечисли какие бумаги подписать

    Если вопрос не про работу (погода, спорт и т.п.) → 
    "Я могу помочь только с кадровыми вопросами"

    Отвечай на русском языке.

    Вопрос: {prompt}
    Ответ:
    """)

class ChromaDB:
    def __init__(self, persist_directory: str):
        self.persist_directory = persist_directory
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vectorstore = Chroma(
            collection_name="tg_docs",
            embedding_function=self.embeddings,
            persist_directory=persist_directory
        )
        