from flask import jsonify, render_template

class StudentView:
    @staticmethod
    def success_response(message, data=None, status_code=200):
        response = {'success': True, 'message': message}
        if data:
            response['data'] = data
        return jsonify(response), status_code
    
    @staticmethod
    def error_response(message, status_code=400):
        return jsonify({'success': False, 'error': message}), status_code
    
    @staticmethod
    def student_added_response():
        return StudentView.success_response('Data Inserted in the Table', status_code=201)
    
    @staticmethod
    def search_results_response(results):
        return StudentView.success_response(
            'Search completed', 
            {'data': results, 'count': len(results)}
        )
    
    @staticmethod
    def update_response(message, affected_rows):
        return StudentView.success_response(
            message, 
            {'affected_rows': affected_rows}
        )
    
    @staticmethod
    def delete_response(message, affected_rows):
        return StudentView.success_response(
            message, 
            {'affected_rows': affected_rows}
        )
    
    @staticmethod
    def render_landing():
        return render_template('landing.html')
    
    @staticmethod
    def render_dashboard():
        return render_template('dashboard.html')
    
    @staticmethod
    def render_med_form():
        return render_template('med_form.html')