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

# Temporary code to initialize database, remove after running once
if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")