from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

# Configure the database
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'database.db')

# Corrected database URI path (Windows format)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DATABASE_PATH}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)  # For session management and flash messages

db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(100), nullable=False)
    LastName = db.Column(db.String(100), nullable=False)
    PhoneNumber = db.Column(db.String(20), nullable=False)
    DateOfBirth = db.Column(db.String(50), nullable=False)
    Country = db.Column(db.String(100), nullable=False)
    EmailAddress = db.Column(db.String(120), unique=True, nullable=False)
    Education = db.Column(db.String(100), nullable=False)
    CollegeOrOrganization = db.Column(db.String(100), nullable=False)
    PasswordHash = db.Column(db.String(100), nullable=False)  # Store hashed password

# Routes
@app.route('/')
def login_page():
    return render_template('Loginpage.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup_page():
    if request.method == 'POST':
        data = request.form

        # Check if the email already exists
        existing_user = User.query.filter_by(EmailAddress=data['email']).first()
        if existing_user:
            flash('Email address already registered.', 'error')
            return redirect(url_for('signup_page'))

        # Hash the password before saving
        password_hash = generate_password_hash(data['password'], method='pbkdf2:sha256')

        new_user = User(
            FirstName=data['first_name'],
            LastName=data['last_name'],
            PhoneNumber=data['phone_number'],
            DateOfBirth=data['date_of_birth'],
            Country=data['country'],
            EmailAddress=data['email'],
            Education=data['education'],
            CollegeOrOrganization=data['organization'],
            PasswordHash=password_hash  # Store hashed password
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login_page'))
    
    return render_template('StudentSignUp.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    
    # Find user by email
    user = User.query.filter_by(EmailAddress=email).first()

    if user and check_password_hash(user.PasswordHash, password):  # Check password
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid email or password', 'error')  # Show an error message
        return redirect(url_for('login_page'))

@app.route('/dashboard')
def dashboard():
    return "Welcome to the Dashboard!"  # Replace with actual dashboard template

@app.route('/delete_user/<email>', methods=['GET'])
def delete_user(email):
    # Find the user by email
    user = User.query.filter_by(EmailAddress=email).first()
    
    if user:
        # Delete the user
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully.', 'success')
    else:
        flash('User not found.', 'error')
    
    return redirect(url_for('dashboard'))  # Redirect to the dashboard or another page of your choice


if __name__ == '__main__':
    # Create all tables based on the models
    with app.app_context():
        db.create_all()
    app.run(debug=True)
