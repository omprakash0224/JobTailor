from flask import render_template, request, redirect, url_for, flash, session, make_response
from app import app
from models import JobPosting, UserProfile, GeneratedContent, db
from gemini_service import JobAssistantService
import io
from datetime import datetime

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        # Get or create user profile
        profile = UserProfile.query.first()
        if not profile:
            profile = UserProfile()
        
        profile.name = request.form.get('name', '')
        profile.email = request.form.get('email', '')
        profile.phone = request.form.get('phone', '')
        profile.summary = request.form.get('summary', '')
        profile.experience = request.form.get('experience', '')
        profile.education = request.form.get('education', '')
        profile.skills = request.form.get('skills', '')
        profile.updated_at = datetime.utcnow()
        
        db.session.add(profile)
        db.session.commit()
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('index'))
    
    # GET request - show profile form
    profile = UserProfile.query.first()
    return render_template('index.html', profile=profile, show_profile=True)

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
    
    if not job_posting:
        flash('Job posting not found.', 'error')
        return redirect(url_for('interview_prep'))
    
    try:
        questions = JobAssistantService.generate_interview_questions(
            job_posting.description,
            job_posting.title
        )
        
        # Save interview questions
        content = GeneratedContent()
        content.content_type = 'interview_questions'
        content.content = questions
        content.job_posting_id = job_posting.id
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
