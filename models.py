from datetime import datetime
from app import db

class JobPosting(db.Model):
    __tablename__ = 'job_posting'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<JobPosting {self.title} at {self.company}>'

class UserProfile(db.Model):
    __tablename__ = 'user_profile'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    summary = db.Column(db.Text)
    experience = db.Column(db.Text)
    education = db.Column(db.Text)
    skills = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserProfile {self.name}>'

class GeneratedContent(db.Model):
    __tablename__ = 'generated_content'
    id = db.Column(db.Integer, primary_key=True)
    content_type = db.Column(db.String(50), nullable=False)  # 'resume', 'cover_letter', 'interview_questions'
    content = db.Column(db.Text, nullable=False)
    job_posting_id = db.Column(db.Integer, db.ForeignKey('job_posting.id'))
    user_profile_id = db.Column(db.Integer, db.ForeignKey('user_profile.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    job_posting = db.relationship('JobPosting', backref='generated_content')
    user_profile = db.relationship('UserProfile', backref='generated_content')
    
    def __repr__(self):
        return f'<GeneratedContent {self.content_type}>'
