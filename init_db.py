from app import app, db
from models import JobPosting, UserProfile, GeneratedContent

with app.app_context():
    # Drop all tables and recreate (WARNING: This will delete all data)
    db.drop_all()
    db.create_all()
    print("Database tables created successfully!")