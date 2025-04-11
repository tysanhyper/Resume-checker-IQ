import re
import os
import logging
from openai import OpenAI
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client with proper configuration
try:
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        logger.warning("OpenAI API key not found in environment variables")
        client = None
    else:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.openai.com/v1"  # Explicitly set the base URL
        )
except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {str(e)}")
    client = None

# Comment out the OpenAI import and API key to avoid errors
# import openai
# openai.api_key = "your-api-key" (don't use the key from your file as it might not be valid)

def suggest_improvements(resume_text: str) -> dict:
    """
    Generate personalized resume improvement suggestions using OpenAI.
    
    Args:
        resume_text (str): The text content of the resume
        
    Returns:
        dict: A dictionary containing various improvement suggestions
    """
    if not client:
        logger.warning("OpenAI client not available, using fallback suggestions")
        return get_fallback_suggestions()

    try:
        # Create a prompt for OpenAI
        prompt = f"""Analyze the following resume and provide specific, actionable improvements in these categories:
        1. Format and Structure
        2. Content and Impact
        3. Skills and Keywords
        4. Professional Branding
        5. Action Words and Language

        Resume:
        {resume_text}

        Please provide detailed, specific suggestions for each category. Focus on modern resume best practices and industry standards.
        Format the response as a JSON-like structure with categories as keys and lists of suggestions as values.
        Keep suggestions concise but actionable."""

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional resume reviewer and career coach. Provide specific, actionable suggestions to improve resumes."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        # Extract and parse the suggestions
        suggestions_text = response.choices[0].message.content

        # If the API call was successful but returned no suggestions, use fallback
        if not suggestions_text:
            logger.warning("OpenAI returned empty suggestions, using fallback")
            return get_fallback_suggestions()

        # Try to parse the response as JSON
        try:
            # Remove any markdown formatting if present
            clean_text = suggestions_text.replace("```json", "").replace("```", "").strip()
            suggestions_dict = json.loads(clean_text)
            logger.info("Successfully parsed OpenAI suggestions as JSON")
            return {
                "suggestions": suggestions_dict,
                "source": "ai-powered"
            }
        except json.JSONDecodeError:
            # If JSON parsing fails, return the raw text
            logger.info("Returning raw OpenAI suggestions")
            return {
                "suggestions": suggestions_text,
                "source": "ai-powered"
            }

    except Exception as e:
        logger.error(f"Error generating suggestions with OpenAI: {str(e)}")
        return get_fallback_suggestions()

def get_fallback_suggestions() -> list:
    """Provide fallback suggestions when the API call fails"""
    return [
        {"category": "Format and Structure", "text": "Use consistent formatting throughout the document with clear section headings."},
        {"category": "Content and Impact", "text": "Quantify achievements with specific metrics and focus on results rather than responsibilities."},
        {"category": "Skills and Keywords", "text": "Include industry-specific keywords and highlight technical skills relevant to the position."},
        {"category": "Professional Branding", "text": "Create a compelling professional summary and include LinkedIn profile and portfolio links."},
        {"category": "Action Words and Language", "text": "Start bullet points with strong action verbs and use present tense for current roles."},
        {"category": "ATS Optimization", "text": "Ensure your resume is ATS-friendly by using standard section headers and including relevant keywords."},
        {"category": "Contact Information", "text": "Make sure your contact information is current and clearly visible at the top of your resume."}
    ]

def suggest_improvements_without_openai(text):
    """
    Analyze a resume and suggest improvements without relying on external APIs.
    
    Args:
        text (str): The text content of the resume
        
    Returns:
        str: A string containing improvement suggestions
    """
    suggestions = []
    
    # Check for resume length
    word_count = len(text.split())
    if word_count < 300:
        suggestions.append("Your resume is quite short. Consider adding more details about your experiences and achievements.")
    elif word_count > 1000:
        suggestions.append("Your resume is quite long. Consider focusing on the most relevant experiences and skills.")
    
    # Check for action verbs at the beginning of bullet points
    bullet_points = re.findall(r'[•\-\*]\s*(.*?)(?:\n|$)', text)
    weak_bullets = 0
    
    action_verbs = ["achieved", "implemented", "developed", "created", "managed", "led", "designed", "built"]
    for bullet in bullet_points:
        if not any(bullet.lower().startswith(verb) for verb in action_verbs):
            weak_bullets += 1
    
    if weak_bullets > 0 and len(bullet_points) > 0:
        if weak_bullets / len(bullet_points) > 0.3:  # If more than 30% are weak
            suggestions.append("Start your bullet points with strong action verbs like 'Achieved', 'Implemented', 'Developed', etc.")
    
    # Check for quantifiable achievements
    if not re.search(r'\d+%|\d+ percent|increased|decreased|reduced|improved|grew|expanded', text, re.IGNORECASE):
        suggestions.append("Include quantifiable achievements (e.g., 'Increased sales by 20%', 'Reduced costs by $10K').")
    
    # Check for LinkedIn profile
    if not re.search(r'linkedin\.com|linkedin', text, re.IGNORECASE):
        suggestions.append("Consider adding your LinkedIn profile URL.")
    
    # Check for ATS-friendly formatting
    if not re.search(r'skills|education|experience|projects', text, re.IGNORECASE):
        suggestions.append("Make sure to clearly label your sections (Skills, Education, Experience, Projects) for ATS systems.")
    
    # Check for contact information
    if not re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
        suggestions.append("Ensure your email address is included and clearly visible.")
    
    if not re.search(r'\+?\d[\d\-\s]{8,}\d', text):
        suggestions.append("Include a phone number for employers to contact you.")
    
    # Default suggestions if none were found
    if not suggestions:
        return "Try using active language, quantifying impact, and aligning with job descriptions. Ensure your resume is ATS-friendly by using standard section headers and including relevant keywords from the job description."
    
    return " ".join(suggestions)

# Commented out OpenAI version - keep this as reference if you want to use it later
'''
def suggest_improvements_with_openai(text):
    """Use OpenAI API to generate suggestions (requires API key)"""
    try:
        prompt = f"Suggest improvements to this resume to make it more ATS-friendly:\n\n{text}"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"OpenAI API error: {str(e)}")
        # Fallback to basic suggestions
        return suggest_improvements(text)
'''