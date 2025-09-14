from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import datetime
import json
from typing import Optional

# Import ML and Security modules from their new folder
from ml_models.database import init_db, insert_document, get_documents_by_role, log_access, register_user, get_document_by_id, delete_document, cleanup_invalid_documents, force_cleanup_all_documents
from ml_models.document_processor import extract_text, extract_metadata, summarize_text
from ml_models.classification_model import DocumentClassifier
from ml_models.search_engine import SemanticSearchEngine
from ml_models.security_manager import SecurityManager

# --- Initialize Core Components ---
classifier = DocumentClassifier()
search_engine = SemanticSearchEngine()
security = SecurityManager()

# Define the lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # This code runs on application startup
    print("Application startup event triggered.")
    
    # Ensure data directory and database exist
    if not os.path.exists('data'):
        os.makedirs('data')
        init_db()
    
    # Clean up documents with invalid dates
    print("Cleaning up documents with invalid dates...")
    cleanup_invalid_documents()
    
    # Rebuild the FAISS index from the database
    print("Rebuilding in-memory search index...")
    all_docs = get_documents_by_role("Admin")
    for doc in all_docs:
        try:
            doc_text = extract_text(doc[2])
            search_engine.add_document(doc[0], doc_text)
        except Exception as e:
            print(f"Error rebuilding index for document ID {doc[0]}: {e}")
            continue
    print("Search index rebuilt successfully.")
    
    yield # The application will run here
    
    # This code runs on application shutdown
    print("Application shutdown event triggered.")

app = FastAPI(lifespan=lifespan)

# Add CORS middleware
origins = ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/")
def read_root():
    return {"message": "Document Classification API is running!"}

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
        'upload_date': datetime.datetime.now().isoformat(),
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
    
    # Category-specific fallback messages and team authors
    category_fallbacks = {
        'HR': 'HR-related document',
        'Finance': 'Finance-related document', 
        'Legal': 'Legal-related document',
        'Admin': 'Administrative document'
    }
    
    team_authors = {
        'HR': 'hr_team',
        'Finance': 'finance_team',
        'Legal': 'legal_team',
        'Admin': 'admin_team'
    }
    
    result = []
    for doc in documents:
        # Helper function to handle null/empty values
        def safe_value(value, fallback="No information available"):
            if value is None or value == "" or value == "Unknown" or value == "Untitled":
                return fallback
            return value
        
        # Get category-specific fallback based on user role
        category_fallback = category_fallbacks.get(current_user['role'], 'General document')
        
        # Get team author based on category
        actual_category = doc[5] if doc[5] and doc[5] != "" else current_user['role']
        team_author = team_authors.get(actual_category, f"{current_user['role'].lower()}_team")
        
        # Parse entities safely
        entities = {}
        try:
            if doc[10] and doc[10] != "null":
                entities = json.loads(doc[10])
        except (json.JSONDecodeError, TypeError):
            entities = {}
        
        result.append({
            'id': doc[0],
            'filename': safe_value(doc[1], "Unknown file"),
            'filepath': doc[2],
            'upload_date': doc[3],
            'uploader': safe_value(doc[4], "Unknown user"),
            'category': safe_value(doc[5], category_fallback),
            'title': safe_value(doc[6], "No title available"),
            'summary': safe_value(doc[9], "No summary available"),
            'author': team_author,
            'entities': entities if entities else {}
        })
    
    log_access(current_user['username'], 'view_list')
    return JSONResponse(content=result)

@app.get("/search/")
async def semantic_search(
    query: str,
    current_user: dict = Depends(get_user_from_query)
):
    """
    Performs a semantic search and returns relevant documents with full details.
    """
    # Get search results (document IDs and scores)
    search_results = search_engine.search(query, top_k=5)
    
    # If no results found, return empty list
    if not search_results:
        log_access(current_user['username'], 'search', None)
        return JSONResponse(content=[])
    
    # Category-specific fallback messages and team authors
    category_fallbacks = {
        'HR': 'HR-related document',
        'Finance': 'Finance-related document', 
        'Legal': 'Legal-related document',
        'Admin': 'Administrative document'
    }
    
    team_authors = {
        'HR': 'hr_team',
        'Finance': 'finance_team',
        'Legal': 'legal_team',
        'Admin': 'admin_team'
    }
    
    # Fetch full document details from database
    detailed_results = []
    
    for result in search_results:
        doc_id = result['document_id']
        doc = get_document_by_id(doc_id)
        
        if doc and security.has_access(current_user['role'], doc[5]):  # doc[5] is category
            # Helper function to handle null/empty values
            def safe_value(value, fallback="No information available"):
                if value is None or value == "" or value == "Unknown" or value == "Untitled":
                    return fallback
                return value
            
            # Get category-specific fallback based on user role
            category_fallback = category_fallbacks.get(current_user['role'], 'General document')
            
            # Get team author based on category
            actual_category = doc[5] if doc[5] and doc[5] != "" else current_user['role']
            team_author = team_authors.get(actual_category, f"{current_user['role'].lower()}_team")
            
            # Parse entities safely
            entities = {}
            try:
                if doc[10] and doc[10] != "null":
                    entities = json.loads(doc[10])
            except (json.JSONDecodeError, TypeError):
                entities = {}
            
            detailed_results.append({
                'id': doc[0],           # id
                'filename': safe_value(doc[1], "Unknown file"),     # filename
                'filepath': doc[2],     # filepath
                'upload_date': doc[3],  # upload_date
                'uploader': safe_value(doc[4], "Unknown user"),     # uploader
                'category': safe_value(doc[5], category_fallback),  # category
                'title': safe_value(doc[6], "No title available"), # title
                'author': team_author,  # Use team author instead of doc[7]
                'summary': safe_value(doc[9], "No summary available"), # summary
                'entities': entities if entities else {},
                'search_score': result['score']  # Include relevance score
            })
    
    log_access(current_user['username'], 'search', None)
    return JSONResponse(content=detailed_results)

@app.post("/cleanup-invalid-documents/")
async def cleanup_invalid_documents_endpoint(current_user: dict = Depends(get_user_from_query)):
    """
    Manually clean up documents with invalid dates. Only admin can perform this action.
    """
    if current_user['role'] != 'Admin':
        raise HTTPException(status_code=403, detail="Only admin can perform cleanup operations")
    
    try:
        deleted_count = cleanup_invalid_documents()
        
        # Rebuild search index after cleanup
        print("Rebuilding search index after cleanup...")
        search_engine.documents = []
        search_engine.document_ids = []
        search_engine.index = None
        search_engine.embeddings = None
        
        all_docs = get_documents_by_role("Admin")
        for doc in all_docs:
            try:
                doc_text = extract_text(doc[2])
                search_engine.add_document(doc[0], doc_text)
            except Exception as e:
                print(f"Error rebuilding index for document ID {doc[0]}: {e}")
                continue
        
        log_access(current_user['username'], 'cleanup', None)
        return JSONResponse(content={"message": f"Cleaned up {deleted_count} documents with invalid dates"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")

@app.post("/force-cleanup-all-documents/")
async def force_cleanup_all_documents_endpoint(current_user: dict = Depends(get_user_from_query)):
    """
    Completely clear all documents with invalid dates. Only admin can perform this action.
    """
    if current_user['role'] != 'Admin':
        raise HTTPException(status_code=403, detail="Only admin can perform force cleanup operations")
    
    try:
        deleted_count = force_cleanup_all_documents()
        
        # Rebuild search index after cleanup
        print("Rebuilding search index after cleanup...")
        search_engine.documents = []
        search_engine.document_ids = []
        search_engine.index = None
        search_engine.embeddings = None
        
        all_docs = get_documents_by_role("Admin")
        for doc in all_docs:
            try:
                doc_text = extract_text(doc[2])
                search_engine.add_document(doc[0], doc_text)
            except Exception as e:
                print(f"Error rebuilding index for document ID {doc[0]}: {e}")
                continue
        
        log_access(current_user['username'], 'force_cleanup', None)
        return JSONResponse(content={"message": f"Force cleaned up {deleted_count} documents with invalid dates"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Force cleanup failed: {str(e)}")

@app.delete("/documents/{doc_id}")
async def delete_document_endpoint(
    doc_id: int,
    current_user: dict = Depends(get_user_from_query)
):
    """
    Deletes a document by ID. Only admin or document owner can delete.
    """
    # Get document details first
    doc = get_document_by_id(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check if user has permission to delete (admin or owner)
    if current_user['role'] != 'Admin' and doc[4] != current_user['username']:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    # Delete the physical file if it exists
    file_path = doc[2]  # doc[2] is filepath
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Warning: Could not delete file {file_path}: {e}")
    
    # Remove from search index to prevent ML model issues
    try:
        # Remove from search engine index if it exists
        if hasattr(search_engine, 'documents'):
            search_engine.documents = [(d_id, text) for d_id, text in search_engine.documents if d_id != doc_id]
            search_engine.document_ids = [d_id for d_id in search_engine.document_ids if d_id != doc_id]
            # Rebuild index without the deleted document
            if search_engine.documents:
                search_engine.rebuild_index()
            else:
                search_engine.index = None
                search_engine.embeddings = None
    except Exception as e:
        print(f"Warning: Could not update search index: {e}")
    
    # Delete from database
    success = delete_document(doc_id)
    if success:
        log_access(current_user['username'], 'delete', doc_id)
        return JSONResponse(content={"message": "Document deleted successfully"})
    else:
        raise HTTPException(status_code=500, detail="Failed to delete document")

@app.post("/register/")
async def register_new_user(username: str = Form(...), password: str = Form(...), role: str = Form(...)):
    """Registers a new user."""
    user = register_user(username, password, role)
    if user:
        return JSONResponse(content={"message": "User registered successfully"})
    else:
        raise HTTPException(status_code=400, detail="Username already exists")