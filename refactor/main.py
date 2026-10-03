from fastapi import FastAPI
from app.routes import documents, ask

app = FastAPI()

app.include_router(documents.router)
app.include_router(ask.router)

@app.get("/")
def home():
    return {"Rag is running": "True", "Version": "Final"}
