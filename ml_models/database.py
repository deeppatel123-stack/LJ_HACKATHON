import sqlite3
import json
from .security_manager import SecurityManager

DATABASE_FILE = 'data/documents.db'

def init_db():
    """Initializes the SQLite database with the required tables."""
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    
    # Create tables
    c.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            upload_date TEXT NOT NULL,
            uploader TEXT NOT NULL,
            category TEXT,
            title TEXT,
            author TEXT,
            date_extracted TEXT,
            summary TEXT,
            entities TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS access_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            action TEXT NOT NULL,
            username TEXT NOT NULL,
            document_id INTEGER,
            FOREIGN KEY (document_id) REFERENCES documents(id)
        )
    ''')

    # Hash passwords before inserting
    security = SecurityManager()
    hashed_hr_pass = security.hash_password('hr_pass')
    hashed_finance_pass = security.hash_password('finance_pass')
    hashed_admin_pass = security.hash_password('admin_pass')
    hashed_legal_pass = security.hash_password('legal_pass')
    hashed_marketing_pass = security.hash_password('marketing_pass')
    
    # Insert hardcoded users
    c.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)", 
              ('hr_user', hashed_hr_pass, 'HR'))
    c.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)", 
              ('finance_user', hashed_finance_pass, 'Finance'))
    c.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)", 
              ('admin', hashed_admin_pass, 'Admin'))
    c.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)", 
              ('legal_user', hashed_legal_pass, 'Legal'))
    c.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)", 
              ('marketing_user', hashed_marketing_pass, 'Marketing'))
    
    conn.commit()
    conn.close()

def insert_document(doc_data):
    """Inserts document metadata into the database."""
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO documents (filename, filepath, upload_date, uploader, category, title, author, date_extracted, summary, entities)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        doc_data['filename'], doc_data['filepath'], doc_data['upload_date'],
        doc_data['uploader'], doc_data['category'], doc_data['title'],
        doc_data['author'], doc_data['date_extracted'], doc_data['summary'],
        json.dumps(doc_data['entities'])
    ))
    doc_id = c.lastrowid
    conn.commit()
    conn.close()
    return doc_id

def get_documents_by_role(role: str):
    """Retrieves documents based on the user's role."""
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    if role == 'Admin':
        c.execute("SELECT * FROM documents")
    else:
        # Assuming category names match roles for simplicity
        c.execute("SELECT * FROM documents WHERE category = ?", (role,))
    documents = c.fetchall()
    conn.close()
    return documents

def get_document_by_id(doc_id: int):
    """Retrieves a single document by its ID."""
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
    document = c.fetchone()
    conn.close()
    return document

def delete_document(doc_id: int):
    """Deletes a document by its ID."""
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
    deleted_rows = c.rowcount
    conn.commit()
    conn.close()
    return deleted_rows > 0

def cleanup_invalid_documents():
    """Removes documents with invalid or null upload dates from the database."""
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    
    # First, let's see what we have
    c.execute("SELECT id, filename, upload_date FROM documents")
    all_docs = c.fetchall()
    print(f"Found {len(all_docs)} total documents")
    
    # Delete documents with null, empty, or invalid upload_date
    c.execute("""
        DELETE FROM documents 
        WHERE upload_date IS NULL 
        OR upload_date = '' 
        OR upload_date = 'None'
        OR upload_date LIKE '%-%-%T%:%:%'
        OR LENGTH(upload_date) < 10
        OR upload_date NOT LIKE '%202%'
    """)
    
    deleted_count = c.rowcount
    conn.commit()
    
    # Check remaining documents
    c.execute("SELECT id, filename, upload_date FROM documents")
    remaining_docs = c.fetchall()
    print(f"Remaining {len(remaining_docs)} documents after cleanup")
    
    conn.close()
    
    print(f"Cleaned up {deleted_count} documents with invalid dates")
    return deleted_count

def force_cleanup_all_documents():
    """Force delete ALL existing documents to start fresh."""
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM documents")
    total_count = c.fetchone()[0]
    
    c.execute("DELETE FROM documents")
    deleted_count = c.rowcount
    conn.commit()
    conn.close()
    
    print(f"Force deleted all {deleted_count} documents from database")
    return deleted_count

def log_access(username: str, action: str, doc_id: int = None):
    """Logs user actions (uploads, views) to the access logs table."""
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO access_logs (timestamp, action, username, document_id)
        VALUES (CURRENT_TIMESTAMP, ?, ?, ?)
    ''', (action, username, doc_id))
    conn.commit()
    conn.close()

def register_user(username: str, password: str, role: str):
    """Registers a new user in the database."""
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    
    c.execute("SELECT username FROM users WHERE username = ?", (username,))
    if c.fetchone():
        conn.close()
        return None
    
    security = SecurityManager()
    hashed_password = security.hash_password(password)
    
    c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
              (username, hashed_password, role))
    conn.commit()
    conn.close()
    
    return {"message": "User registered successfully"}

def run_cleanup():
    cleanup_invalid_documents()

# Temporary code to initialize database, remove after running once
if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
    run_cleanup()