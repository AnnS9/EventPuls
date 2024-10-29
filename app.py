from flask import Flask
from db import init_db, add_event, vote_on_event, get_events
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'  # SQLite database file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable track modifications to save memory

# Initialize the database
init_db(app)

@app.route('/')
def index():
    events = get_events()
    return f"Events: {', '.join([event.eventName for event in events])}"

@app.route('/add_event', methods=['POST'])
def add_event_route():
    # Example event data
    event_name = "Sample Event"
    description = "This is a sample event."
    date = datetime(2024, 12, 25)  # Sample date
    location = "Sample Location"
    
    new_event = add_event(event_name, description, date, location)
    return f"Added event: {new_event.eventName}"

@app.route('/vote/<int:event_id>/<int:user_id>', methods=['POST'])
def vote_route(event_id, user_id):
    new_vote = vote_on_event(event_id, user_id)
    return f"Vote recorded for event ID {event_id} by user ID {user_id}"

if __name__ == '__main__':
    app.run(debug=True)