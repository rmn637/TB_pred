import pickle
from .database.connection import DatabaseConnection
from mysql.connector import Error

class TBModel:
    def __init__(self, db_config, model_path='models/predictive_model/random_forest.pkl'):
        self.db_connection = DatabaseConnection(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database']
        )
        # Load ML model
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)

    def insert_medform(self, medform_data):
        """
        Insert a new medical form record into the tb_assessments table.
        medform_data: dict with keys matching the table columns (except 'id').
        """
        connection = self.db_connection.get_connection()
        if not connection:
            return False, "Database connection failed"
        try:
            cursor = connection.cursor()
            # Exclude 'id' if present (auto-increment)
            if 'id' in medform_data:
                medform_data = {k: v for k, v in medform_data.items() if k != 'id'}
            columns = ', '.join(medform_data.keys())
            placeholders = ', '.join(['%s'] * len(medform_data))
            query = f"INSERT INTO tb_assessments ({columns}) VALUES ({placeholders})"
            cursor.execute(query, tuple(medform_data.values()))
            connection.commit()
            cursor.close()
            connection.close()
            return True, "Medical form inserted successfully"
        except Error as e:
            return False, f"Database error: {str(e)}"

    def predict_tb(self, features):
        """
        Predict TB risk using the loaded ML model.
        features: list or array of input features in the correct order.
        Returns: prediction (e.g., 0/1 or probability)
        """
        try:
            prediction = self.model.predict([features])
            if hasattr(self.model, "predict_proba"):
                proba = self.model.predict_proba([features])
                return int(prediction[0]), float(proba[0][1])
            return int(prediction[0]), None
        except Exception as e:
            return None, f"Prediction error: {str(e)}"

    def view_all_medforms(self):
        """
        Retrieve all medical form records from the tb_assessments table.
        Returns: list of dicts
        """
        connection = self.db_connection.get_connection()
        if not connection:
            return []
        try:
            cursor = connection.cursor(dictionary=True)
            query = ("SELECT id, patient_id, assessment_date, cough, cough_days, colds, colds_days, fever, fever_days, "
                     "bleeding, dob, loc, chest_pain, body_joint_pain, abdominal_pain, back_pain, nape_pain, "
                     "sore_throat, dizziness, loss_appetite, wounds, eent, allergies, vomiting, gender, final_age, "
                     "results, tb_probability FROM tb_assessments")
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            connection.close()
            return results
        except Error:
            return []