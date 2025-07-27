from flask import jsonify, render_template, redirect, url_for, session

class AccountView:
    @staticmethod
    def login_success_response():
        """Return success response for AJAX or redirect for form submission"""
        return jsonify({'message': 'Login successful!', 'success': True}), 200
    
    @staticmethod
    def login_failed_response():
        return jsonify({'message': 'Invalid username or password!', 'success': False}), 401
    
    @staticmethod
    def error_response(message, status_code=400):
        return jsonify({'error': message}), status_code
    
    @staticmethod
    def render_login():
        """Render the login page"""
        return render_template('login.html')
    
    @staticmethod
    def render_register():
        """Render the registration page"""
        return render_template('register.html')
    
    @staticmethod
    def register_success_response():
        return jsonify({'message': 'Registration successful! Please login.', 'success': True, 'redirect': '/login'}), 200
    
    @staticmethod
    def register_failed_response(message):
        return jsonify({'message': message, 'success': False}), 400
    
    @staticmethod
    def logout_success():
        """Handle successful logout"""
        session.clear()
        return redirect(url_for('login'))