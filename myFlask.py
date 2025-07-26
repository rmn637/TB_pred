from flask import Flask, jsonify, session, redirect, url_for, request, render_template
from flask_cors import CORS
import os
import google.generativeai as genai
from functools import wraps
from controllers.student_controller import StudentController
from controllers.account_controller import AccountController
from controllers.tb_controller import TBController

base_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    __name__,
    static_folder=os.path.join(base_dir, 'views', 'static'),
    template_folder=os.path.join(base_dir, 'views', 'templates')
)
app.secret_key = os.urandom(24)

# Configure CORS to allow credentials (sessions)
CORS(app, supports_credentials=True, origins=["http://localhost:1234", "http://127.0.0.1:1234"])

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'TB_Finals'
}

student_controller = StudentController(DB_CONFIG)
account_controller = AccountController(DB_CONFIG)
tb_controller = TBController(DB_CONFIG)

# Myca Support chat Section
genai.configure(api_key="AIzaSyAKyJ2d22a5FOBxNje6Tixb1lISiLAkbpg")
model = genai.GenerativeModel("gemini-2.5-flash")

# Ai contents + personality
system_prompt = """
You are Myca, a virtual assistant designed to support medical professionals—specifically doctors—by providing accurate, concise, and context-aware information related to tuberculosis (TB). Your role is to assist clinicians by offering summaries of current guidelines, treatment protocols, diagnostic tips, and patient communication strategies related to TB.
You respond in a professional and efficient tone—clear, informative, and respectful of the doctor's expertise. You do not explain basic medical concepts unless asked. Assume the user is a trained clinician and focus on enhancing their workflow and decision-making.
If asked about symptoms, medications, diagnostics, or treatment approaches, respond with evidence-informed summaries. When referring to guidelines, prioritize authoritative sources like the WHO, CDC, or national TB programs. Do not speculate on patient-specific outcomes or suggest off-label treatments.
Avoid unnecessary pleasantries or emotional language. Focus on being a reliable, fast, and helpful tool in a clinical environment.

Tone and behavior guidelines:
- Professional and efficient
- Concise and medically accurate
- Assumes the user is a licensed healthcare provider
- Offers support tools, suggestions, and summaries—not direct patient care or prescriptions
- Always defer final judgment to the clinician
"""

@app.route("/myca-chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")
    convo = model.start_chat(history=[
        {"role": "user", "parts": system_prompt},
        {"role": "user", "parts": user_input}
    ])
    response = convo.send_message(user_input)
    return jsonify({"reply": response.text})

# Start
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def home():
    from views.student_view import StudentView
    # Check if user is logged in, if not redirect to login
    if 'user_id' not in session or not session.get('logged_in'):
        return redirect(url_for('login'))
    return StudentView.render_landing()

@app.route('/dashboard')
@login_required
def dashboard():
    from views.student_view import StudentView
    return StudentView.render_dashboard()

@app.route('/med_form')
@login_required
def med_form():
    from views.student_view import StudentView
    return StudentView.render_med_form()

@app.route('/submit_medical_form', methods=['POST'])
@login_required
def submit_medical_form():
    response = tb_controller.submit_medical_form()
    if response[1] == 200 and request.content_type != 'application/json':
        return redirect(url_for('result'))
    return response

@app.route('/result', methods=['GET'])
@login_required
def result(form_id):
    return tb_controller.render_medical_form_result(form_id)

@app.route('/medform_list', methods=['GET'])
@login_required
def medform_list():
    return tb_controller.list_medforms()

@app.route('/login', methods=['GET', 'POST'])
def login():
    from views.account_view import AccountView
    
    # If already logged in, redirect to home
    if 'user_id' in session and session.get('logged_in'):
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        # Handle login POST request
        response = account_controller.login_user()
        # If login was successful and it's a form submission, redirect
        if response[1] == 200 and request.content_type != 'application/json':
            return redirect(url_for('home'))
        return response
    
    return AccountView.render_login()

@app.route('/register', methods=['GET', 'POST'])
def register():
    from views.account_view import AccountView
    
    if request.method == 'POST':
        # Handle registration POST request
        response = account_controller.register_user()
        # If registration was successful and it's a form submission, redirect to login
        if response[1] == 201 and request.content_type != 'application/json':
            return redirect(url_for('login'))
        return response
    
    return AccountView.render_register()

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Flask API is running'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1234, debug=True)