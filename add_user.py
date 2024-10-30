from app import db, User, app  # Ensure this points to your main app module
from werkzeug.security import generate_password_hash

def add_user(username, password):
    with app.app_context():  # Use app context to access the database
        # Create the users table if it doesn't exist
        db.create_all()  
        
        # Check if the user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print("User already exists.")
            return

        # Create a new user
        new_user = User(username=username)
        new_user.password = generate_password_hash(password) 

        
        db.session.add(new_user)
        db.session.commit()
        print(f"User '{username}' added successfully!")

# adding an admin user
if __name__ == '__main__':
    admin_username = 'admin2'
    admin_password = 'password2024'  
    add_user(admin_username, admin_password)