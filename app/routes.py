from flask import render_template, redirect, url_for, request, flash
from .models import Event, Vote
from . import db

# Homepage route
@app.route('/')
def index():
    events = Event.query.all()
    return render_template('index.html', events=events)

# Admin page
@app.route('/admin')
def admin():
    events = Event.query.all()
    return render_template('admin.html', events=events)

# Route to handle voting on an event
@app.route('/event/<int:event_id>/vote', methods=['POST'])
def vote(event_id):
    form = VoteForm()
    if form.validate_on_submit():
        # Assuming you have a way to get the current user's ID
        user_id = 42  # Replace this with actual logic to get the logged-in user ID
        
        # Add the vote to the database
        new_vote = Vote(eventId=event_id, userId=user_id)
        db.session.add(new_vote)
        db.session.commit()

        flash("Thank you for voting!")
        return redirect(url_for('vote_confirmation'))

    # If form submission fails, redirect back to the event page
    event = Event.query.get_or_404(event_id)
    return render_template('event.html', event=event, form=form)

# Vote confirmation screen
@app.route('/vote_confirmation')
def vote_confirmation():
    return render_template('vote_confirmation.html')