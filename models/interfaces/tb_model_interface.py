from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Any

class TBInterface(ABC):

    @abstractmethod
    def insert_medform(self, medform_data: Dict[str, Any]) -> Tuple[bool, str]:
        pass

    @abstractmethod
    def custom_nn_predict(self, features: List[Any]) -> Tuple[int, float]:
        pass

    @abstractmethod
    def view_all_medforms(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_medical_form_result(self, form_id: int) -> Tuple[Dict[str, Any], float]:
        pass