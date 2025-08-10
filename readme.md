# Job Application Assistant

## Overview

A Flask-based web application that leverages Google's Gemini AI to assist job seekers with application preparation. The application provides AI-powered analysis of job postings, customized resume suggestions, cover letter generation, and interview question preparation. Users can create profiles to store their professional information and receive personalized recommendations for multiple job applications.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Web Framework
- **Flask**: Lightweight web framework chosen for rapid development and simplicity
- **SQLAlchemy**: ORM for database operations with declarative base pattern
- **Jinja2 Templates**: Server-side rendering with template inheritance for consistent UI

### Database Layer
- **SQLite**: Default database for development with configurable DATABASE_URL for production
- **Three core models**: JobPosting, UserProfile, and GeneratedContent
- **Relationship mapping**: Foreign key relationships between generated content and both job postings and user profiles
- **Connection pooling**: Configured with pool_recycle and pool_pre_ping for reliability

### AI Integration
- **Google Gemini API**: Primary AI service for content generation and analysis
- **Service layer pattern**: JobAssistantService class abstracts AI operations
- **Four AI functions**: Job analysis, resume customization, cover letter generation, and interview preparation
- **Error handling**: Comprehensive exception handling with logging for AI service failures

### Frontend Architecture
- **Bootstrap 5**: Dark theme UI framework with responsive design
- **Font Awesome**: Icon library for consistent visual elements
- **Progressive enhancement**: JavaScript for form validation, auto-resize textareas, and copy functionality
- **Mobile-first**: Responsive design with mobile navigation and touch-friendly interface

### Authentication & Session Management
- **Flask sessions**: Simple session-based state management
- **Single user model**: Designed for individual use rather than multi-user authentication
- **Environment-based secrets**: Configurable session keys for security

### Content Management
- **Template-based routing**: Separate routes for each major function (analyze, customize, generate, interview)
- **Content persistence**: All generated content stored in database with timestamps
- **Export functionality**: Copy-to-clipboard and download features for generated content

## External Dependencies

### AI Services
- **Google Gemini API**: Requires GEMINI_API_KEY environment variable for content generation
- **genai Python client**: Official Google client library for API communication

### Frontend Libraries
- **Bootstrap 5 (CDN)**: UI framework with Replit dark theme integration
- **Font Awesome 6 (CDN)**: Icon library loaded from CDN

### Production Infrastructure
- **ProxyFix middleware**: Handles reverse proxy headers for deployment
- **Environment configuration**: DATABASE_URL and SESSION_SECRET for production deployment
- **WSGI compatibility**: Ready for deployment with Gunicorn or similar WSGI servers

### Database
- **SQLite**: Default for development and testing
- **PostgreSQL**: Recommended for production (configurable via DATABASE_URL)
- **Migration support**: SQLAlchemy's create_all() for schema initialization

### Demo 



https://github.com/user-attachments/assets/f17dfe40-65a8-466b-ab1d-c62bb7754bb7

