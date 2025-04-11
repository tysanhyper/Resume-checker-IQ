import re
from typing import Dict, List, Tuple
import json

def calculate_ats_score(resume_text: str, skills: list) -> Dict:
    """Calculate ATS compatibility score based on various factors"""
    score = 100
    reasons = []
    improvements = []

    # Check for proper section headers
    sections = ['education', 'experience', 'skills', 'projects', 'work']
    found_sections = sum(1 for section in sections if re.search(rf'\b{section}\b', resume_text.lower()))
    section_score = (found_sections / len(sections)) * 25
    score -= (25 - section_score)
    if section_score < 25:
        improvements.append("Add clear section headers (Education, Experience, Skills, etc.)")

    # Check for contact information
    contact_elements = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\+?\d[\d\-\s]{8,}\d',
        'linkedin': r'linkedin\.com|linkedin'
    }
    missing_contacts = []
    for element, pattern in contact_elements.items():
        if not re.search(pattern, resume_text):
            missing_contacts.append(element)
            score -= 5
    if missing_contacts:
        improvements.append(f"Add missing contact information: {', '.join(missing_contacts)}")

    # Check for measurable results
    if not re.search(r'\d+%|\d+ percent|\d+x|\$\d+|\d+ dollars', resume_text, re.IGNORECASE):
        score -= 10
        improvements.append("Add quantifiable achievements (%, $, numbers)")

    # Check formatting consistency
    if len(re.findall(r'\n{3,}', resume_text)) > 2:
        score -= 5
        improvements.append("Improve formatting consistency (remove excess spacing)")

    # Check bullet point consistency
    bullets = re.findall(r'[•\-\*]\s*(.*?)(?:\n|$)', resume_text)
    if len(bullets) < 5:
        score -= 5
        improvements.append("Use more bullet points to highlight experiences")

    # Analyze keyword density
    total_words = len(resume_text.split())
    skill_mentions = sum(1 for skill in skills if re.search(rf'\b{skill}\b', resume_text.lower()))
    keyword_density = (skill_mentions / total_words) * 100
    if keyword_density < 3:
        score -= 10
        improvements.append("Increase relevant keyword density")

    # Ensure score stays within 0-100 range
    score = max(0, min(100, score))

    return {
        "ats_score": round(score),
        "improvements": improvements,
        "keyword_density": round(keyword_density, 2),
        "sections_found": found_sections,
        "total_sections": len(sections)
    }

def score_resume(skills: List[str]) -> Tuple[int, List[str]]:
    """Score a resume based on skills and identify missing important skills"""
    # Market skills with their importance weights and categories
    market_skills = {
        'python': {'weight': 10, 'category': 'Programming Languages'},
        'javascript': {'weight': 9, 'category': 'Programming Languages'},
        'typescript': {'weight': 8, 'category': 'Programming Languages'},
        'java': {'weight': 9, 'category': 'Programming Languages'},
        'react': {'weight': 9, 'category': 'Frontend'},
        'angular': {'weight': 8, 'category': 'Frontend'},
        'vue': {'weight': 7, 'category': 'Frontend'},
        'node.js': {'weight': 8, 'category': 'Backend'},
        'sql': {'weight': 9, 'category': 'Database'},
        'nosql': {'weight': 7, 'category': 'Database'},
        'mongodb': {'weight': 7, 'category': 'Database'},
        'postgresql': {'weight': 8, 'category': 'Database'},
        'mysql': {'weight': 7, 'category': 'Database'},
        'aws': {'weight': 10, 'category': 'Cloud'},
        'azure': {'weight': 8, 'category': 'Cloud'},
        'gcp': {'weight': 8, 'category': 'Cloud'},
        'docker': {'weight': 9, 'category': 'DevOps'},
        'kubernetes': {'weight': 8, 'category': 'DevOps'},
        'git': {'weight': 8, 'category': 'Tools'},
        'ci/cd': {'weight': 7, 'category': 'DevOps'},
        'rest api': {'weight': 8, 'category': 'Backend'},
        'graphql': {'weight': 7, 'category': 'Backend'},
        'machine learning': {'weight': 9, 'category': 'AI/ML'},
        'data science': {'weight': 9, 'category': 'AI/ML'},
        'tensorflow': {'weight': 8, 'category': 'AI/ML'},
        'pytorch': {'weight': 8, 'category': 'AI/ML'},
    }
    
    # Normalize skills to lowercase for comparison
    normalized_skills = [skill.lower() for skill in skills]
    
    # Calculate score based on matched skills and their weights
    total_score = 0
    max_possible_score = 0
    skill_categories = {}
    
    # Get the top 10 highest weighted skills for max possible score
    top_skills = sorted(market_skills.items(), key=lambda x: x[1]['weight'], reverse=True)[:10]
    max_possible_score = sum(skill_info['weight'] for _, skill_info in top_skills)
    
    # Calculate actual score and organize skills by category
    for skill, info in market_skills.items():
        if skill in normalized_skills:
            total_score += info['weight']
            category = info['category']
            if category not in skill_categories:
                skill_categories[category] = []
            skill_categories[category].append(skill)
    
    # Normalize to 100-point scale
    normalized_score = min(int((total_score / max_possible_score) * 100), 100)
    
    # Determine missing important skills
    missing = []
    for skill, info in top_skills:
        if skill not in normalized_skills:
            missing.append({
                'skill': skill,
                'category': info['category'],
                'importance': info['weight']
            })
    
    # Limit to top 5 missing skills
    missing = missing[:5]
    
    return normalized_score, missing, skill_categories