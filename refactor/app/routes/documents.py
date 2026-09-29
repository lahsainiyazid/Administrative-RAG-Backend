from fastapi import APIRouter, UploadFile, File, HTTPException
from langchain_core.documents import Document
from app.db import collection
from app.cache import clear_cache
from app.parsers import parse_pdf, parse_docx, parse_excel
from app import retrieval

router = APIRouter()

@router.get("/documents")
def get_documents():
    documents = list(collection.find({}, {"_id": 1, "source": 1, "id": 1, "text": 1}))
    for doc in documents:
        doc["_id"] = str(doc["_id"])
    return documents

@router.get("/document/{filename}")
def get_document(filename: str):
    docs = list(collection.find({"source": filename}))
    if not docs:
        raise HTTPException(404, detail="File not found")
    for doc in docs:
        doc["_id"] = str(doc["_id"])
    return {
        "filename": filename,
        "total_chunks": len(docs),
        "chunks": docs
    }

@router.delete("/documents/{filename}")
def delete_document(filename: str):
    result = collection.delete_many({"source": filename})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Document not found")

    retrieval.sync_retrievers()
    clear_cache()

    return {
        "message": "Document deleted successfully",
        "filename": filename,
        "deleted_chunks": result.deleted_count
    }

@router.put("/document/{filename}")
async def update_document(filename: str, file: UploadFile = File(...)):
    if not (file.filename.endswith(".docx") or file.filename.endswith(".pdf") or file.filename.endswith(".xlsx") or file.filename.endswith(".xls")):
        raise HTTPException(status_code=400, detail="Only .docx, .pdf, .xls, .xlsx files are accepted")

    delete_result = collection.delete_many({"source": filename})

    content = await file.read()
    if file.filename.endswith(".pdf"):
        chunks = parse_pdf(content)
    elif file.filename.endswith(".docx"):
        chunks = parse_docx(content)
    else:
        chunks = parse_excel(content)

    if not chunks:
        raise HTTPException(status_code=400, detail="Error while extracting chunks from document!")

    docs_to_add = [
        Document(
            page_content=chunk["text"],
            metadata={"source": file.filename, "id": chunk["id"]}
        )
        for chunk in chunks
    ]

    inserted_ids = retrieval.vector_store.add_documents(docs_to_add)

    retrieval.sync_retrievers()
    clear_cache()

    return {
        "message": "Document updated successfully",
        "filename": file.filename,
        "new_chunks_count": len(inserted_ids),
        "deleted_chunks": delete_result.deleted_count
    }

@router.post('/upload_file')
async def upload_documents(file: UploadFile = File(...)):
    if not (file.filename.endswith('.docx') or file.filename.endswith('.pdf') or file.filename.endswith('.xls') or file.filename.endswith('.xlsx')):
        raise HTTPException(status_code=400, detail='Only .docx, .pdf, .xls, .xlsx files are supported')

    content = await file.read()
    if file.filename.endswith('.docx'):
        chunks = parse_docx(content)
    elif file.filename.endswith('.pdf'):
        chunks = parse_pdf(content)
    else:
        chunks = parse_excel(content)

    if not chunks:
        raise HTTPException(status_code=400, detail='Error while generating chunks')

    docs_to_add = [
        Document(
            page_content=chunk["text"],
            metadata={"source": file.filename, "id": chunk["id"]}
        )
        for chunk in chunks
    ]

    inserted_ids = retrieval.vector_store.add_documents(docs_to_add)
    retrieval.sync_retrievers()
    clear_cache()

    return {
        "Message": "Documents loaded successfully",
        "filename": file.filename,
        "Number of chunks": len(inserted_ids)
    }
