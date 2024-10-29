from flask_sqlalchemy import SQLAlchemy
from models import Event, Vote
from datetime import datetime

db = SQLAlchemy()

def init_db(app):
    """Initialize the database with the app."""
    db.init_app(app)
    with app.app_context():
        db.create_all()  # Create tables based on the models

def add_event(event_name, description, date, location):
    """Add a new event to the database."""
    new_event = Event(
        eventName=event_name,
        description=description,
        date=date,
        location=location,
        tag="Proposed"  # Default status
    )
    db.session.add(new_event)
    db.session.commit()
    return new_event

def get_events():
    """Retrieve all events from the database."""
    return Event.query.all()

def get_event_by_id(event_id):
    """Retrieve an event by its ID."""
    return Event.query.get(event_id)

def vote_on_event(event_id, user_id):
    """Cast a vote for an event."""
    new_vote = Vote(
        eventId=event_id,
        userId=user_id,
        timestamp=datetime.utcnow()  # Current time for the vote
    )
    db.session.add(new_vote)
    
    # Increment the vote count for the event
    event = Event.query.get(event_id)
    if event:
        event.votes += 1
    
    db.session.commit()
    return new_vote

def get_votes_for_event(event_id):
    """Retrieve all votes for a specific event."""
    return Vote.query.filter_by(eventId=event_id).all()

def get_votes_by_user(user_id):
    """Retrieve all votes cast by a specific user."""
    return Vote.query.filter_by(userId=user_id).all()

def delete_event(event_id):
    """Delete an event from the database."""
    event = Event.query.get(event_id)
    if event:
        db.session.delete(event)
        db.session.commit()
        return True
    return False

def delete_vote(vote_id):
    """Delete a vote from the database."""
    vote = Vote.query.get(vote_id)
    if vote:
        db.session.delete(vote)
        db.session.commit()
        return True
    return False
