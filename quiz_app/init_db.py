from app import app, db, Quiz, Question, User
import json

def init_db():
    with app.app_context():
        # Drop all tables and create them fresh
        db.drop_all()
        db.create_all()
        
        # Create a default admin user
        admin = User(username="admin", email="admin@example.com")
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        
        # Create sample quizzes
        python_quiz = Quiz(
            title="Python Basics",
            description="Test your knowledge of Python fundamentals",
            time_limit=300,  # 5 minutes
            creator_id=admin.id
        )
        
        web_quiz = Quiz(
            title="Web Development",
            description="Test your knowledge of HTML, CSS, and JavaScript",
            time_limit=600,  # 10 minutes
            creator_id=admin.id
        )
        
        # Python quiz questions
        python_questions = [
            {
                "question": "What is the output of print(type([]))?",
                "options": ["<class 'list'>", "<class 'tuple'>", "<class 'set'>", "<class 'dict'>"],
                "correct": "<class 'list'>",
                "points": 1
            },
            {
                "question": "Which of these is not a Python built-in data type?",
                "options": ["list", "tuple", "array", "set"],
                "correct": "array",
                "points": 1
            },
            {
                "question": "What does the 'self' parameter in a class method refer to?",
                "options": [
                    "The class itself",
                    "The instance of the class",
                    "The parent class",
                    "The module containing the class"
                ],
                "correct": "The instance of the class",
                "points": 2
            }
        ]
        
        # Web development questions
        web_questions = [
            {
                "question": "What does HTML stand for?",
                "options": [
                    "Hyper Text Markup Language",
                    "High Tech Modern Language",
                    "Hyper Transfer Markup Language",
                    "Hyper Text Modern Links"
                ],
                "correct": "Hyper Text Markup Language",
                "points": 1
            },
            {
                "question": "Which CSS property is used to change the text color?",
                "options": ["text-color", "color", "font-color", "text-style"],
                "correct": "color",
                "points": 1
            },
            {
                "question": "What is the correct way to write a JavaScript array?",
                "options": [
                    "var colors = (1:'red', 2:'green', 3:'blue')",
                    "var colors = 'red', 'green', 'blue'",
                    "var colors = ['red', 'green', 'blue']",
                    "var colors = 'red' + 'green' + 'blue'"
                ],
                "correct": "var colors = ['red', 'green', 'blue']",
                "points": 2
            }
        ]
        
        # Add quizzes to database
        db.session.add(python_quiz)
        db.session.add(web_quiz)
        db.session.commit()
        
        # Add questions to quizzes
        for q_data in python_questions:
            question = Question(
                quiz_id=python_quiz.id,
                question_text=q_data["question"],
                correct_answer=q_data["correct"],
                points=q_data["points"]
            )
            question.set_options(q_data["options"])
            db.session.add(question)
        
        for q_data in web_questions:
            question = Question(
                quiz_id=web_quiz.id,
                question_text=q_data["question"],
                correct_answer=q_data["correct"],
                points=q_data["points"]
            )
            question.set_options(q_data["options"])
            db.session.add(question)
        
        db.session.commit()
        
        print("Database initialized with sample quizzes!")
        print("Default admin user created:")
        print("Username: admin")
        print("Password: admin123")

if __name__ == "__main__":
    init_db() 