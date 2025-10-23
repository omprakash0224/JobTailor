import os
import logging
from google import genai
from google.genai import types
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Initialize Gemini client
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    logging.error("GEMINI_API_KEY not found in environment variables.")
    raise ValueError("GEMINI_API_KEY is required but not set in environment variables")

# Create client instance
client = genai.Client(api_key=api_key)

class JobAssistantService:

    @staticmethod
    def _generate_content(prompt):
        """Helper function to generate content with error handling"""
        try:
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )

            if not response.text:
                logging.warning("Content generation resulted in an empty response.")
                return "Analysis failed: No content generated."

            return response.text

        except Exception as e:
            logging.error(f"Error during content generation: {e}")
            return f"Error during content generation: {str(e)}"

    @staticmethod
    def parse_resume(resume_text):
        """Parse resume and extract structured information including projects and certifications"""
        try:
            prompt = f"""
            Parse the following resume text and extract the information in a structured JSON format.
            
            Resume Text:
            {resume_text}
            
            Please extract and return a JSON object with the following fields.
            For ALL fields, provide the data as PLAIN TEXT STRINGS (not nested objects or arrays).
            Format lists as bullet points or comma-separated text.
            
            {{
                "name": "Full name as plain text",
                "email": "Email address as plain text",
                "phone": "Phone number as plain text",
                "summary": "Professional summary as plain text paragraph",
                "experience": "All work experience formatted as plain text with line breaks. Include job titles, companies, dates, and responsibilities",
                "education": "All education details formatted as plain text with line breaks. Include degrees, institutions, dates, GPA, coursework",
                "skills": "All skills formatted as plain text with categories and bullet points or comma-separated",
                "projects": "All projects formatted as plain text with line breaks. For each project include: name, description, technologies, role, achievements",
                "certifications": "All certifications formatted as plain text with line breaks. For each include: name, organization, date obtained, expiration"
            }}
            
            IMPORTANT: Return everything as plain text strings, not as nested JSON objects or arrays.
            Use newlines (\\n) and formatting characters for structure.
            
            If any field is not found in the resume, set it to an empty string.
            Return ONLY the JSON object, no additional text.
            """
            
            response = JobAssistantService._generate_content(prompt)
            
            # Try to parse JSON response
            try:
                # Clean the response if it has markdown code blocks
                cleaned_response = response.strip()
                if cleaned_response.startswith('```json'):
                    cleaned_response = cleaned_response[7:]
                if cleaned_response.startswith('```'):
                    cleaned_response = cleaned_response[3:]
                if cleaned_response.endswith('```'):
                    cleaned_response = cleaned_response[:-3]
                cleaned_response = cleaned_response.strip()
                
                parsed_data = json.loads(cleaned_response)
                
                # Ensure all values are strings
                for key, value in parsed_data.items():
                    if isinstance(value, (dict, list)):
                        parsed_data[key] = json.dumps(value, indent=2)
                
                return parsed_data
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse JSON response: {e}")
                # Return a fallback structure with the raw text
                return {
                    "name": "",
                    "email": "",
                    "phone": "",
                    "summary": response[:500],
                    "experience": "",
                    "education": "",
                    "skills": "",
                    "projects": "",
                    "certifications": ""
                }
                
        except Exception as e:
            logging.error(f"Error parsing resume: {e}")
            return {
                "name": "",
                "email": "",
                "phone": "",
                "summary": f"Error parsing resume: {str(e)}",
                "experience": "",
                "education": "",
                "skills": "",
                "projects": "",
                "certifications": ""
            }

    @staticmethod
    def analyze_job_posting(job_description):
        """Analyze job posting and extract key requirements and skills"""
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
        7. Relevant certifications mentioned
        8. Types of projects that would be relevant
        
        Format your response in clear sections with bullet points.
        """
        return JobAssistantService._generate_content(prompt)

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
            Projects: {user_profile.projects}
            Certifications: {user_profile.certifications}
            
            Please provide:
            1. Suggested changes to the professional summary
            2. Skills to highlight or add
            3. Experience points to emphasize
            4. Which projects to highlight and how to describe them
            5. Which certifications to emphasize
            6. Keywords to include for ATS optimization
            7. Sections to reorganize or prioritize
            8. Any gaps to address or downplay
            
            Make the suggestions specific and actionable.
            """
            
            return JobAssistantService._generate_content(prompt)
            
        except Exception as e:
            logging.error(f"Error customizing resume: {e}")
            return f"Error customizing resume: {str(e)}"

    @staticmethod
    def generate_cover_letter(job_description, user_profile, company_name, position_title):
        """Generate a personalized cover letter"""
        try:
            prompt = f"""
            Generate a professional cover letter for the following job application:
            
            Position: {position_title}
            Company: {company_name}
            
            Job Description:
            {job_description}
            
            Candidate Profile:
            Name: {user_profile.name}
            Summary: {user_profile.summary}
            Experience: {user_profile.experience}
            Education: {user_profile.education}
            Skills: {user_profile.skills}
            Projects: {user_profile.projects}
            Certifications: {user_profile.certifications}
            
            Please write a compelling cover letter that:
            1. Opens with a strong introduction
            2. Highlights relevant experience and projects
            3. Mentions relevant certifications if applicable
            4. Demonstrates knowledge of the company
            5. Shows enthusiasm for the role
            6. Closes with a call to action
            
            Keep it professional, concise (3-4 paragraphs), and tailored to this specific position.
            """
            
            return JobAssistantService._generate_content(prompt)
            
        except Exception as e:
            logging.error(f"Error generating cover letter: {e}")
            return f"Error generating cover letter: {str(e)}"

    @staticmethod
    def generate_interview_questions(job_description, user_profile):
        """Generate potential interview questions and suggested answers"""
        try:
            prompt = f"""
            Based on the job posting and candidate profile, generate likely interview questions and suggested answers:
            
            Job Description:
            {job_description}
            
            Candidate Profile:
            Experience: {user_profile.experience}
            Skills: {user_profile.skills}
            Projects: {user_profile.projects}
            Certifications: {user_profile.certifications}
            
            Please provide:
            1. 5-7 technical questions based on required skills
            2. 3-5 behavioral questions
            3. 2-3 questions about specific projects or certifications
            4. Suggested answers tailored to the candidate's background
            5. Tips for showcasing relevant project experience
            
            Format each question with a suggested answer below it.
            """
            
            return JobAssistantService._generate_content(prompt)
            
        except Exception as e:
            logging.error(f"Error generating interview questions: {e}")
            return f"Error generating interview questions: {str(e)}"
