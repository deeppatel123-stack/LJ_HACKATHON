import sqlite3
from passlib.context import CryptContext

# Create a password context for hashing and verification
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SecurityManager:
    """
    Handles user authentication and role-based access control using hashed passwords.
    """

    def hash_password(self, password: str) -> str:
        """Hashes a plaintext password."""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifies a plaintext password against a hashed one."""
        return pwd_context.verify(plain_password, hashed_password)

    def authenticate(self, username, password):
        """Authenticates a user against the database with hashed passwords."""
        conn = sqlite3.connect('data/documents.db')
        c = conn.cursor()
        c.execute("SELECT password, role FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()
        
        if user and self.verify_password(password, user[0]):
            return {'username': username, 'role': user[1]}
        return None

    def has_access(self, user_role, document_category):
        """Checks if a user has access to a document category."""
        if user_role == 'Admin':
            return True
        return user_role == document_category