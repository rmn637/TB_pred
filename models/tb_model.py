import pickle
from .database.connection import DatabaseConnection
from mysql.connector import Error
from .interfaces.tb_model_interface import TBInterface
import numpy as np
from .predictive_models.activation_functions import ActivationFunctions
from sklearn.preprocessing import StandardScaler

class TBModel(TBInterface):
    def __init__(self, db_config):
        self.db_connection = DatabaseConnection(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database']
        )
        # Load custom neural network model
        with open('models/predictive_models/custom_neural_net.pkl', 'rb') as f:
            self.custom_model_nn = pickle.load(f)
        # Extract weights and biases
        self.weights_input_h1 = self.custom_model_nn["weights_input_h1"]
        self.bias_h1 = self.custom_model_nn["bias_h1"]
        self.weights_h1_h2 = self.custom_model_nn["weights_h1_h2"]
        self.bias_h2 = self.custom_model_nn["bias_h2"]
        self.weights_h2_h3 = self.custom_model_nn["weights_h2_h3"]
        self.bias_h3 = self.custom_model_nn["bias_h3"]
        self.weights_h3_output = self.custom_model_nn["weights_h3_output"]
        self.bias_output = self.custom_model_nn["bias_output"]

    def insert_medform(self, medform_data):
        """
        Insert a new medical form record into the tb_assessments table.
        medform_data: dict with keys matching the table columns (except 'id').
        After insertion, predict tuberculosis using the custom neural network.
        """
        connection = self.db_connection.get_connection()
        if not connection:
            return False, "Database connection failed", None, None
        try:
            cursor = connection.cursor()
            medform_data = {k: (v if v not in [None, ''] else 0) for k, v in medform_data.items()}
            feature_keys = [k for k in medform_data.keys() if k not in ['id', 'tuberculosis']]
            features = [int(medform_data[k]) if str(medform_data[k]).isdigit() else 0 for k in feature_keys]

            # Predict using custom neural network
            tb_pred = self.custom_nn_predict(features)
            print(tb_pred)
            medform_data['tuberculosis'] = int(tb_pred[0])

            # Prepare SQL query
            columns = ', '.join(medform_data.keys())
            placeholders = ', '.join(['%s'] * len(medform_data))
            query = f"INSERT INTO tb_assessments ({columns}) VALUES ({placeholders})"
            cursor.execute(query, tuple(medform_data.values()))
            connection.commit()
            cursor.close()
            connection.close()

            return True, "Medical form inserted successfully. TB prediction made.", int(tb_pred[0])
        except Error as e:
            return False, f"Database error: {str(e)}", None, None

    def custom_nn_predict(self, X):
        X = np.array(X, dtype=float).reshape(1, -1)
        scaler = StandardScaler()
        X = scaler.fit_transform(X)
        h1_input = np.dot(X, self.weights_input_h1) + self.bias_h1
        h1_output = ActivationFunctions.relu(h1_input)

        h2_input = np.dot(h1_output, self.weights_h1_h2) + self.bias_h2
        h2_output = ActivationFunctions.leaky_relu(h2_input)

        h3_input = np.dot(h2_output, self.weights_h2_h3) + self.bias_h3
        h3_output = ActivationFunctions.sigmoid(h3_input)

        final_input = np.dot(h3_output, self.weights_h3_output) + self.bias_output
        predicted_output = ActivationFunctions.sigmoid(final_input)
        print(predicted_output)
        print((predicted_output > 0.5).astype(int))
        return (predicted_output > 0.5).astype(int)

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
            query = ("SELECT * FROM tb_assessments")
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            connection.close()
            return results
        except Error:
            return []
        
    def get_medical_form_result(self, form_id):
        """
        Retrieve a specific medical form result by ID.
        Returns: dict with form data and TB prediction probability.
        """
        connection = self.db_connection.get_connection()
        if not connection:
            return {}, 0.0
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM tb_assessments WHERE id = %s"
            cursor.execute(query, (form_id,))
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            if result:
                features = [result[key] for key in result if key not in ['id', 'results', 'tb_probability']]
                _, tb_probability = self.predict_tb(features)
                return result, tb_probability
            return {}, 0.0
        except Error as e:
            return {}, 0.0