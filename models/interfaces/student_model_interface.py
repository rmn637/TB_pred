from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Any

class StudentInterface(ABC):
    
    @abstractmethod
    def add_student(self, studentnum: str, name: str, course: str, yearstanding: str) -> Tuple[bool, str]:
        pass
    
    @abstractmethod
    def search_students(self, name: str) -> Tuple[bool, str, List[Dict[str, Any]]]:
        pass
    
    @abstractmethod
    def update_student(self, name_to_identify: str, updates: Dict[str, str]) -> Tuple[bool, str, int]:
        pass
    
    @abstractmethod
    def delete_student(self, name: str) -> Tuple[bool, str, int]:
        pass
    
    @abstractmethod
    def get_all_students(self) -> Tuple[bool, str, List[Dict[str, Any]]]:
        pass
    
    @abstractmethod
    def get_student_by_id(self, studentnum: str) -> Tuple[bool, str, Dict[str, Any]]:
        pass