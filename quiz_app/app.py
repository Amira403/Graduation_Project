from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    quiz_results = db.relationship('QuizResult', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Quiz Model
class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    time_limit = db.Column(db.Integer)  # Time limit in seconds
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    questions = db.relationship('Question', backref='quiz', lazy=True)
    results = db.relationship('QuizResult', backref='quiz', lazy=True)
    creator = db.relationship('User', backref='created_quizzes', lazy=True)

# Question Model
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text, nullable=False)  # JSON string of options
    correct_answer = db.Column(db.String(200), nullable=False)
    points = db.Column(db.Integer, default=1)

    def get_options(self):
        return json.loads(self.options)

    def set_options(self, options_list):
        self.options = json.dumps(options_list)

# Quiz Result Model
class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    time_taken = db.Column(db.Integer)  # Time taken in seconds
    answers = db.Column(db.Text)  # JSON string of user's answers

    def get_answers(self):
        return json.loads(self.answers) if self.answers else {}

    def set_answers(self, answers_dict):
        self.answers = json.dumps(answers_dict)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    quizzes = Quiz.query.all() if current_user.is_authenticated else []
    return render_template('index.html', quizzes=quizzes)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))

        user = User(email=email, username=email.split('@')[0])  # Use part of email as username
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please provide both email and password')
            return redirect(url_for('login'))
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('Email not found')
            return redirect(url_for('login'))
        
        if not user.check_password(password):
            flash('Incorrect password')
            return redirect(url_for('login'))
        
        login_user(user)
        flash('Logged in successfully!')
        next_page = request.args.get('next')
        return redirect(next_page or url_for('index'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/api/quizzes', methods=['GET'])
def get_quizzes():
    quizzes = Quiz.query.all()
    return jsonify([{
        'id': quiz.id,
        'title': quiz.title,
        'description': quiz.description,
        'time_limit': quiz.time_limit
    } for quiz in quizzes])

@app.route('/api/quiz/<int:quiz_id>', methods=['GET'])
@login_required
def get_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = [{
        'id': q.id,
        'question_text': q.question_text,
        'options': q.get_options(),
        'points': q.points
    } for q in quiz.questions]
    
    return jsonify({
        'id': quiz.id,
        'title': quiz.title,
        'description': quiz.description,
        'time_limit': quiz.time_limit,
        'questions': questions
    })

@app.route('/quiz/<int:quiz_id>', methods=['GET'])
@login_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    return render_template('quiz.html', quiz=quiz)

@app.route('/quiz/<int:quiz_id>/submit', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    answers = request.json.get('answers', {})
    time_taken = request.json.get('time_taken')
    
    score = 0
    for question in quiz.questions:
        if str(question.id) in answers and answers[str(question.id)] == question.correct_answer:
            score += question.points
    
    result = QuizResult(
        user_id=current_user.id,
        quiz_id=quiz_id,
        score=score,
        time_taken=time_taken
    )
    result.set_answers(answers)
    
    db.session.add(result)
    db.session.commit()
    
    return jsonify({
        'score': score,
        'total_points': sum(q.points for q in quiz.questions),
        'time_taken': time_taken
    })

@app.route('/view_results')
@login_required
def view_results():
    results = QuizResult.query.filter_by(user_id=current_user.id).order_by(QuizResult.completed_at.desc()).all()
    return render_template('results.html', results=results)

@app.route('/create_quiz', methods=['GET', 'POST'])
@login_required
def create_quiz():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        time_limit = int(request.form.get('time_limit')) * 60  # Convert minutes to seconds

        quiz = Quiz(
            title=title,
            description=description,
            time_limit=time_limit,
            creator_id=current_user.id
        )
        db.session.add(quiz)
        db.session.commit()

        # Process questions
        questions_data = []
        i = 0
        while True:
            question_text = request.form.get(f'questions[{i}][text]')
            if not question_text:
                break

            options = request.form.get(f'questions[{i}][options]').split('\n')
            options = [opt.strip() for opt in options if opt.strip()]
            correct_answer = request.form.get(f'questions[{i}][correct_answer]')
            points = int(request.form.get(f'questions[{i}][points]', 1))

            question = Question(
                quiz_id=quiz.id,
                question_text=question_text,
                correct_answer=correct_answer,
                points=points
            )
            question.set_options(options)
            db.session.add(question)
            i += 1

        db.session.commit()
        flash('Quiz created successfully!')
        return redirect(url_for('index'))

    return render_template('create_quiz.html')

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()  # Drop all existing tables
        db.create_all()  # Create all tables fresh
    app.run(debug=True) 