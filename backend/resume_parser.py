import re

# Make spaCy optional - fallback to basic extraction if not available
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except (ImportError, OSError):
    SPACY_AVAILABLE = False
    print("spaCy not available, using basic extraction methods")

def extract_resume_data(text: str) -> dict:
    """
    Extract key information from resume text
    
    Args:
        text (str): The text content of the resume
        
    Returns:
        dict: Extracted data including name, email, phone, skills, etc.
    """
    # Basic regex extractions that will always work
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.search(email_pattern, text)
    email = email_match.group(0) if email_match else ""
    
    phone_pattern = r'\+?\d[\d\-\s]{8,}\d'
    phone_match = re.search(phone_pattern, text)
    phone = phone_match.group(0) if phone_match else ""
    
    # Name extraction - fallback to first line if spaCy is not available
    name = ""
    if SPACY_AVAILABLE:
        doc = nlp(text[:1000])  # Only process the first 1000 chars for performance
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                name = ent.text
                break
    
    # Fallback name extraction if spaCy didn't find it
    if not name:
        lines = text.strip().split('\n')
        if lines:
            name = lines[0].strip()
            
    # Education extraction
    education_patterns = [
        r'(?:EDUCATION|ACADEMIC BACKGROUND|QUALIFICATIONS)',
        r'(?:B\.?Tech|B\.?E|M\.?Tech|M\.?E|PhD|M\.?S|B\.?S|M\.?Sc|B\.?Sc|M\.?B\.?A|B\.?B\.?A)',
        r'(?:Bachelor|Master|Doctor|Diploma)',
        r'(?:University|College|Institute|School)'
    ]
    
    education = []
    for pattern in education_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        education.extend(matches)
    
    # Experience extraction
    experience_patterns = [
        r'\d+[\+]? years? (?:of )?(?:experience|work)',
        r'(?:EXPERIENCE|WORK HISTORY|EMPLOYMENT|WORK EXPERIENCE)',
        r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4} (?:to|-)' 
    ]
    
    experience = []
    for pattern in experience_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        experience.extend(matches)
    
    # Extract skills - comprehensive list
    skill_keywords = [
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby', 'swift',
        'html', 'css', 'sass', 'less', 'bootstrap', 'tailwind',
        'react', 'angular', 'vue', 'svelte', 'jquery', 'flask', 'django', 'express', 'spring', 
        'node.js', 'mongodb', 'mysql', 'postgresql', 'oracle', 'firebase',
        'aws', 'azure', 'gcp', 'terraform', 'docker', 'kubernetes', 'jenkins',
        'git', 'jira', 'figma', 'sketch', 'photoshop', 'illustrator',
        'machine learning', 'deep learning', 'nlp', 'computer vision', 'data science',
        'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'matplotlib',
        'tableau', 'power bi', 'excel', 'sql', 'nosql', 'rest api', 'graphql',
        'agile', 'scrum', 'kanban', 'devops', 'ci/cd', 'unit testing', 'test automation'
    ]
    
    skills = []
    for skill in skill_keywords:
        if re.search(r'\b' + re.escape(skill) + r'\b', text.lower()):
            skills.append(skill)
    
    return {
        "name": name,
        "email": email,
        "phone": phone,
        "skills": skills,
        "education": education[:3],  # Limit to first 3 for display purposes
        "experience": experience[:3]  # Limit to first 3 for display purposes
    }