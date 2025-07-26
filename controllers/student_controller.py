from flask import request
from models.student_model import StudentModel
from views.student_view import StudentView

class StudentController:
    def __init__(self, db_config):
        self.model = StudentModel(db_config)
        self.view = StudentView()
    
    def add_record(self):
        try:
            if request.method == 'GET':
                studentnum = request.args.get('studentnum')
                name = request.args.get('name')
                course = request.args.get('course')
                yearstanding = request.args.get('yearstanding')
            else:
                data = request.get_json() if request.is_json else request.form
                studentnum = data.get('studentnum')
                name = data.get('name')
                course = data.get('course')
                yearstanding = data.get('yearstanding')
            
            if not all([studentnum, name, course, yearstanding]):
                return self.view.error_response('All fields are required')
            
            success, message = self.model.add_student(studentnum, name, course, yearstanding)
            
            if success:
                return self.view.student_added_response()
            else:
                return self.view.error_response(message, 500)
                
        except Exception as e:
            return self.view.error_response(f'Server error: {str(e)}', 500)
    
    def search_record(self):
        try:
            name = request.args.get('name')
            
            if not name:
                return self.view.error_response('Name parameter is required')
            
            success, message, results = self.model.search_students(name)
            
            if success:
                return self.view.search_results_response(results)
            else:
                return self.view.error_response(message, 500)
                
        except Exception as e:
            return self.view.error_response(f'Server error: {str(e)}', 500)
    
    def update_record(self):
        try:
            if request.method == 'GET':
                name_to_identify = request.args.get('name_to_identify')
                updates = {
                    'name': request.args.get('new_name'),
                    'studentnum': request.args.get('studentnum'),
                    'course': request.args.get('course'),
                    'yearstanding': request.args.get('yearstanding')
                }
            else:
                data = request.get_json() if request.is_json else request.form
                name_to_identify = data.get('name_to_identify')
                updates = {
                    'name': data.get('new_name'),
                    'studentnum': data.get('studentnum'),
                    'course': data.get('course'),
                    'yearstanding': data.get('yearstanding')
                }
            
            if not name_to_identify:
                return self.view.error_response('Name to identify record is required for update')
            
            success, message, affected_rows = self.model.update_student(name_to_identify, updates)
            
            if success and affected_rows > 0:
                return self.view.update_response(message, affected_rows)
            elif success and affected_rows == 0:
                return self.view.error_response('No record found or no changes made', 404)
            else:
                return self.view.error_response(message, 500)
                
        except Exception as e:
            return self.view.error_response(f'Server error: {str(e)}', 500)
    
    def delete_record(self):
        try:
            if request.method == 'GET':
                name_to_delete = request.args.get('name')
            else:
                data = request.get_json() if request.is_json else request.form
                name_to_delete = data.get('name')
            
            if not name_to_delete:
                return self.view.error_response('Name parameter is missing for deletion')
            
            success, message, affected_rows = self.model.delete_student(name_to_delete)
            
            if success and affected_rows > 0:
                return self.view.delete_response(message, affected_rows)
            elif success and affected_rows == 0:
                return self.view.error_response('No record found', 404)
            else:
                return self.view.error_response(message, 500)
                
        except Exception as e:
            return self.view.error_response(f'Server error: {str(e)}', 500)