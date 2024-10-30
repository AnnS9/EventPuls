from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from enum import Enum

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


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

# Initialize database
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    events = Event.query.all()  # Fetch all events from the database
    return render_template('index.html', events=events)

@app.route('/admin')
def admin_index():
    events = Event.query.all()  # Fetch all events
    return render_template('admin.html', events=events) 


@app.route('/admin/events/<int:event_id>', methods=['GET', 'POST'])
def admin_event_detail(event_id):
    event = Event.query.get_or_404(event_id)  # Fetch the event by ID

    if request.method == 'POST':
        # Increment vote count
        vote = Vote.query.filter_by(eventId=event_id).first()
        if vote:
            vote.voteCount += 1
        else:
            new_vote = Vote(eventId=event_id, voteCount=1)
            db.session.add(new_vote)
        db.session.commit()

        return redirect(url_for('admin_event_detail', event_id=event_id))

    return render_template('event.html', event=event)

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

@app.route('/events/edit/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)

    if request.method == 'POST':
        event.eventId = request.form['eventId']
        event.eventName = request.form['eventName']
        event.description = request.form.get('description', '')
        event.date = date.fromisoformat(request.form['date'])
        event.location = request.form['location']
        event.tag = EventStatus[request.form['tag']] 
        
        db.session.commit()
        return redirect(url_for('admin_index'))

    return render_template('add_event.html', event=event)

@app.route('/events/delete/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return redirect(url_for('admin_index'))

if __name__ == '__main__':
    app.run(debug=True)