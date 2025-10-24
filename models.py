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
    projects = db.Column(db.Text)
    certifications = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserProfile {self.name}>'

class GeneratedContent(db.Model):
    __tablename__ = 'generated_content'
    id = db.Column(db.Integer, primary_key=True)
    content_type = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    job_posting_id = db.Column(db.Integer, db.ForeignKey('job_posting.id'))
    user_profile_id = db.Column(db.Integer, db.ForeignKey('user_profile.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    job_posting = db.relationship('JobPosting', backref='generated_content')
    user_profile = db.relationship('UserProfile', backref='generated_content')
    
    def __repr__(self):
        return f'<GeneratedContent {self.content_type}>'

class JobApplication(db.Model):
    __tablename__ = 'job_application'
    id = db.Column(db.Integer, primary_key=True)
    job_posting_id = db.Column(db.Integer, db.ForeignKey('job_posting.id'), nullable=False)
    user_profile_id = db.Column(db.Integer, db.ForeignKey('user_profile.id'), nullable=False)
    
    # Application details
    status = db.Column(db.String(50), default='Applied')  # Applied, Phone Screen, Interview, Offer, Rejected, Withdrawn
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    job_url = db.Column(db.String(500))
    salary_range = db.Column(db.String(100))
    location = db.Column(db.String(200))
    job_type = db.Column(db.String(50))  # Full-time, Part-time, Contract, Remote
    
    # Tracking information
    notes = db.Column(db.Text)
    follow_up_date = db.Column(db.DateTime)
    contact_person = db.Column(db.String(100))
    contact_email = db.Column(db.String(120))
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    job_posting = db.relationship('JobPosting', backref='applications')
    user_profile = db.relationship('UserProfile', backref='applications')
    
    def __repr__(self):
        return f'<JobApplication {self.job_posting.title} - {self.status}>'
    
    @property
    def status_color(self):
        """Return Bootstrap color class based on status"""
        colors = {
            'Applied': 'primary',
            'Phone Screen': 'info',
            'Interview': 'warning',
            'Technical Round': 'warning',
            'Final Round': 'warning',
            'Offer': 'success',
            'Accepted': 'success',
            'Rejected': 'danger',
            'Withdrawn': 'secondary'
        }
        return colors.get(self.status, 'secondary')
