from abc import ABC, abstractmethod

class DataManagerInterface(ABC):

    @abstractmethod
    def get_all_users(self):
        """Retrieve data based on a query."""
        pass

    @abstractmethod
    def get_user(self, user_id):
        """Get User by ID."""
        pass

    @abstractmethod
    def register(self, username, password, email):
        """Save data to the database."""
        pass

    @abstractmethod
    def update_user(self, user_id):
        """Update existing User's data identified by ID."""
        pass

    @abstractmethod
    def delete_user(self, user_id):
        """Delete User identified by ID."""
        pass

    @abstractmethod
    def get_all_items(self):
        """Retrieve all items."""
        pass

    @abstractmethod
    def get_item(self, item_id):
        """Get Item by ID."""
        pass
    
    @abstractmethod
    def add_item(self, name, description, price, rating, image):
        """Add a new item."""
        pass

    @abstractmethod
    def update_item(self, item_id, name, description, price, rating, image):
        """Update existing Item's data identified by ID."""
        pass

    @abstractmethod
    def delete_item(self, item_id):
        """Delete Item identified by ID."""
        pass

    @abstractmethod
    def like_item(self, item_id):
        """Like an item."""
        pass
