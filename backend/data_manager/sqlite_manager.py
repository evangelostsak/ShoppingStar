from data_manager.interface import DataManagerInterface
from data_manager.models import User, Item, db
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
    

    def update_user(self, user_id, username, password, profile_picture):
        """Update existing User's data identified by ID."""

        try:
            update_user = self.get_user(user_id)
            if not update_user:
                return "User doesn't exist."
            update_user.username = username
            if password:
                update_user.set_password(password)
            if profile_picture:
                update_user.profile_picture = profile_picture
            self.db.session.commit()
            return f"User {username} updated successfully!"
        
        except SQLAlchemyError as e:
            print(f"Error updating user {user_id}: {e}")
            self.db.session.rollback()
            return None
        

    def delete_user(self, user_id):
        """Delete User by ID."""
        try:
            delete_user = self.get_user(user_id)
            if not delete_user:
                return "User doesn't exist."
            self.db.session.delete(delete_user)
            self.db.session.commit()
            return f"User {delete_user.username} deleted successfully!"
        except SQLAlchemyError as e:
            print(f"Error deleting user {user_id}: {e}")
            self.db.session.rollback()
            return None
   

    def get_all_items(self):
        """Retrieve all items from the database."""
        try:
            return Item.query.all()
        except SQLAlchemyError as e:
            print(f"Error retrieving items: {e}")
            return []
        

    def get_item(self, item_id):
        """Get Item by ID."""
        if not item_id:
            return None
        try:
            return Item.query.get(item_id)
        
        except SQLAlchemyError as e:
            print(f"Error retrieving item with ID {item_id}: {e}")
            return None
        

    def add_item(self, name, description, price, rating=None, image=None):
        """Add a new item to the database."""
        
        try:
            new_item = Item(name=name, description=description, price=price, rating=rating, image=image)

            if not new_item.name or not new_item.price:
                return "Item name and price are required."
            existing_item = self.db.session.query(Item).filter_by(name=name, description=description).first()
            if existing_item:
                return f"Item {name} already exists!"
            self.db.session.add(new_item)
            self.db.session.commit()
            return f"Item {name} added successfully!"
        
        except SQLAlchemyError as e:
            print(f"Error adding item {name}: {e}")
            self.db.session.rollback()
            return None
        

    def update_item(self, item_id, name, description, price, rating=None, image=None):
        """Update existing Item's data identified by ID."""
        
        try:
            update_item = self.get_item(item_id)
            if not update_item:
                return "Item doesn't exist."
            if name:
                update_item.name = name
            if description:
                update_item.description = description
            if price:
                update_item.price = price
            if rating:
                update_item.rating = rating
            if image:
                update_item.image = image

            self.db.session.commit()
            return f"Item {name} updated successfully!"
        
        except SQLAlchemyError as e:
            print(f"Error updating item {item_id}: {e}")
            self.db.session.rollback()
            return None
        

    def delete_item(self, item_id):
        """Delete Item by ID."""
        try:
            delete_item = self.get_item(item_id)
            if not delete_item:
                return "Item doesn't exist."
            self.db.session.delete(delete_item)
            self.db.session.commit()
            return f"Item {delete_item.name} deleted successfully!"
        
        except SQLAlchemyError as e:
            print(f"Error deleting item {item_id}: {e}")
            self.db.session.rollback()
            return None
        

    def get_item_by_name(self, name):
        """Get an item by its name."""
        try:
            item = self.db.session.query(Item).filter_by(name=name).first()
            return item
        
        except SQLAlchemyError as e:
            print(f"Error: {e}")
            return None
        

    def like_item(self, item_id):
        """Like an item."""
        try:
            item = self.get_item(item_id)
            if not item:
                return "Item doesn't exist."
            item.likes += 1
            self.db.session.commit()
            return f"Item {item.name} liked successfully!"
        
        except SQLAlchemyError as e:
            print(f"Error liking item {item_id}: {e}")
            self.db.session.rollback()
            return None