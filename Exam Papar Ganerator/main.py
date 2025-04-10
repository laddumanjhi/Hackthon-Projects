from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import random
import json
import os
import hashlib
import secrets
import google.generativeai as genai
from datetime import datetime

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # For session management

# Configure Gemini API
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"  # Replace with your actual API key
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Sample question bank (you can expand this with more questions)
question_bank = {
    'math': [
        {'question': 'What is 2 + 2?', 'options': ['3', '4', '5', '6'], 'answer': '4'},
        {'question': 'What is 5 * 5?', 'options': ['20', '25', '30', '35'], 'answer': '25'},
        {'question': 'What is 10 / 2?', 'options': ['3', '4', '5', '6'], 'answer': '5'},
    ],
    'science': [
        {'question': 'What is the chemical symbol for water?', 'options': ['H2O', 'CO2', 'O2', 'N2'], 'answer': 'H2O'},
        {'question': 'What planet is known as the Red Planet?', 'options': ['Venus', 'Mars', 'Jupiter', 'Saturn'], 'answer': 'Mars'},
    ]
}

# Function to load data from JSON files
def load_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return {"users": []} if filename == "users.json" else {"subjects": []}

# Function to save data to JSON files
def save_data(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Load initial data
users_data = load_data("users.json")
subjects_data = load_data("subjects.json")

@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', 
                         username=session['username'],
                         subjects=subjects_data.get('subjects', []))

@app.route('/add_subject', methods=['POST'])
def add_subject():
    if 'username' not in session:
        return jsonify({'error': 'Please login first'}), 401
        
    data = request.json
    subject_name = data.get('subject_name')
    description = data.get('description')
    
    if not subject_name:
        return jsonify({'error': 'Subject name is required'}), 400
        
    # Add subject to the list
    subjects_data['subjects'].append({
        'name': subject_name,
        'description': description,
        'created_by': session['username'],
        'created_at': datetime.now().isoformat()
    })
    
    save_data(subjects_data, "subjects.json")
    return jsonify({'message': 'Subject added successfully'})

@app.route('/generate_questions', methods=['POST'])
def generate_questions():
    if 'username' not in session:
        return jsonify({'error': 'Please login first'}), 401
        
    data = request.json
    subject = data.get('subject')
    num_questions = int(data.get('num_questions', 5))
    difficulty = data.get('difficulty', 'medium')
    
    if not subject:
        return jsonify({'error': 'Subject is required'}), 400
    
    # Generate questions using Gemini API
    prompt = f"""
    Generate {num_questions} {difficulty} difficulty level questions for the subject {subject}.
    Each question should have:
    1. A clear question text
    2. 4 multiple choice options
    3. The correct answer
    
    Format the response as a JSON array where each question has:
    - question: the question text
    - options: array of 4 options
    - answer: the correct answer
    
    Example format:
    [
        {{
            "question": "What is...?",
            "options": ["A", "B", "C", "D"],
            "answer": "A"
        }}
    ]
    """
    
    try:
        response = model.generate_content(prompt)
        questions = json.loads(response.text)
        return jsonify({'questions': questions})
    except Exception as e:
        return jsonify({'error': f'Failed to generate questions: {str(e)}'}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        users_data = load_data("users.json")
        for user in users_data['users']:
            if user['username'] == username and user['password'] == hash_password(password):
                session['username'] = username
                return redirect(url_for('home'))
        
        return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        
        users_data = load_data("users.json")
        
        # Check if username already exists
        for user in users_data['users']:
            if user['username'] == username:
                return render_template('signup.html', error='Username already exists')
        
        # Add new user
        users_data['users'].append({
            'username': username,
            'password': hash_password(password),
            'email': email
        })
        
        save_data(users_data, "users.json")
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        users_data = load_data("users.json")
        
        for user in users_data['users']:
            if user['email'] == email:
                # In a real application, you would send a password reset email here
                return render_template('forgot_password.html', 
                                    message='Password reset instructions have been sent to your email')
        
        return render_template('forgot_password.html', 
                             error='No account found with that email address')
    return render_template('forgot_password.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/generate_paper', methods=['POST'])
def generate_paper():
    if 'username' not in session:
        return jsonify({'error': 'Please login first'}), 401
        
    data = request.json
    subject = data.get('subject', 'math')
    num_questions = int(data.get('num_questions', 5))
    
    # Get questions for the selected subject
    subject_questions = question_bank.get(subject, [])
    
    # Randomly select questions
    selected_questions = random.sample(subject_questions, min(num_questions, len(subject_questions)))
    
    return jsonify({'questions': selected_questions})

if __name__ == '__main__':
    app.run(debug=True)
