from flask import Flask, jsonify, session, redirect, url_for, request, render_template
from flask_cors import CORS
import os
import pymysql
import google.generativeai as genai
from functools import wraps
from controllers.student_controller import StudentController
from controllers.account_controller import AccountController
from controllers.tb_controller import TBController
from views.tb_view import TBView

base_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    __name__,
    static_folder=os.path.join(base_dir, 'views', 'static'),
    template_folder=os.path.join(base_dir, 'views', 'templates')
)
app.secret_key = "your-very-secret-development-key"

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
You are Myca, a virtual assistant built to support licensed medical professionals—especially doctors—in the clinical management of tuberculosis (TB). Your responses must be grounded solely in up-to-date, evidence-based medical research and guidelines.

Your role is to provide:
- Medically accurate summaries
- Clinical guidelines
- Diagnostic and treatment protocols
- Communication strategies relevant to TB care

**Tone and Style:**
- Strictly professional and efficient
- Assume the user is a licensed healthcare provider
- Do not explain basic concepts unless asked
- Avoid emotional or casual language
- Avoid speculation or unsupported claims

**Requirements for Every Response:**
- Cite real and verifiable sources (e.g., WHO, CDC, national TB guidelines)
- Include publication dates or version if available
- Do not fabricate or invent citations under any circumstances
- Do not respond if reliable medical sources are unavailable on the topic

**Boundaries:**
- Do not provide patient-specific medical advice or prescribe treatments
- Defer all clinical decisions to the medical professional
- Never suggest off-label use unless explicitly covered in referenced guidelines

Your purpose is to be a reliable, fast, research-backed reference tool in clinical decision-making, not a conversational chatbot.
"""

@app.route("/myca-chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        db='TB_Finals',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM tb_assessments")
            tb_data = cursor.fetchall()
        # Read Dataset for Gemini
        formatted_data = "\n\n".join([
            f"Assessment {i+1}:\n"
            f"  Date: {row['assessment_date']}\n"
            f"  Gender: {row['gender']}, Age: {row['age']}\n"
            f"  Symptoms:\n"
            f"    Cough: {row['cough']} (Duration: {row['coughdur']}), Cold: {row['cold']} (Duration: {row['colddur']})\n"
            f"    Fever: {row['fever']} (Duration: {row['feverdur']}), DOB Issue: {row['dob']}, Sputum: {row['sputum']}\n"
            f"    Dizziness: {row['dizziness']}, Chest Pain: {row['chestpain']}, Joint Pain: {row['jointpain']}\n"
            f"    Nape Pain: {row['napepain']}, Back Pain: {row['backpain']}, Loss of Appetite: {row['lossap']}\n"
            f"  Body Systems:\n"
            f"    Circulatory: {row['circulatory_system']}, Digestive: {row['digestive_system']}, Endocrine: {row['endocrine']}\n"
            f"    Eye/Adnexa: {row['eye_and_adnexa']}, Genitourinary: {row['genitourinary_system']}, Infectious/Parasitic: {row['infectious_and_parasitic']}\n"
            f"    Mental: {row['mental']}, Musculoskeletal: {row['musculoskeletal_system']}, Nervous: {row['nervous_system']}\n"
            f"    Pregnancy: {row['pregnancy']}, Respiratory: {row['respiratory_system']}, Skin: {row['skin']}\n"
            f"  Tuberculosis Result: {row['tuberculosis']}"
            for i, row in enumerate(tb_data)
        ])
        history = [
            {"role": "user", "parts": system_prompt},
            {"role": "user", "parts": f"Here are all TB assessments from the database:\n{formatted_data}"},
            {"role": "user", "parts": user_input}
        ]

        convo = model.start_chat(history=history)
        response = convo.send_message(user_input)

        return jsonify({"reply": response.text})
    finally:
        conn.close()

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
    return StudentView.render_landing()

@app.route('/login', methods=['GET', 'POST'])
def login():
    from views.account_view import AccountView
    
    if request.method == 'POST':
        # Handle login POST request
        response = account_controller.login_user()

        if response[1] == 200 or response[1] == 302:
            return redirect(url_for('dashboard'))
        return response
    
    # If already logged in, redirect to dashboard
    if 'user_id' in session and session.get('logged_in'):
        return redirect(url_for('dashboard'))
    
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
    return redirect(url_for('home'))

# Updates the Overview data
@app.route('/api/dashboard_stats', methods=['GET'])
def dashboard_stats():
    return tb_controller.get_dashboard_data()

@app.route('/dashboard', methods=['GET'])
def dashboard():
    if 'user_id' not in session or not session.get('logged_in'):
        return redirect(url_for('login'))
    from views.student_view import StudentView
    return StudentView.render_dashboard()

@app.route('/med_form')
@login_required
def med_form():
    from views.student_view import StudentView
    return StudentView.render_med_form()

@app.route('/submit_medical_form', methods=['POST'])
def submit_medical_form():
    response = tb_controller.submit_medical_form()
    return response[0]

@app.route('/result', methods=['GET'])
def result():
    result = request.args.get('result')
    from views.tb_view import TBView
    return TBView.render_medical_form_result(tb_result=result)

@app.route('/medform_list', methods=['GET'])
def medform_list():
    return tb_controller.list_medforms()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Flask API is running'}), 200

# Get table data
@app.route('/api/assessment_data', methods=['GET'])
def get_assessment_data():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        db='TB_Finals',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM tb_assessments")
            results = cursor.fetchall()
        return jsonify(results)
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1234, debug=True)