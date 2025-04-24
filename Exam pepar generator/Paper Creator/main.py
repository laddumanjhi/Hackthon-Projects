from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure Gemini API
GOOGLE_API_KEY = os.getenv('AIzaSyAECIjd14iLrjmi5RGjYHB-MUu3RvJGjGM')
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_paper():
    try:
        data = request.json
        original_text = data.get('text', '')
        difficulty = data.get('difficulty', 'medium')
        mode = data.get('mode', 'convert')  # 'convert' or 'understand'

        if mode == 'convert':
            prompt = f"""
            Convert the following exam paper to {difficulty} difficulty level. 
            Maintain the same topic and structure but adjust the complexity accordingly.
            
            Original Paper:
            {original_text}
            """
        else:  # understand mode
            prompt = f"""
            Explain the following exam paper in simple terms, breaking down complex concepts.
            Provide clear explanations and examples where appropriate.
            
            Paper:
            {original_text}
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

if __name__ == '__main__':
    app.run(debug=True)
