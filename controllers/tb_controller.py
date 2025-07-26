from flask import request, jsonify, render_template
from models.tb_model import TBModel

class TBController:
    def __init__(self, db_config):
        self.tb_model = TBModel(db_config)

    def submit_medical_form(self): # add prediction logic here
        try:
            data = request.get_json() if request.is_json else request.form
            # Extract canonical fields
            fields = [
                'gender', 'age', 'cough', 'coughdur', 'cold', 'colddur', 'fever', 'feverdur', 'dob',
                'sputum', 'dizziness', 'chestpain', 'jointpain', 'napepain', 'backpain', 'lossap',
                'circulatory_system', 'digestive_system', 'endocrine', 'eye_and_adnexa', 'genitourinary_system',
                'infectious_and_parasitic', 'mental', 'musculoskeletal_system', 'nervous_system', 'pregnancy',
                'respiratory_system', 'skin', 'tuberculosis'
            ]
            medform_data = {field: data.get(field) for field in fields}
            # Insert into DB
            success, message = self.tb_model.insert_medform(medform_data)
            if success:
                return jsonify({'success': True, 'message': message}), 200
            else:
                return jsonify({'success': False, 'message': message}), 400
        except Exception as e:
            return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

    def list_medforms(self):
        try:
            medforms = self.tb_model.view_all_medforms()
            return render_template('tb_list.html', medforms=medforms)
        except Exception as e:
            return f"Error: {str(e)}", 500