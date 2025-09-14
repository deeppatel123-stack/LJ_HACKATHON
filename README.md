# AI-Powered Document Classification and Indexing System

This project is a full-stack application for automatically classifying, indexing, and searching documents. It combines a FastAPI backend with an ML model and a React.js frontend to provide a seamless user experience.

The system is designed to handle common document types (PDF, DOCX, TXT) and perform the following key functions:

1.  **Document Classification**: Automatically categorizes documents into predefined classes like **HR, Finance, Legal, and Technical Reports**.
2.  **Metadata Extraction & Summarization**: Captures essential details like the title, author, and key entities, and generates a brief summary of the document's content.
3.  **Semantic Search**: Allows users to search for documents based on meaning rather than just keywords, providing more accurate and relevant results.
4.  **Role-Based Access Control**: Secures documents by restricting access based on user roles (e.g., HR users can only view HR documents).

-----

## Project Structure

The project is organized into three main components:

  - `app/`: Contains the FastAPI backend, which serves as the API layer.
  - `ml_models/`: Houses all the core Python scripts for document processing, classification, and search.
  - `client/`: The React.js frontend, which provides the user interface.

<!-- end list -->

```
LJ_HACKATHON_FINAL/
├── app/
│   ├── main.py
│   └── __init__.py
│
├── ml_models/
│   ├── classification_model.py
│   ├── document_processor.py
│   ├── database.py
│   ├── search_engine.py
│   └── security_manager.py
│
├── client/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── DocumentList.jsx
│   │   │   ├── DocumentUpload.jsx
│   │   │   ├── SearchBar.jsx
│   │   │   └── UserRegistration.jsx
│   │   ├── App.jsx
│   │   └── index.css
│   └── package.json
│
├── data/
│   └── documents.db
│
├── requirements.txt
└── .gitignore
```

-----

## Getting Started

Follow these steps to set up and run the project locally.

### Prerequisites

  - Python 3.9+
  - Node.js & npm
  - Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/LJ_HACKATHON_FINAL.git
cd LJ_HACKATHON_FINAL
```

### Step 2: Set Up the Backend

1.  **Create a Python virtual environment**:
    ```bash
    python -m venv venv
    # Activate the environment
    # On Windows: .\venv\Scripts\activate
    # On macOS/Linux: source venv/bin/activate
    ```
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    python -m spacy download en_core_web_sm
    ```
3.  **Initialize the database**:
    Create a folder named `data` and then run the database script to create the `documents.db` file with hardcoded users.
    ```bash
    mkdir data
    python ml_models/database.py
    ```
4.  **Start the FastAPI server**:
    ```bash
    uvicorn app.main:app --reload --port 8002
    ```

### Step 3: Set Up the Frontend

1.  **Navigate to the client directory**:
    ```bash
    cd client
    ```
2.  **Install dependencies**:
    ```bash
    npm install
    ```
3.  **Start the development server**:
    ```bash
    npm run dev
    ```

### Step 4: Use the Application

  - Open your browser and go to `http://localhost:5173`.
  - Use the **login or register** form to get started. Hardcoded users are available for testing:
      - `admin`/`admin_pass`
      - `hr_user`/`hr_pass`
      - `finance_user`/`finance_pass`
  - Upload a document and watch it get classified.
  - Use the search bar to test semantic search, and the refresh button to update the document list.

-----

## API Endpoints

The FastAPI backend provides the following RESTful API endpoints:

  - **`POST /register/`**: Register a new user with a username, password, and role.
  - **`POST /upload/`**: Upload a document for processing, classification, and indexing.
  - **`GET /documents/`**: Retrieve a list of documents based on the authenticated user's role.
  - **`GET /search/`**: Perform a semantic search on the documents and return relevant results.

-----
