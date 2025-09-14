from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.event import on_event
import os
import shutil
import datetime
import json
from typing import Optional

# Import ML and Security modules from their new folder
from ml_models.database import init_db, insert_document, get_documents_by_role, log_access, register_user
from ml_models.document_processor import extract_text, extract_metadata, summarize_text
from ml_models.classification_model import DocumentClassifier
from ml_models.search_engine import SemanticSearchEngine
from ml_models.security_manager import SecurityManager

# --- Initialize Core Components ---
app = FastAPI()
classifier = DocumentClassifier()
search_engine = SemanticSearchEngine()
security = SecurityManager()

# Add CORS middleware to allow the frontend to access the API
origins = ["http://localhost:5173"]  # URL of your Vite development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Startup Event to Rebuild the In-Memory Index ---
@app.on_event("startup")
async def startup_event():
    # Ensure data directory and database exist
    if not os.path.exists('data'):
        os.makedirs('data')
        init_db()
    
    # Rebuild the FAISS index from the database
    print("Rebuilding in-memory search index...")
    all_docs = get_documents_by_role("Admin") # Get all documents regardless of role
    for doc in all_docs:
        try:
            doc_text = extract_text(doc[2])
            search_engine.add_document(doc[0], doc_text)
        except Exception as e:
            print(f"Error rebuilding index for document ID {doc[0]}: {e}")
            continue
    print("Search index rebuilt successfully.")

# --- Security Dependencies ---
def get_user_from_form(username: str = Form(...), password: str = Form(...)):
    user = security.authenticate(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user

def get_user_from_query(username: str = Query(...), password: str = Query(...)):
    user = security.authenticate(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user

# --- API Endpoints ---
@app.post("/upload/")
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_user_from_form)
):
    """
    Uploads a document, processes it, and stores metadata in the DB.
    """
    file_path = f"data/{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    text = extract_text(file_path)
    metadata = extract_metadata(text)
    category = classifier.classify_document(text)
    summary = summarize_text(text)
    
    doc_data = {
        'filename': file.filename,
        'filepath': file_path,
        'upload_date': str(datetime.datetime.now()),
        'uploader': current_user['username'],
        'category': category,
        'title': metadata['title'],
        'author': metadata['author'],
        'date_extracted': metadata['date_extracted'],
        'summary': summary,
        'entities': metadata['entities']
    }
    
    doc_id = insert_document(doc_data)
    search_engine.add_document(doc_id, text)
    log_access(current_user['username'], 'upload', doc_id)
    
    return JSONResponse(content={
        "message": "Document uploaded and processed successfully",
        "doc_id": doc_id,
        "classification": category,
        "metadata": metadata
    })

@app.get("/documents/")
async def get_documents(current_user: dict = Depends(get_user_from_query)):
    """
    Retrieves a list of documents based on the user's role.
    """
    documents = get_documents_by_role(current_user['role'])
    
    result = []
    for doc in documents:
        result.append({
            'id': doc[0],
            'filename': doc[1],
            'uploader': doc[4],
            'category': doc[5],
            'title': doc[6],
            'summary': doc[9],
            'entities': json.loads(doc[10])
        })
    
    log_access(current_user['username'], 'view_list')
    return JSONResponse(content=result)

@app.get("/search/")
async def semantic_search(
    query: str,
    current_user: dict = Depends(get_user_from_query)
):
    """
    Performs a semantic search and returns relevant documents.
    """
    # The search engine already has the full index from the startup event
    results = search_engine.search(query, top_k=5)
    
    log_access(current_user['username'], 'search', None)
    return JSONResponse(content=results)

@app.post("/register/")
async def register_new_user(username: str = Form(...), password: str = Form(...), role: str = Form(...)):
    """Registers a new user."""
    user = register_user(username, password, role)
    if user:
        return JSONResponse(content={"message": "User registered successfully"})
    else:
        raise HTTPException(status_code=400, detail="Username already exists")