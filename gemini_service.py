import os
import logging
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class JobAssistantService:
    
    @staticmethod
    def analyze_job_posting(job_description):
        """Analyze job posting and extract key requirements and skills"""
        try:
            prompt = f"""
            Analyze the following job posting and provide a detailed breakdown:
            
            Job Description:
            {job_description}
            
            Please provide:
            1. Key required skills and qualifications
            2. Nice-to-have skills
            3. Main responsibilities
            4. Company culture indicators
            5. Level of experience required
            6. Key technologies or tools mentioned
            
            Format your response in clear sections with bullet points.
            """
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            return response.text if response.text else "Analysis failed"
            
        except Exception as e:
            logging.error(f"Error analyzing job posting: {e}")
            return f"Error analyzing job posting: {str(e)}"
    
    @staticmethod
    def customize_resume(job_description, user_profile):
        """Generate customized resume suggestions based on job requirements"""
        try:
            prompt = f"""
            Based on the job posting and user profile below, provide specific suggestions to customize the resume:
            
            Job Posting:
            {job_description}
            
            User Profile:
            Name: {user_profile.name}
            Summary: {user_profile.summary}
            Experience: {user_profile.experience}
            Education: {user_profile.education}
            Skills: {user_profile.skills}
            
            Please provide:
            1. Suggested changes to the professional summary
            2. Skills to highlight or add
            3. Experience points to emphasize
            4. Keywords to include for ATS optimization
            5. Sections to reorganize or prioritize
            6. Any gaps to address or downplay
            
            Make the suggestions specific and actionable.
            """
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            return response.text if response.text else "Resume customization failed"
            
        except Exception as e:
            logging.error(f"Error customizing resume: {e}")
            return f"Error customizing resume: {str(e)}"
    
    @staticmethod
    def generate_cover_letter(job_description, user_profile, company_name, position_title):
        """Generate a personalized cover letter"""
        try:
            prompt = f"""
            Write a professional cover letter for the following position:
            
            Company: {company_name}
            Position: {position_title}
            
            Job Description:
            {job_description}
            
            Applicant Information:
            Name: {user_profile.name}
            Email: {user_profile.email}
            Phone: {user_profile.phone}
            Summary: {user_profile.summary}
            Experience: {user_profile.experience}
            Education: {user_profile.education}
            Skills: {user_profile.skills}
            
            The cover letter should:
            1. Be professional and engaging
            2. Highlight relevant experience and skills
            3. Show enthusiasm for the role and company
            4. Address specific job requirements
            5. Be concise (3-4 paragraphs)
            6. Include proper formatting with date, address, salutation, and closing
            
            Make it personalized and compelling.
            """
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            return response.text if response.text else "Cover letter generation failed"
            
        except Exception as e:
            logging.error(f"Error generating cover letter: {e}")
            return f"Error generating cover letter: {str(e)}"
    
    @staticmethod
    def generate_interview_questions(job_description, position_title):
        """Generate relevant interview questions based on job requirements"""
        try:
            prompt = f"""
            Based on this job posting, generate potential interview questions:
            
            Position: {position_title}
            Job Description:
            {job_description}
            
            Generate 3 categories of questions:
            
            1. TECHNICAL QUESTIONS (5-8 questions):
            - Role-specific technical questions
            - Problem-solving scenarios
            - Tool/technology specific questions
            
            2. BEHAVIORAL QUESTIONS (5-8 questions):
            - STAR method questions
            - Team collaboration scenarios
            - Leadership and conflict resolution
            
            3. COMPANY/ROLE FIT QUESTIONS (3-5 questions):
            - Questions about motivation
            - Culture fit
            - Career goals alignment
            
            For each question, also provide:
            - Brief guidance on what the interviewer is looking for
            - Key points to address in the answer
            
            Format clearly with headers and bullet points.
            """
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            return response.text if response.text else "Interview questions generation failed"
            
        except Exception as e:
            logging.error(f"Error generating interview questions: {e}")
            return f"Error generating interview questions: {str(e)}"
