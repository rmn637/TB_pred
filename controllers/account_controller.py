from flask import request, session
from models.account_model import AccountModel
from views.account_view import AccountView

class AccountController:
    def __init__(self, db_config):
        self.model = AccountModel(db_config)
        self.view = AccountView()
    
    def login_user(self):
        """Handle user login with session management"""
        try:
            data = request.get_json() if request.is_json else request.form
            username = data.get('username') or data.get('uname')
            password = data.get('password') or data.get('pword')
            if not username or not password:
                return self.view.error_response('Username and password are required')
            
            success, user_data = self.model.authenticate_user(username, password)

            if success:
                # Set session data
                session['user_id'] = user_data[0]
                session['username'] = user_data[3]
                session['logged_in'] = True
                return self.view.login_success_response()
            else:
                return self.view.login_failed_response()
                
        except Exception as e:
            return self.view.error_response(f'Server error: {str(e)}', 500)
    
    def register_user(self):
        """Handle user registration"""
        try:
            data = request.get_json() if request.is_json else request.form
            username = data.get('username')
            firstName = data.get('first_name')
            lastName = data.get('last_name')
            password = data.get('password')
            confirm_password = data.get('confirm_password')

            if not all([username, firstName, lastName, password, confirm_password]):
                return self.view.register_failed_response('All fields are required')
            
            if password != confirm_password:
                return self.view.register_failed_response('Passwords do not match')

            success, message = self.model.create_user(username, firstName, lastName, password)
            if success:
                return self.view.register_success_response()
            else:
                return self.view.register_failed_response(message)
                
        except Exception as e:
            return self.view.error_response(f'Server error: {str(e)}', 500)