# Exam Paper Converter

A web application that helps you convert exam papers to different difficulty levels and understand complex concepts using AI.

## Features

- Convert exam papers to different difficulty levels (Easy, Medium, Hard)
- Understand complex concepts with AI-powered explanations
- Modern and responsive user interface
- Real-time processing with loading indicators

## Prerequisites

- Python 3.7 or higher
- Google Gemini API key

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd exam-paper-converter
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory and add your Google Gemini API key:
```
GOOGLE_API_KEY=your_api_key_here
```

5. Run the application:
```bash
python main.py
```

6. Open your web browser and navigate to `http://localhost:5000`

## Usage

1. Paste your exam paper text in the input box
2. Choose between "Convert" or "Understand" mode
3. If converting, select the desired difficulty level
4. Click "Process Paper" to generate the result
5. The converted or explained text will appear in the output box

## Project Structure

```
exam-paper-converter/
├── main.py              # Flask application
├── requirements.txt     # Python dependencies
├── .env                # Environment variables (create this)
├── static/
│   └── style.css       # CSS styles
└── templates/
    └── index.html      # HTML template
```

## Contributing

Feel free to submit issues and enhancement requests! 