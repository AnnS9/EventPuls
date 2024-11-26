from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify
from flask_cors import CORS
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from sqlalchemy import select, insert
from datetime import date
from datetime import timedelta
from enum import Enum
import logging
import os

app = Flask(__name__)
app.config['SESSION_COOKIE_HTTPONLY'] = True # Prevent JavaScript from accessing the session cookie
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db' #setting up local database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30) #Setting session lifetime
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') #Getting secret_key assigned securely in environment
app.config['STATIC_FOLDER'] = 'static' #setting up static folder

CORS(app) #enabling CORS
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Redirect to login page if not logged in
logging.basicConfig(level=logging.DEBUG)
migrate = Migrate(app, db) #connection to database to track changes

class EventStatus(Enum): # Enum for Event Status
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
    image_url = db.Column(db.String(255), nullable=True)  
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

    @property
    def is_active(self):
        return True  

    @property
    def is_authenticated(self):
        return True  

    @property
    def is_anonymous(self):
        return False  

    def get_id(self):
        return str(self.user_id)  

# Initialize database
with app.app_context():
    db.create_all()  # Create the  table
    db.session.commit()

#Flask-Login to load the user from the database 
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) # Retrieve the user by ID from the database

#CHANGE TAG FROM PROPOSED AND CONFIRMED TO PAST WHEN IS PAST DATE
@app.before_request
def update_event_tags():
    db.create_all()
    today = date.today()
    
    # Query for events where the date has passed and the tag is either 'Proposed' or 'Confirmed'
    events_to_update = Event.query.filter(
        Event.date < today, 
        Event.tag.in_([EventStatus.Proposed, EventStatus.Confirmed])
    ).all()
    
    # Loop through and update their tag to 'Past'
    for event in events_to_update:
        event.tag = EventStatus.Past  # Change the tag to 'Past'
    
    # Commit the changes to the database
    db.session.commit()

#EVENT LIST ON INDEX PAGE
@app.route('/')
def index():
    events = Event.query.all()   # Query the database to retrieve all events from the 'Event' table
    return render_template('index.html', events=events)
#Flask web server, making it accessible on all network interfaces

       
#LOGIN TO APP FOR ADMIN USER
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)  
            return redirect(url_for('admin_index')) 
        else:
            flash('Invalid username or password')

    return render_template('login.html')

# Query the database to retrieve all events from the 'Event' table to admin panel
@app.route('/admin')
@login_required
def admin_index():
    events = Event.query.all()  
    return render_template('admin.html', events=events) 

#VOTING SYSTEM
@app.route('/admin/events/<int:event_id>', methods=['GET', 'POST'])
def admin_event_detail(event_id):

    Events = select(Event).filter(Event.eventId == event_id)
    event = db.session.execute(Events).scalar_one_or_none()

    if event is None:
        return redirect(url_for('admin_index'))  # or handle 404


    if request.method == 'POST':
        # Increment the vote count
        event.votes += 1

        # Check if votes have reached 200 and update the tag to 'Confirmed' if not already
        if event.votes >= 200 and event.tag != EventStatus.Confirmed:
            event.tag = EventStatus.Confirmed  # Update the tag to 'Confirmed'

        # Commit the changes to the database
        db.session.commit()

        # Redirect to the confirmation page or wherever you need
        return redirect(url_for('vote_confirmation', event_id=event_id))

    # Render the event details page
    return render_template('event.html', event=event)

#Confirmation page if vote added
@app.route('/events/<int:event_id>/confirmation', methods=['GET'])
def vote_confirmation(event_id):
    
    Events = select(Event).filter(Event.eventId == event_id)
    event = db.session.execute(Events).scalar_one_or_none()

    if event is None:
        return redirect(url_for('admin_index'))  # or handle 404

    return render_template('vote_confirmation.html', event=event)

#EVENT ADD
UPLOAD_FOLDER = os.path.join('./static', './images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/events/add', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        eventName = request.form.get('eventName')
        description = request.form.get('description', '')
        event_date = request.form.get('date')
        location = request.form.get('location')
        tag = request.form.get('tag')
        image = request.files.get('image_url') 
        
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_url = f'images/{filename}'    
         
        else:
            image_url = None  
        
        Events = insert(Event).values(
            eventName=eventName,
            description=description,
            date=date.fromisoformat(event_date),
            location=location,
            tag=tag,  
            image_url=image_url,
            votes=0,
        )

        db.session.execute(Events)
        db.session.commit()
        flash('Event added successfully!', 'success')
        return redirect(url_for('admin_index'))
    return render_template('add_event.html')

#UPDATE EVENT
@app.route('/events/edit/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    Events = select(Event).filter(Event.eventId == event_id)
    event = db.session.execute(Events).scalar_one_or_none()

    if event is None:
        return redirect(url_for('admin_index'))  # or handle 404

    if request.method == 'POST':
        # Update the event with new form data
        event.eventName = request.form.get('eventName', '')
        event.description = request.form.get('description', '')
        event.date = date.fromisoformat(request.form['date'])
        event.location = request.form['location']
        event.tag = EventStatus[request.form['tag']]

         # Validate form fields server-side
        if not event.eventName or not event.date or not event.location:
            return "Please fill out all required fields!", 400

        # Handling image upload
     
        image = request.files['image_url']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            event.image_url = f'images/{filename}' 
        else:
            filename = None  

        # Commit the changes to the database
        db.session.commit()
        flash('Event updated successfully!', 'success')
        return redirect(url_for('admin_index'))

    return render_template('edit_event.html', event=event, EventStatus=EventStatus)


#DELETE EVENT
@app.route('/events/delete/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    # Query for the event using the new SQLAlchemy syntax
    Events = select(Event).filter(Event.eventId == event_id)
    event = db.session.execute(Events).scalar_one_or_none()

    if event is None:
        return redirect(url_for('admin_index'))  # or handle 404

    # Delete the event
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted successfully!', 'success')
    return redirect(url_for('admin_index'))


#LOGOUT
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
if __name__ == '__main__':
    app.run(debug=True)