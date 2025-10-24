from flask import render_template, request, redirect, url_for, flash, session, make_response
from app import app, db
from models import JobPosting, UserProfile, GeneratedContent, JobApplication
from gemini_service import JobAssistantService
from datetime import datetime
from werkzeug.utils import secure_filename
import logging
import os
import json
import io

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        profile = UserProfile.query.first()
        if not profile:
            profile = UserProfile(
                name=request.form.get('name'),
                email=request.form.get('email'),
                phone=request.form.get('phone'),
                summary=request.form.get('summary'),
                experience=request.form.get('experience'),
                education=request.form.get('education'),
                skills=request.form.get('skills'),
                projects=request.form.get('projects'),
                certifications=request.form.get('certifications')
            )
            db.session.add(profile)
        else:
            profile.name = request.form.get('name')
            profile.email = request.form.get('email')
            profile.phone = request.form.get('phone')
            profile.summary = request.form.get('summary')
            profile.experience = request.form.get('experience')
            profile.education = request.form.get('education')
            profile.skills = request.form.get('skills')
            profile.projects = request.form.get('projects')
            profile.certifications = request.form.get('certifications')
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    profile = UserProfile.query.first()
    return render_template('profile.html', profile=profile)

@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    if 'resume_file' not in request.files:
        flash('No file uploaded', 'error')
        return redirect(url_for('profile'))
    
    file = request.files['resume_file']
    
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('profile'))
    
    if file and allowed_file(file.filename):
        try:
            # Extract text from file
            text_content = extract_text_from_file(file)
            
            if not text_content:
                flash('Could not extract text from file', 'error')
                return redirect(url_for('profile'))
            
            # Use AI to parse resume
            parsed_data = JobAssistantService.parse_resume(text_content)
            
            # Update or create profile
            profile = UserProfile.query.first()
            if not profile:
                profile = UserProfile(
                    name=parsed_data.get('name', ''),
                    email=parsed_data.get('email', ''),
                    phone=parsed_data.get('phone', ''),
                    summary=parsed_data.get('summary', ''),
                    experience=parsed_data.get('experience', ''),
                    education=parsed_data.get('education', ''),
                    skills=parsed_data.get('skills', ''),
                    projects=parsed_data.get('projects', ''),
                    certifications=parsed_data.get('certifications', '')
                )
                db.session.add(profile)
            else:
                update_profile_from_parsed_data(profile, parsed_data)
            
            db.session.commit()
            flash('Resume parsed and profile updated successfully!', 'success')
            
        except Exception as e:
            logging.error(f"Error processing resume: {e}")
            flash(f'Error processing resume: {str(e)}', 'error')
    else:
        flash('Invalid file type. Please upload PDF, DOC, DOCX, or TXT', 'error')
    
    return redirect(url_for('profile'))

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_file(file):
    """Extract text from uploaded file"""
    filename = file.filename.lower()
    text_content = ""
    
    try:
        if filename.endswith('.txt'):
            text_content = file.read().decode('utf-8')
        elif filename.endswith('.pdf'):
            # You'll need to install PyPDF2: pip install PyPDF2
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text_content += page.extract_text()
        elif filename.endswith(('.doc', '.docx')):
            # You'll need to install python-docx: pip install python-docx
            import docx
            doc = docx.Document(file)
            text_content = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
    except Exception as e:
        logging.error(f"Error extracting text from file: {e}")
        return ""
    
    return text_content

def update_profile_from_parsed_data(profile, parsed_data):
    """Update profile fields from AI-parsed resume data"""
    try:
        profile.name = parsed_data.get('name', profile.name)
        profile.email = parsed_data.get('email', profile.email)
        profile.phone = parsed_data.get('phone', profile.phone)
        profile.summary = parsed_data.get('summary', profile.summary)
        
        # Handle experience - convert to string if it's a dict/list
        experience = parsed_data.get('experience', profile.experience)
        if isinstance(experience, (dict, list)):
            profile.experience = json.dumps(experience, indent=2)
        else:
            profile.experience = experience
        
        # Handle education - convert to string if it's a dict/list
        education = parsed_data.get('education', profile.education)
        if isinstance(education, (dict, list)):
            profile.education = json.dumps(education, indent=2)
        else:
            profile.education = education
        
        # Handle skills - convert to string if it's a dict/list
        skills = parsed_data.get('skills', profile.skills)
        if isinstance(skills, (dict, list)):
            profile.skills = json.dumps(skills, indent=2)
        else:
            profile.skills = skills
        
        # Handle projects - convert to string if it's a dict/list
        projects = parsed_data.get('projects', profile.projects)
        if isinstance(projects, (dict, list)):
            profile.projects = json.dumps(projects, indent=2)
        else:
            profile.projects = projects
        
        # Handle certifications - convert to string if it's a dict/list
        certifications = parsed_data.get('certifications', profile.certifications)
        if isinstance(certifications, (dict, list)):
            profile.certifications = json.dumps(certifications, indent=2)
        else:
            profile.certifications = certifications
    except Exception as e:
        logging.error(f"Error updating profile: {e}")
        raise

@app.route('/analyze_job', methods=['GET', 'POST'])
def analyze_job():
    if request.method == 'POST':
        job_title = request.form.get('job_title', '')
        company_name = request.form.get('company_name', '')
        job_description = request.form.get('job_description', '')
        
        if not job_description.strip():
            flash('Please provide a job description.', 'error')
            return render_template('analyze_job.html')
        
        # Save job posting
        job_posting = JobPosting()
        job_posting.title = job_title
        job_posting.company = company_name
        job_posting.description = job_description
        db.session.add(job_posting)
        db.session.commit()
        
        # Analyze with Gemini
        try:
            analysis = JobAssistantService.analyze_job_posting(job_description)
            
            # Save analysis
            content = GeneratedContent()
            content.content_type = 'job_analysis'
            content.content = analysis
            content.job_posting_id = job_posting.id
            db.session.add(content)
            db.session.commit()
            
            return render_template('results.html', 
                                 content=analysis, 
                                 content_type='Job Analysis',
                                 job_id=job_posting.id)
            
        except Exception as e:
            flash(f'Error analyzing job posting: {str(e)}', 'error')
            return render_template('analyze_job.html')
    
    return render_template('analyze_job.html')

@app.route('/customize_resume')
def customize_resume():
    job_id = request.args.get('job_id')
    job_posting = None
    if job_id:
        job_posting = JobPosting.query.get(job_id)
    
    jobs = JobPosting.query.order_by(JobPosting.created_at.desc()).limit(10).all()
    profile = UserProfile.query.first()
    
    return render_template('customize_resume.html', 
                         jobs=jobs, 
                         selected_job=job_posting,
                         profile=profile)

@app.route('/process_resume_customization', methods=['POST'])
def process_resume_customization():
    job_id = request.form.get('job_id')
    
    if not job_id:
        flash('Please select a job posting.', 'error')
        return redirect(url_for('customize_resume'))
    
    job_posting = JobPosting.query.get(job_id)
    profile = UserProfile.query.first()
    
    if not job_posting:
        flash('Job posting not found.', 'error')
        return redirect(url_for('customize_resume'))
    
    if not profile:
        flash('Please create your profile first.', 'error')
        return redirect(url_for('profile'))
    
    try:
        customization = JobAssistantService.customize_resume(
            job_posting.description, 
            profile
        )
        
        # Save customization
        content = GeneratedContent()
        content.content_type = 'resume_customization'
        content.content = customization
        content.job_posting_id = job_posting.id
        content.user_profile_id = profile.id
        db.session.add(content)
        db.session.commit()
        
        return render_template('results.html', 
                             content=customization, 
                             content_type='Resume Customization Suggestions',
                             job_id=job_posting.id)
        
    except Exception as e:
        flash(f'Error customizing resume: {str(e)}', 'error')
        return redirect(url_for('customize_resume'))

@app.route('/generate_cover_letter')
def generate_cover_letter():
    job_id = request.args.get('job_id')
    job_posting = None
    if job_id:
        job_posting = JobPosting.query.get(job_id)
    
    jobs = JobPosting.query.order_by(JobPosting.created_at.desc()).limit(10).all()
    profile = UserProfile.query.first()
    
    return render_template('generate_cover_letter.html', 
                         jobs=jobs, 
                         selected_job=job_posting,
                         profile=profile)

@app.route('/process_cover_letter', methods=['POST'])
def process_cover_letter():
    job_id = request.form.get('job_id')
    
    if not job_id:
        flash('Please select a job posting.', 'error')
        return redirect(url_for('generate_cover_letter'))
    
    job_posting = JobPosting.query.get(job_id)
    profile = UserProfile.query.first()
    
    if not job_posting:
        flash('Job posting not found.', 'error')
        return redirect(url_for('generate_cover_letter'))
    
    if not profile:
        flash('Please create your profile first.', 'error')
        return redirect(url_for('profile'))
    
    try:
        cover_letter = JobAssistantService.generate_cover_letter(
            job_posting.description,
            profile,
            job_posting.company,
            job_posting.title
        )
        
        # Save cover letter
        content = GeneratedContent()
        content.content_type = 'cover_letter'
        content.content = cover_letter
        content.job_posting_id = job_posting.id
        content.user_profile_id = profile.id
        db.session.add(content)
        db.session.commit()
        
        return render_template('results.html', 
                             content=cover_letter, 
                             content_type='Cover Letter',
                             job_id=job_posting.id,
                             show_download=True)
        
    except Exception as e:
        flash(f'Error generating cover letter: {str(e)}', 'error')
        return redirect(url_for('generate_cover_letter'))

@app.route('/interview_prep')
def interview_prep():
    job_id = request.args.get('job_id')
    job_posting = None
    if job_id:
        job_posting = JobPosting.query.get(job_id)
    
    jobs = JobPosting.query.order_by(JobPosting.created_at.desc()).limit(10).all()
    
    return render_template('interview_prep.html', 
                         jobs=jobs, 
                         selected_job=job_posting)

@app.route('/process_interview_prep', methods=['POST'])
def process_interview_prep():
    job_id = request.form.get('job_id')
    
    if not job_id:
        flash('Please select a job posting.', 'error')
        return redirect(url_for('interview_prep'))
    
    job_posting = JobPosting.query.get(job_id)
    profile = UserProfile.query.first()  # Get the user profile
    
    if not job_posting:
        flash('Job posting not found.', 'error')
        return redirect(url_for('interview_prep'))
    
    if not profile:
        flash('Please create your profile first.', 'error')
        return redirect(url_for('profile'))
    
    try:
        questions = JobAssistantService.generate_interview_questions(
            job_posting.description,
            profile  # Pass the profile object, not job_posting.title
        )
        
        # Save interview questions
        content = GeneratedContent()
        content.content_type = 'interview_questions'
        content.content = questions
        content.job_posting_id = job_posting.id
        content.user_profile_id = profile.id  # Also link to user profile
        db.session.add(content)
        db.session.commit()
        
        return render_template('results.html', 
                             content=questions, 
                             content_type='Interview Questions',
                             job_id=job_posting.id)
        
    except Exception as e:
        flash(f'Error generating interview questions: {str(e)}', 'error')
        return redirect(url_for('interview_prep'))

@app.route('/download/<int:content_id>')
def download_content(content_id):
    content = GeneratedContent.query.get_or_404(content_id)
    
    # Create a text file with the content
    output = io.StringIO()
    output.write(content.content)
    
    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/plain'
    response.headers['Content-Disposition'] = f'attachment; filename={content.content_type}_{content.id}.txt'
    
    return response

@app.route('/history')
def history():
    recent_content = GeneratedContent.query.order_by(GeneratedContent.created_at.desc()).limit(20).all()
    return render_template('history.html', content_list=recent_content)

@app.route('/applications')
def applications():
    """View all job applications"""
    profile = UserProfile.query.first()
    
    if not profile:
        flash('Please create your profile first.', 'error')
        return redirect(url_for('profile'))
    
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    sort_by = request.args.get('sort', 'date_desc')
    
    # Base query
    query = JobApplication.query.filter_by(user_profile_id=profile.id)
    
    # Apply status filter
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    # Apply sorting
    if sort_by == 'date_desc':
        query = query.order_by(JobApplication.application_date.desc())
    elif sort_by == 'date_asc':
        query = query.order_by(JobApplication.application_date.asc())
    elif sort_by == 'company':
        query = query.join(JobPosting).order_by(JobPosting.company)
    
    applications = query.all()
    
    # Get statistics
    total_apps = JobApplication.query.filter_by(user_profile_id=profile.id).count()
    active_apps = JobApplication.query.filter_by(user_profile_id=profile.id).filter(
        JobApplication.status.in_(['Applied', 'Phone Screen', 'Interview', 'Technical Round', 'Final Round'])
    ).count()
    offers = JobApplication.query.filter_by(user_profile_id=profile.id, status='Offer').count()
    
    return render_template('applications.html', 
                         applications=applications,
                         total_apps=total_apps,
                         active_apps=active_apps,
                         offers=offers,
                         status_filter=status_filter,
                         sort_by=sort_by)

@app.route('/applications/add', methods=['GET', 'POST'])
def add_application():
    """Add a new job application"""
    profile = UserProfile.query.first()
    
    if not profile:
        flash('Please create your profile first.', 'error')
        return redirect(url_for('profile'))
    
    if request.method == 'POST':
        try:
            # Check if job posting exists or create new one
            job_id = request.form.get('job_id')
            
            if job_id:
                job_posting = JobPosting.query.get(job_id)
            else:
                # Create new job posting
                job_posting = JobPosting(
                    title=request.form.get('job_title'),
                    company=request.form.get('company'),
                    description=request.form.get('job_description', '')
                )
                db.session.add(job_posting)
                db.session.flush()  # Get the ID
            
            # Create application
            application = JobApplication(
                job_posting_id=job_posting.id,
                user_profile_id=profile.id,
                status=request.form.get('status', 'Applied'),
                job_url=request.form.get('job_url'),
                salary_range=request.form.get('salary_range'),
                location=request.form.get('location'),
                job_type=request.form.get('job_type'),
                notes=request.form.get('notes'),
                contact_person=request.form.get('contact_person'),
                contact_email=request.form.get('contact_email')
            )
            
            # Handle application date
            app_date = request.form.get('application_date')
            if app_date:
                application.application_date = datetime.strptime(app_date, '%Y-%m-%d')
            
            # Handle follow-up date
            follow_up = request.form.get('follow_up_date')
            if follow_up:
                application.follow_up_date = datetime.strptime(follow_up, '%Y-%m-%d')
            
            db.session.add(application)
            db.session.commit()
            
            flash('Application added successfully!', 'success')
            return redirect(url_for('applications'))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error adding application: {e}")
            flash(f'Error adding application: {str(e)}', 'error')
    
    # Get existing job postings for dropdown
    jobs = JobPosting.query.order_by(JobPosting.created_at.desc()).limit(20).all()
    
    return render_template('add_application.html', jobs=jobs, profile=profile)

@app.route('/applications/<int:app_id>')
def view_application(app_id):
    """View single application details"""
    application = JobApplication.query.get_or_404(app_id)
    
    # Get related content
    related_content = GeneratedContent.query.filter_by(
        job_posting_id=application.job_posting_id
    ).order_by(GeneratedContent.created_at.desc()).all()
    
    return render_template('view_application.html', 
                         application=application,
                         related_content=related_content)

@app.route('/applications/<int:app_id>/edit', methods=['GET', 'POST'])
def edit_application(app_id):
    """Edit an existing application"""
    application = JobApplication.query.get_or_404(app_id)
    
    if request.method == 'POST':
        try:
            application.status = request.form.get('status')
            application.job_url = request.form.get('job_url')
            application.salary_range = request.form.get('salary_range')
            application.location = request.form.get('location')
            application.job_type = request.form.get('job_type')
            application.notes = request.form.get('notes')
            application.contact_person = request.form.get('contact_person')
            application.contact_email = request.form.get('contact_email')
            
            # Handle application date
            app_date = request.form.get('application_date')
            if app_date:
                application.application_date = datetime.strptime(app_date, '%Y-%m-%d')
            
            # Handle follow-up date
            follow_up = request.form.get('follow_up_date')
            if follow_up:
                application.follow_up_date = datetime.strptime(follow_up, '%Y-%m-%d')
            else:
                application.follow_up_date = None
            
            # Update job posting details
            application.job_posting.title = request.form.get('job_title')
            application.job_posting.company = request.form.get('company')
            
            db.session.commit()
            
            flash('Application updated successfully!', 'success')
            return redirect(url_for('view_application', app_id=app_id))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating application: {e}")
            flash(f'Error updating application: {str(e)}', 'error')
    
    return render_template('edit_application.html', application=application)

@app.route('/applications/<int:app_id>/delete', methods=['POST'])
def delete_application(app_id):
    """Delete an application"""
    try:
        application = JobApplication.query.get_or_404(app_id)
        db.session.delete(application)
        db.session.commit()
        
        flash('Application deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting application: {e}")
        flash(f'Error deleting application: {str(e)}', 'error')
    
    return redirect(url_for('applications'))

@app.route('/applications/<int:app_id>/quick-update', methods=['POST'])
def quick_update_status(app_id):
    """Quick update application status via AJAX"""
    try:
        application = JobApplication.query.get_or_404(app_id)
        new_status = request.form.get('status')
        
        if new_status:
            application.status = new_status
            db.session.commit()
            
            return {'success': True, 'message': 'Status updated'}
        else:
            return {'success': False, 'message': 'Invalid status'}, 400
            
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating status: {e}")
        return {'success': False, 'message': str(e)}, 500
