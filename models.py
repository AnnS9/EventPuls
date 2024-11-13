from datetime import datetime
from sqlalchemy import Column, Integer, String, Date
from .app import db
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#EVENT TABLE
class Event(db.Model):
    __tablename__ = 'events'
    
    eventId = db.Column(db.Integer, primary_key=True)  
    eventName = db.Column(db.String(100), nullable=False)  
    description = db.Column(db.Text, nullable=True) 
    date = db.Column(db.Date, nullable=False)  
    location = db.Column(db.String(100), nullable=True) 
    tag = db.Column(db.Enum("Proposed", "Confirmed", "Past", name="event_status"), default="Proposed")  
    image_url = db.Column(db.String(255), nullable=True)  
    votes = db.Column(db.Integer, default=0)  
    

    def __init__(self, eventName, description, date, location, tag, votes=0, image=None):
        self.eventName = eventName
        self.description = description
        self.date = date
        self.location = location
        self.tag = tag
        self.votes = votes
        

    def __repr__(self):
        return f"<Event {self.eventName} - {self.date}>"
#VOTE TABLE
class Vote(db.Model):
    __tablename__ = 'votes'

    voteId = db.Column(db.Integer, primary_key=True)  
    eventId = db.Column(db.Integer, db.ForeignKey('events.eventId'), nullable=False)  
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  

    # Define relationship to Event
    event = db.relationship('Event', backref=db.backref('votes', lazy=True))

    def __repr__(self):
        return f"<Vote {self.voteId} - Event {self.eventId}>"
    

