import io
import hashlib
import pandas as pd
from PyPDF2 import PdfReader
from docx import Document as DocxDocument

def parse_docx(content: bytes):
    try:
        doc = DocxDocument(io.BytesIO(content))
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"

        chunks = []
        chunk_size = 1000
        words = text.split()
        for i in range(0, len(words), chunk_size):
            chunk_text = " ".join(words[i:i+chunk_size])
            if chunk_text.strip():
                chunks.append({
                    "text": chunk_text,
                    "id": hashlib.md5(chunk_text.encode()).hexdigest()
                })
        return chunks
    except Exception as e:
        print(f"Error {e} while loading docx")
        return []

def parse_pdf(content: bytes):
    try:
        pdf_reader = PdfReader(io.BytesIO(content))
        text = ""
        for page in pdf_reader.pages:
            text += (page.extract_text() or "") + '\n'
        chunks = []
        chunk_size = 1000
        words = text.split()
        for i in range(0, len(words), chunk_size):
            chunk_text = " ".join(words[i:i+chunk_size])
            if chunk_text.strip():
                chunks.append({
                    "text": chunk_text,
                    "id": hashlib.md5(chunk_text.encode()).hexdigest()
                })
        return chunks
    except Exception as e:
        print(f"Error:{e} while loading documents")
        return []

def parse_excel(content: bytes):
    try:
        excel_file = pd.ExcelFile(io.BytesIO(content))
        all_text = ""
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            for col in df.columns:
                values = df[col].dropna().astype(str).to_list()
                if values:
                    all_text += f"Column {col}: " + ", ".join(values) + "\n"
        chunks = []
        chunk_size = 1000
        words = all_text.split()
        for i in range(0, len(words), chunk_size):
            chunk_text = " ".join(words[i:i+chunk_size])
            if chunk_text.strip():
                chunks.append({
                    "text": chunk_text,
                    "id": hashlib.md5(chunk_text.encode()).hexdigest()
                })
        return chunks
    except Exception as e:
        print(f"Error {e} while loading the chunks")
        return []
