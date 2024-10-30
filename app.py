from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

from datetime import date
from enum import Enum

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'XVL0X0UAU8NqfSoH'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Redirect to login page if not logged in



# Enum for Event Status
class EventStatus(Enum):
    Proposed = "Proposed"
    Confirmed = "Confirmed"
    Past = "Past"

# Event Model
class Event(db.Model):
    eventId = db.Column(db.Integer, primary_key=True)
    eventName = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    tag = db.Column(db.Enum(EventStatus), nullable=False)  
    votes = db.Column(db.Integer, default=0)

# Vote Model
class Vote(db.Model):
    voteId = db.Column(db.Integer, primary_key=True)
    eventId = db.Column(db.Integer, db.ForeignKey('event.eventId'), nullable=False)
    voteCount = db.Column(db.Integer, default=0)

# User Model
class User(db.Model, UserMixin):  # Ensure User inherits UserMixin
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    # Flask-Login requires these methods
    @property
    def is_active(self):
        return True  # or implement logic to check if the user is active

    @property
    def is_authenticated(self):
        return True  # This indicates the user is logged in

    @property
    def is_anonymous(self):
        return False  # This indicates the user is not anonymous

    def get_id(self):
        return str(self.user_id)  # Return the user ID as a string

# Initialize database
with app.app_context():
    db.create_all()  # Create the events table
    db.session.commit()

    # Create an admin user if it doesn't already exist
    admin_username = 'admin'
    admin_password = 'your_secure_password'  # Choose a strong password

    # Check if the admin user already exists
    existing_user = User.query.filter_by(username=admin_username).first()
    if not existing_user:
        # Create new admin user
        new_admin = User(username=admin_username)
        new_admin.set_password(admin_password)  # Hash the password

        # Add and commit to the database
        db.session.add(new_admin)
        db.session.commit()
        print(f"Admin user '{admin_username}' added successfully!")
    else:
        print("Admin user already exists.")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    events = Event.query.all()  # Fetch all events from the database
    return render_template('index.html', events=events)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)  # Log the user in
            return redirect(url_for('admin_index'))  # Redirect to admin page
        else:
            flash('Invalid username or password')

    return render_template('login.html')

@app.route('/admin')
@login_required
def admin_index():
    events = Event.query.all()  # Fetch all events
    return render_template('admin.html', events=events) 

#VOTING SYSTEM AND CONFIRMATION MESSAGE
@app.route('/events/<int:event_id>', methods=['GET', 'POST'])
def admin_event_detail(event_id):
    event = Event.query.get_or_404(event_id)  # Fetch the event by ID

    if request.method == 'POST':
        # Increment vote count
        event.votes += 1  # Increment the vote count directly on the event object
        db.session.commit()  # Save the changes to the database

        flash('Thank you for your vote!')  # Add a confirmation message
        return redirect(url_for('admin_event_detail', event_id=event_id))

    return render_template('event.html', event=event)

#EVENT EDIT
@app.route('/events/add', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        eventId = request.form['eventId']
        eventName = request.form['eventName']
        description = request.form.get('description', '')
        event_date = request.form['date']
        location = request.form['location']
        tag = request.form['tag']
        
        new_event = Event(
            eventId=eventId,
            eventName=eventName,
            description=description,
            date=date.fromisoformat(event_date),
            location=location,
            tag=EventStatus[tag],  
            votes=0
        )
        
        db.session.add(new_event)
        db.session.commit()
        
        return redirect(url_for('admin_index'))
    return render_template('add_event.html')

#LOGOUT
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/events/edit/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)

    if request.method == 'POST':
        # Update the event with new form data
        event.eventName = request.form['eventName']
        event.description = request.form.get('description', '')
        event.date = date.fromisoformat(request.form['date'])
        event.location = request.form['location']
        event.tag = EventStatus[request.form['tag']]

        db.session.commit()
        flash('Event updated successfully!', 'success')
        return redirect(url_for('admin_index'))

    return render_template('edit_event.html', event=event, EventStatus=EventStatus)

@app.route('/events/delete/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return redirect(url_for('admin_index'))

if __name__ == '__main__':
    app.run(debug=True)