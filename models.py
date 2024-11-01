from datetime import datetime
from sqlalchemy import Column, Integer, String, Date
from .app import db
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#EVENT TABLE
class Event(db.Model):
    __tablename__ = 'events'
    
    eventId = db.Column(db.Integer, primary_key=True)  # Unique identifier for each event
    eventName = db.Column(db.String(100), nullable=False)  # Name of the event
    description = db.Column(db.Text, nullable=True)  # Short description of the event
    date = db.Column(db.Date, nullable=False)  # The date the event will take place
    location = db.Column(db.String(100), nullable=True)  # Location of the event
    tag = db.Column(db.Enum("Proposed", "Confirmed", "Past", name="event_status"), default="Proposed")  # Status of the event
    votes = db.Column(db.Integer, default=0)  # Total votes received by the event
    image = db.Column(db.String(100), nullable=True) #Image 

    def __init__(self, eventName, description, date, location, tag, votes=0, image=None):
        self.eventName = eventName
        self.description = description
        self.date = date
        self.location = location
        self.tag = tag
        self.votes = votes
        self.image = image

    def __repr__(self):
        return f"<Event {self.eventName} - {self.date}>"
#VOTE TABLE
class Vote(db.Model):
    __tablename__ = 'votes'

    voteId = db.Column(db.Integer, primary_key=True)  # Unique identifier for each vote
    eventId = db.Column(db.Integer, db.ForeignKey('events.eventId'), nullable=False)  # Foreign key to the Event table
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # Timestamp for when the vote was cast

    # Define relationship to Event
    event = db.relationship('Event', backref=db.backref('votes', lazy=True))

    def __repr__(self):
        return f"<Vote {self.voteId} - Event {self.eventId}>"
    

