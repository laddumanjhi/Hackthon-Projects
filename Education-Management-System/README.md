# Education Management System

A modern education management system built with React and Flask.

## Features

- User management (students, teachers, admins)
- Course management
- Dashboard with statistics
- Modern UI with Material-UI

## Prerequisites

- Node.js (v14 or higher)
- Python (v3.8 or higher)
- pip (Python package manager)

## Installation

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Unix/MacOS:
     ```bash
     source venv/bin/activate
     ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the backend server:
   ```bash
   python run.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

## Usage

1. The backend server will run on `http://localhost:5000`
2. The frontend application will run on `http://localhost:3000`
3. Open your browser and navigate to `http://localhost:3000`

## API Endpoints

- GET `/api/users` - Get all users
- GET `/api/courses` - Get all courses
- POST `/api/courses` - Create a new course

## License

This project is licensed under the MIT License. 