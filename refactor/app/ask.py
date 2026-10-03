import json
import time
import hashlib
from fastapi import APIRouter, HTTPException
from app.schemas import QuestionRequest
from app.cache import redis_client
from app.models import llm_expansion, llm_answer, reranker
from app import retrieval

router = APIRouter()

@router.post("/ask")
def ask_rag_question(request: QuestionRequest,k:int=3):
    if retrieval.hybrid is None:
        raise HTTPException(
            status_code=400,
            detail="No documents available in the knowledge base. Please upload a document first."
        )

    start = time.time()
    normalized_question = request.question.strip().lower()
    cache_key = f"rag_cache:{hashlib.md5(normalized_question.encode('utf-8')).hexdigest()}"

    # Check Redis Cache
    try:
        cached_response = redis_client.get(cache_key)
        if cached_response:
            response_data = json.loads(cached_response)
            response_data["cached"] = True
            return response_data
    except Exception as e:
        print(f"Cache lookup error: {e}")

    # Query Expansion
    expansion_start = time.time()
    expansion_prompt = f"""أنت محرك بحث ذكي متخصص في الوثائق الإدارية. مهمتك هي إعادة صياغة السؤال التالي إلى استعلامين بديلين دقيقين لتحسين البحث.
قواعد صارمة وممنوع مخالفتها:
أخرج الاستعلامين فقط، ولا شيء غيرهما.
ممنوع منعاً باتاً إضافة أي مقدمات أو خواتم أو شروحات.
ممنوع استخدام الأرقام أو النقاط (مثل: 1- أو *).
افصل بين الاستعلامين بسطر جديد واحد فقط.
استخدم مصطلحات إدارية رسمية ودقيقة.
السؤال: {request.question}
الاستعلامان:"""

    expanded_query = llm_expansion.invoke(expansion_prompt).content.strip()
    expansion_time = time.time() - expansion_start

    # Hybrid Retrieval
    retrieval_start = time.time()
    results = retrieval.hybrid.invoke(expanded_query)
    retrieval_time = time.time() - retrieval_start

    # Reranking with CrossEncoder
    reranker_start = time.time()
    pairs = [(request.question, doc.page_content) for doc in results]
    scores = reranker.predict(pairs)
    ranked_docs = [doc for _, doc in sorted(zip(scores, results), key=lambda x: x[0], reverse=True)]
    final_docs = ranked_docs[:k]
    reranker_time = time.time() - reranker_start

    # LLM Generation
    context = "\n\n".join(doc.page_content for doc in final_docs)
    system_prompt = """You are an expert assistant for Moroccan public administration.
Answer ONLY from the provided context.
Rules:
Never use external knowledge.
If the answer cannot be fully supported by the context, clearly say so.
Reply in the user's language.
"""
    user_prompt = f"""
Context:
{context}

Question:
{request.question}
"""

    llm_start = time.time()
    answer = llm_answer.invoke([("system", system_prompt), ("human", user_prompt)])
    llm_time = time.time() - llm_start
    total_time = time.time() - start

    token_usage = answer.response_metadata.get("token_usage", {})
    final_response = {
        "Question": request.question,
        "Answer": answer.content.strip(),
        "total_time": round(total_time, 3),
        "expansion_time": round(expansion_time, 3),
        "retrieval_time": round(retrieval_time, 3),
        "reranker_time": round(reranker_time, 3),
        "llm_time": round(llm_time, 3),
        "token_usage": {
            "total_tokens": token_usage.get("total_tokens", 0),
            "prompt_tokens": token_usage.get("prompt_tokens", 0),
            "completion_tokens": token_usage.get("completion_tokens", 0)
        },
        "cached": False
    }

    # Store Result in Redis Cache (24h TTL)
    try:
        redis_client.setex(cache_key, 86400, json.dumps(final_response))
    except Exception as e:
        print(f"Failed to save to cache error: {e}")

    return final_response
