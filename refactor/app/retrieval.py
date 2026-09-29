from langchain_core.documents import Document
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from app.db import collection
from app.models import embeddings

documents = []
try:
    cursor = collection.find({})
    for item in cursor:
        documents.append(Document(page_content=item.get("text", ""), metadata={"source": item.get("source", ""), "id": item.get("id", "")}))
except Exception as e:
    print(f"Error:{e} while loading chunks!")

vector_store = MongoDBAtlasVectorSearch(collection=collection, embedding=embeddings, index_name="vector_index")

if documents:
    bm25 = BM25Retriever.from_documents(documents)
    bm25.k = 5
    dense = vector_store.as_retriever(search_kwargs={"k": 5})
    hybrid = EnsembleRetriever(retrievers=[bm25, dense], weights=[0.6, 0.4])
else:
    bm25 = None
    dense = None
    hybrid = None

def sync_retrievers():
    global bm25, hybrid, dense
    latest_docs = []
    for item in collection.find({}):
        latest_docs.append(Document(page_content=item.get('text', ''), metadata={'source': item.get('source', ''), 'id': item.get('id')}))
    if latest_docs:
        bm25 = BM25Retriever.from_documents(latest_docs)
        bm25.k = 5
        dense = vector_store.as_retriever(search_kwargs={'k': 5})
        hybrid = EnsembleRetriever(retrievers=[bm25, dense], weights=[0.6, 0.4])
    else:
        bm25 = None
        dense = None
        hybrid = None
