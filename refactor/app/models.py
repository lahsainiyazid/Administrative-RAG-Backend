from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from sentence_transformers import CrossEncoder
from app.config import GROQ_API_KEY

llm_expansion = ChatGroq(model="openai/gpt-oss-20b", temperature=0, api_key=GROQ_API_KEY)
llm_answer = ChatGroq(model="openai/gpt-oss-120b", temperature=0, api_key=GROQ_API_KEY)

embeddings = HuggingFaceEmbeddings(
    model_name="intfloat/multilingual-e5-large",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)

reranker = CrossEncoder("BAAI/bge-reranker-base")
