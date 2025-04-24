from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import google.generativeai as genai
import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import json
from models import db  # Import your db model only

# Load environment variables
load_dotenv()

app = Flask(__name__, instance_relative_config=False)  # Prevent instance folder creation

# Configure Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")
genai.configure(api_key=GOOGLE_API_KEY)

# List available models
available_models = genai.list_models()
print("Available models:", [m.name for m in available_models])

# Use the standard model name
model = genai.GenerativeModel('models/gemini-1.5-flash')  # Back to original name

# Configure Flask-SQLAlchemy
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)  # Initialize db here
login_manager = LoginManager(app)
login_manager.login_view = 'home'

# File to store user data
USERS_FILE = 'users.json'

# -------------------- UPDATED USER MODEL --------------------
class User(UserMixin, db.Model):
    __tablename__ = 'user'  # Specify the table name explicitly
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    institution = db.Column(db.String(255))
    education_level = db.Column(db.String(50), nullable=True)  # Change to nullable=True

    @staticmethod
    def get(user_id):
        return User.query.get(int(user_id))  # Ensure ID is converted to int

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Define available tasks
    available_tasks = [
        {
            'id': 'generate_exam_questions',
            'title': 'Generate Exam Questions',
            'description': 'Create custom exam questions for any subject with different difficulty levels'
        },
        {
            'id': 'generate_exam_paper',
            'title': 'Generate Full Exam Paper',
            'description': 'Create a complete exam paper with multiple sections and mark distribution'
        },
        {
            'id': 'get_syllabus',
            'title': 'Generate Syllabus',
            'description': 'Create a detailed syllabus for any subject at your education level'
        },
        {
            'id': 'important_questions',
            'title': 'Important Questions',
            'description': 'Get most important questions and answers for exam preparation'
        },
        {
            'id': 'study_package',
            'title': 'Generate Study Package',
            'description': 'Get a complete study package including syllabus, important topics, and practice questions'
        }
    ]
    return render_template('dashboard.html', tasks=available_tasks)

@app.route('/generate', methods=['POST'])
@login_required
def generate_questions():
    try:
        data = request.json
        subject = data.get('subject', '')
        question_type = data.get('type', 'questions')  # New: 'questions', 'syllabus', or 'practice'
        difficulty = data.get('difficulty', 'medium')
        num_questions = data.get('num_questions', 5)
        
        # Input validation
        if not subject:
            return jsonify({
                'success': False,
                'error': 'Subject is required'
            }), 400
            
        if difficulty not in ['easy', 'medium', 'hard']:
            difficulty = 'medium'
            
        if not isinstance(num_questions, int) or num_questions < 1 or num_questions > 20:
            num_questions = 5

        # Handle different types of requests
        if question_type == 'syllabus':
            prompt = f"""
            Generate a comprehensive syllabus for {subject}. Include:
            
            1. Course Overview
            2. Learning Objectives
            3. Main Topics:
               - Detailed breakdown of each topic
               - Key concepts to master
               - Recommended study hours
            4. Prerequisites
            5. Learning Resources
            6. Assessment Structure
            
            Format the response in a clear, structured manner suitable for {difficulty} level students.
            """
        
        elif question_type == 'practice':
            prompt = f"""
            Generate {num_questions} practice problems for {subject} at {difficulty} level.
            
            For each problem:
            1. Problem Statement
            2. Step-by-step solution
            3. Key concepts used
            4. Common mistakes to avoid
            5. Additional practice tips
            
            Make sure to show all work and explain each step thoroughly.
            """
            
        else:  # Default question generation
            prompt = f"""
            Generate {num_questions} {difficulty}-level exam questions for the subject: {subject}
            
            Follow this exact format for each question:

            Question [number]:
            [Question text]
            
            Options:
            A) [Option A]
            B) [Option B]
            C) [Option C]
            D) [Option D]
            
            Correct Answer: [Letter]
            
            Explanation:
            [Detailed explanation why this is the correct answer]
            
            -------------------
            
            Make sure to:
            1. Use clear and concise language
            2. Include relevant technical terms for {subject}
            3. Make questions appropriate for {difficulty} difficulty level
            4. Ensure all options are plausible but only one is correct
            5. Provide thorough explanations that help with learning
            """

        response = model.generate_content(prompt)
        
        return jsonify({
            'success': True,
            'result': response.text,
            'metadata': {
                'subject': subject,
                'type': question_type,
                'difficulty': difficulty,
                'num_questions': num_questions
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/get_questions', methods=['POST'])
def get_specific_questions():
    try:
        data = request.json
        topic = data.get('topic', '')
        num_questions = data.get('num_questions', 3)

        prompt = f"""
        Generate {num_questions} specific questions about: {topic}
        
        For each question:
        1. Provide the detailed question
        2. Include a comprehensive answer
        3. Add relevant examples if applicable
        
        Format the response clearly with proper numbering.
        """

        response = model.generate_content(prompt)
        return jsonify({
            'success': True,
            'result': response.text
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/generate_exam_paper', methods=['GET', 'POST'])
def generate_exam_paper():
    if request.method == 'GET':
        return render_template('generate_exam_paper.html')  # Ensure you have this template
    try:
        data = request.json
        subject = data.get('subject', '')
        duration = data.get('duration', '3 hours')
        total_marks = data.get('total_marks', 100)

        prompt = f"""
        Generate a complete exam paper for {subject} with the following specifications:
        - Duration: {duration}
        - Total Marks: {total_marks}
        
        Include:
        1. Clear instructions
        2. Multiple sections (objective, subjective, etc.)
        3. Mark distribution for each question
        4. Space for answers
        
        Format it like a professional exam paper.
        """

        response = model.generate_content(prompt)
        return jsonify({
            'success': True,
            'result': response.text
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/get_syllabus', methods=['GET', 'POST'])
def get_syllabus():
    if request.method == 'GET':
        return render_template('get_syllabus.html')  # Ensure you have this template
    try:
        data = request.json
        subject = data.get('subject', '')
        level = data.get('level', 'undergraduate')

        prompt = f"""
        Generate a detailed syllabus for {subject} at {level} level.
        
        Include:
        1. Course overview
        2. Learning objectives
        3. Main topics and subtopics
        4. Recommended readings
        5. Assessment methods
        
        Format it in a clear, structured manner.
        """

        response = model.generate_content(prompt)
        return jsonify({
            'success': True,
            'result': response.text
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/important_questions', methods=['GET', 'POST'])
def get_important_questions():
    if request.method == 'GET':
        return render_template('important_questions.html')  # Ensure you have this template
    try:
        data = request.json
        subject = data.get('subject', '')
        exam_type = data.get('exam_type', 'final')

        prompt = f"""
        Generate most important questions for {subject} ({exam_type} exam).
        
        For each question:
        1. Explain why it's important
        2. Provide a detailed answer
        3. Include common mistakes to avoid
        4. Add relevant examples or case studies
        
        Focus on questions that frequently appear in exams and are crucial for understanding the subject.
        """

        response = model.generate_content(prompt)
        return jsonify({
            'success': True,
            'result': response.text
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/generate_study_package', methods=['GET', 'POST'])
def generate_study_package():
    if request.method == 'GET':
        return render_template('generate_study_package.html')  # Ensure you have this template
    try:
        data = request.json
        subject = data.get('subject', '')
        level = data.get('level', 'undergraduate')
        
        # Generate all components
        syllabus_prompt = f"""
        Generate a concise syllabus outline for {subject} at {level} level.
        Include main topics and learning objectives only.
        """
        syllabus = model.generate_content(syllabus_prompt)

        important_topics_prompt = f"""
        List 5 most important topics in {subject} that students must master.
        Explain why each topic is crucial.
        """
        important_topics = model.generate_content(important_topics_prompt)

        practice_questions_prompt = f"""
        Generate 3 practice questions for {subject}:
        - 1 easy question
        - 1 medium question
        - 1 challenging question
        Include answers and explanations.
        """
        practice_questions = model.generate_content(practice_questions_prompt)

        study_tips_prompt = f"""
        Provide 5 effective study strategies specifically for mastering {subject}.
        Include time management and practice tips.
        """
        study_tips = model.generate_content(study_tips_prompt)

        # Combine all components
        return jsonify({
            'success': True,
            'package': {
                'syllabus': syllabus.text,
                'important_topics': important_topics.text,
                'practice_questions': practice_questions.text,
                'study_tips': study_tips.text
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/generate_exam_questions')
def generate_exam_questions():
    return render_template('generate_exam_questions.html')

@app.route('/loading')
def loading():
    return render_template('loading_animation.html')

@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        institution = data.get('institution', None)

        if not name or not email or not password:
            return jsonify({'success': False, 'error': 'All fields are required!'}), 400

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'success': False, 'error': 'Email already registered!'}), 409

        hashed_password = generate_password_hash(password)
        new_user = User(name=name, email=email, password=hashed_password, institution=institution)

        db.session.add(new_user)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Sign up successful!'}), 201

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        print(f"Attempting to log in with email: {email}")  # Debug statement

        user = User.query.filter_by(email=email).first()
        if not user:
            print("User not found")  # Debug statement
            return jsonify({'success': False, 'error': 'Invalid email or password'}), 401

        if not check_password_hash(user.password, password):
            print("Password does not match")  # Debug statement
            return jsonify({'success': False, 'error': 'Invalid email or password'}), 401

        login_user(user)
        return jsonify({'success': True, 'user': {'name': user.name, 'email': user.email}})

    except Exception as e:
        print(f"Error during login: {str(e)}")  # Debug statement
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))  # Ensure a valid response is returned

@app.route('/users', methods=['GET'])
def list_users():
    users = User.query.all()
    return jsonify([{'name': user.name, 'email': user.email} for user in users])

@app.route('/create_dummy_user', methods=['POST'])
def create_dummy_user():
    try:
        # Dummy user data
        dummy_user = User(
            name='Test User',
            email='test@example.com',
            password=generate_password_hash('yourpassword')  # Use a hashed password
        )

        # Check if the user already exists
        existing_user = User.query.filter_by(email=dummy_user.email).first()
        if existing_user:
            return jsonify({'success': False, 'error': 'Dummy user already exists!'}), 409

        # Add the dummy user to the database
        db.session.add(dummy_user)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Dummy user created successfully!'}), 201

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/guest', methods=['POST'])
def guest():
    try:
        data = request.json
        name = data.get('name')

        if not name:
            return jsonify({'success': False, 'error': 'Name is required!'}), 400

        # Respond with a greeting message
        return jsonify({'success': True, 'message': f'Hello, {name}! Welcome to our application!'}), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/guest_login', methods=['POST'])
def guest_login():
    try:
        # Generate a guest name or use a default name
        guest_name = "Guest User"  # You can customize this or generate dynamically

        # Store guest information in the session
        session['guest_name'] = guest_name

        return jsonify({'success': True, 'message': f'Logged in as {guest_name}'}), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/guest_login')
def guest_login_page():
    return render_template('guest_login.html')

# -------------------- DATABASE INITIALIZATION --------------------
with app.app_context():
    db.create_all()  # Ensure this is called only once

if __name__ == '__main__':
    app.run(debug=True)
