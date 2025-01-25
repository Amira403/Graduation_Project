# Quiz Application

An interactive quiz application built with Flask that allows users to take timed quizzes and track their progress.

## Features

- User authentication (register/login)
- Multiple choice questions
- Timed quizzes
- Score tracking
- Detailed results with correct/incorrect answers
- Responsive design
- REST API endpoints

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the database:
```bash
python init_db.py
```

4. Run the application:
```bash
python app.py
```

5. Visit http://localhost:5000 in your browser

## Sample Quizzes

The initialization script creates two sample quizzes:
- Python Basics (5 minutes)
- Web Development (10 minutes)

## API Endpoints

- GET `/api/quizzes` - List all quizzes
- GET `/api/quiz/<quiz_id>` - Get quiz details and questions

## Development

To add new quizzes, modify the `init_db.py` script or use the API endpoints (to be implemented). 