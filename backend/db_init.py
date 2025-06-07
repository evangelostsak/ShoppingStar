# This script initializes the database by creating all tables.

from app import app, data_manager

with app.app_context():
    data_manager.db.create_all()  # Creates all tables 
    print("Databases initialized successfully.")