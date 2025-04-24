from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import random
import json
import os
import hashlib
import secrets
import google.generativeai as genai
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # For session management

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Function to load data from JSON files
def load_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return {"users": []}

# Function to save data to JSON files
def save_data(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Load initial data
users_data = load_data("users.json")

@app.route('/')
def home():
    return render_template('index.html')  # Directly render index.html

@app.route('/generate_questions', methods=['POST'])
def generate_questions():
    # Remove the login check
    # if 'username' not in session:
    #     return jsonify({'error': 'Please login first'}), 401
        
    data = request.json
    subject = data.get('subject')
    num_questions = int(data.get('num_questions', 5))
    difficulty = data.get('difficulty', 'medium')
    
    if not subject:
        return jsonify({'error': 'Subject is required'}), 400
    
    # Generate questions using Gemini API
    prompt = f"""You are a question generator. Generate exactly {num_questions} {difficulty} difficulty level questions for {subject}.
    Each question must follow this exact JSON format:
    {{
        "question": "The question text here",
        "options": ["Option A", "Option B", "Option C", "Option D"],
        "answer": "The correct option letter (A, B, C, or D)"
    }}

    Return the questions as a JSON array. Do not include any other text or explanation.
    Example response:
    [
        {{
            "question": "What is 2+2?",
            "options": ["3", "4", "5", "6"],
            "answer": "B"
        }},
        {{
            "question": "What is 5*5?",
            "options": ["20", "25", "30", "35"],
            "answer": "B"
        }}
    ]

    Remember:
    1. Return ONLY the JSON array
    2. Each question must have exactly 4 options
    3. The answer must be one of: A, B, C, or D
    4. Do not include any other text or explanation
    """
    
    try:
        response = model.generate_content(prompt)
        # Get the text content from the response
        response_text = response.text.strip()
        print("Raw API Response:", response_text)  # Debug print
        
        # Try to parse the response as JSON
        try:
            # Find the first [ and last ] to extract just the JSON array
            start = response_text.find('[')
            end = response_text.rfind(']') + 1
            if start == -1 or end == 0:
                raise ValueError("No JSON array found in response")
            
            json_text = response_text[start:end]
            print("Extracted JSON:", json_text)  # Debug print
            
            questions = json.loads(json_text)
            # Validate the structure
            if not isinstance(questions, list):
                raise ValueError("Response is not a list")
            for q in questions:
                if not all(key in q for key in ['question', 'options', 'answer']):
                    raise ValueError("Invalid question structure")
                if not isinstance(q['options'], list) or len(q['options']) != 4:
                    raise ValueError("Invalid options structure")
                if q['answer'] not in ['A', 'B', 'C', 'D']:
                    raise ValueError("Answer must be A, B, C, or D")
            
            return jsonify({'questions': questions})
        except json.JSONDecodeError as e:
            print("JSON Parse Error:", str(e))  # Debug print
            return jsonify({'error': f'Invalid JSON response from AI: {str(e)}', 'raw_response': response_text}), 500
        except ValueError as e:
            print("Validation Error:", str(e))  # Debug print
            return jsonify({'error': f'Invalid response structure: {str(e)}', 'raw_response': response_text}), 500
            
    except Exception as e:
        print("General Error:", str(e))  # Debug print
        return jsonify({'error': f'Failed to generate questions: {str(e)}'}), 500

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
    # Commenting out the logout functionality
    # session.pop('username', None)
    # return redirect(url_for('login'))
    return redirect(url_for('home'))  # Redirect to home instead

def save_user_data(data):
    with open('user.json', 'r+') as file:
        users = json.load(file)
        users.append(data)
        file.seek(0)
        json.dump(users, file)

if __name__ == '__main__':
    app.run(debug=True)
