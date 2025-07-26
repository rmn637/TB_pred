from .database.connection import DatabaseConnection
from mysql.connector import Error
from .interfaces.student_model_interface import StudentInterface
from typing import Dict, List, Tuple, Any

class StudentModel(StudentInterface):
    def __init__(self, db_config):
        self.db_connection = DatabaseConnection(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database']
        )
    
    def add_student(self, studentnum: str, name: str, course: str, yearstanding: str) -> Tuple[bool, str]:
        connection = self.db_connection.get_connection()
        if not connection:
            return False, "Database connection failed"
        
        try:
            cursor = connection.cursor()
            query = "INSERT INTO students (studentnum, name, course, yearstanding) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (studentnum, name, course, yearstanding))
            connection.commit()
            cursor.close()
            connection.close()
            return True, "Student added successfully"
        except Error as e:
            return False, f"Database error: {str(e)}"
    
    def search_students(self, name: str) -> Tuple[bool, str, List[Dict[str, Any]]]:
        connection = self.db_connection.get_connection()
        if not connection:
            return False, "Database connection failed", []
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM students WHERE name LIKE %s"
            cursor.execute(query, (f'%{name}%',))
            results = cursor.fetchall()
            cursor.close()
            connection.close()
            return True, "Search completed", results
        except Error as e:
            return False, f"Database error: {str(e)}", []
    
    def update_student(self, name_to_identify: str, updates: Dict[str, str]) -> Tuple[bool, str, int]:
        connection = self.db_connection.get_connection()
        if not connection:
            return False, "Database connection failed", 0
        
        try:
            cursor = connection.cursor()
            update_fields = []
            update_values = []
            
            for field, value in updates.items():
                if value:
                    update_fields.append(f"{field} = %s")
                    update_values.append(value)
            
            if not update_fields:
                return False, "No fields to update", 0
            
            set_clause = ", ".join(update_fields)
            query = f"UPDATE students SET {set_clause} WHERE name = %s"
            update_values.append(name_to_identify)
            
            cursor.execute(query, update_values)
            affected_rows = cursor.rowcount
            connection.commit()
            cursor.close()
            connection.close()
            
            return True, f"Updated {affected_rows} record(s)", affected_rows
        except Error as e:
            return False, f"Database error: {str(e)}", 0
    
    def delete_student(self, name: str) -> Tuple[bool, str, int]:
        connection = self.db_connection.get_connection()
        if not connection:
            return False, "Database connection failed", 0
        
        try:
            cursor = connection.cursor()
            query = "DELETE FROM students WHERE name = %s"
            cursor.execute(query, (name,))
            affected_rows = cursor.rowcount
            connection.commit()
            cursor.close()
            connection.close()
            
            return True, f"Deleted {affected_rows} record(s)", affected_rows
        except Error as e:
            return False, f"Database error: {str(e)}", 0
    
    def get_all_students(self) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """Get all students from the database."""
        connection = self.db_connection.get_connection()
        if not connection:
            return False, "Database connection failed", []
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM students ORDER BY name"
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            connection.close()
            return True, "All students retrieved", results
        except Error as e:
            return False, f"Database error: {str(e)}", []
    
    def get_student_by_id(self, studentnum: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Get a specific student by student number."""
        connection = self.db_connection.get_connection()
        if not connection:
            return False, "Database connection failed", {}
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM students WHERE studentnum = %s"
            cursor.execute(query, (studentnum,))
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            
            if result:
                return True, "Student found", result
            else:
                return False, "Student not found", {}
        except Error as e:
            return False, f"Database error: {str(e)}", {}