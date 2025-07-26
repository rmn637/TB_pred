from .database.connection import DatabaseConnection
from mysql.connector import Error
import hashlib

class AccountModel:
    def __init__(self, db_config):
        self.db_connection = DatabaseConnection(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database']
        )
    
    def authenticate_user(self, username, password):
        connection = self.db_connection.get_connection()
        if not connection:
            return False, "Database connection failed"
        
        try:
            cursor = connection.cursor()
            encrypted_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

            if not username or not password:
                return False, "Username and password are required"
            
            query = "SELECT * FROM account WHERE username = %s AND pword = %s"
            cursor.execute(query, (username, encrypted_password))
            result = cursor.fetchone()
            cursor.close()
            connection.close()

            if result:
                return True, result
            else:
                return False, "Invalid credentials"
            
        except Error as e:
            return False, f"Database error: {str(e)}"

    def create_user(self, username, firstName, lastName, password):
        """Create a new user with encrypted password."""
        connection = self.db_connection.get_connection()
        if not connection:
            return False, "Database connection failed"
        try:
            encrypted_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
            cursor = connection.cursor()

            # Check if username already exists
            check_query = "SELECT id FROM account WHERE username = %s"
            cursor.execute(check_query, (username,))
            if cursor.fetchone():
                cursor.close()
                connection.close()
                return False, "Username already exists"
            # Insert new user
            insert_query = "INSERT INTO account (username, firstName, lastName, pword) VALUES (%s, %s, %s, %s)"
            cursor.execute(insert_query, (username, firstName, lastName, encrypted_password))
            connection.commit()
            cursor.close()
            connection.close()
            return True, "User created successfully"
        except Error as e:
            return False, f"Database error: {str(e)}"