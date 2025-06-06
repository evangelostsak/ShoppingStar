from interface import DataManagerInterface
from models import User, Item, db
from sqlalchemy.exc import SQLAlchemyError

class SQLiteDataManager(DataManagerInterface):
    """SQLite database manager using sqlalchemy, inherits DataManagerInterface"""

    def __init__(self, app):
        """Initialize database with flask"""
        db.init_app(app)  # Initialize SQLAlchemy with Flask app
        self.db = db

    def get_all_users(self):
        """Retrieve all users from the database."""
        try:
            return User.query.all()
        except SQLAlchemyError as e:
            print(f"Error retrieving users: {e}")
            return []
    
    def get_user(self, user_id):
        """Get User by ID."""
        if not user_id:
            return None
        try:
            return User.query.get(user_id)
        except SQLAlchemyError as e:
            print(f"Error retrieving user with ID {user_id}: {e}")
            return None
        

    def get_user_by_username(self, username):
        """Get a user by their username"""

        try:
            user = self.db.session.query(User).filter_by(username=username).first()
            return user
        except SQLAlchemyError as e:
            print(f"Error: {e}")
            return None
        

    def register(self, username, password):
        """Register a new user."""
        try:
            existing_user = self.db.session.query(User).filter_by(username=username).first()
            if existing_user:
                return f"User {username} already exists!"
            new_user = User(username=username)
            new_user.set_password(password)
            self.db.session.add(new_user)
            self.db.session.commit()

            return f"Account for {username} registered successfully!"

        except SQLAlchemyError as e:
            print(f"Error registering user {username}: {e}")
            self.db.session.rollback()
            return None
        
    def authenticate_user(self, username, password):
        """Authenticate user with username and password"""

        try:
            user = self.get_user_by_username(username)
            if user and user.check_password(password):
                return user
        except SQLAlchemyError as e:
            print(f"Error: {e}")
        return None
    

    