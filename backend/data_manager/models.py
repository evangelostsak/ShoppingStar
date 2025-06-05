from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    """User model for storing user information."""

    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(150), unique=True, nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password = Column(String(200), nullable=False)
    profile_picture = Column(String(200), nullable=True, default='default.png')
    
    def set_password(self, password):
        """Set the password for the user, hashing it for security."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the stored hashed password."""
        return check_password_hash(self.password, password)
    
    def __repr__(self):
        """Return a string representation of the User object."""
        return f"User(id = {self.id}, name = {self.username})"
    
class Item(db.Model):
    """Item model for storing item information."""

    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    description = Column(String(500), nullable=True)
    price = Column(Float, nullable=False)
    rating = Column(Float, nullable=True)
    image = Column(String(200), nullable=True, default='default_item.png')
    likes = Column(Integer, default=0)

    
    def __repr__(self):
        """Return a string representation of the Item object."""
        return f"Item(id = {self.id}, name = {self.name}, price = {self.price})"
    

    
""" class Cart(db.Model):

    __tablename__ = 'carts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='cart')
    
    def __repr__(self):
        return f"Cart(id = {self.id}, user_id = {self.user_id})" """