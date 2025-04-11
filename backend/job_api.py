import requests
import logging

logger = logging.getLogger(__name__)

def get_real_jobs(skill, country="in"):
    """
    Get real job listings from the JSearch API
    
    Args:
        skill (str): The skill to search for jobs
        country (str): Country code (default: "in" for India)
        
    Returns:
        list: A list of job dictionaries
    """
    try:
        url = "https://jsearch.p.rapidapi.com/search"
        querystring = {
            "query": f"{skill} developer",
            "page": "1",
            "num_pages": "1",
            "country": country,
            "remote_jobs_only": "false"
        }
        headers = {
            "x-rapidapi-key": "YOUR RAPIDAPI KEY",
            "x-rapidapi-host": "YOUR RAPIDAPI HOST"
        }

        response = requests.get(url, headers=headers, params=querystring, timeout=10)
        
        # Check if the request was successful
        if response.status_code != 200:
            logger.warning(f"API request failed with status code {response.status_code}")
            return get_mock_jobs(skill, country)
            
        data = response.json()
        jobs = data.get("data", [])

        # Process the jobs
        top_jobs = []
        for job in jobs[:5]:
            salary = job.get("job_min_salary")
            if salary is not None:
                try:
                    salary = f"₹{int(salary):,}" if country == "in" else f"${int(salary):,}"
                except (ValueError, TypeError):
                    salary = "Not specified"
            else:
                salary = "Not specified"
                
            top_jobs.append({
                "title": job.get("job_title", "Software Developer"),
                "company": job.get("employer_name", "Tech Company"),
                "location": f"{job.get('job_city', 'Remote')}, {job.get('job_country', 'India')}",
                "salary": salary,
                "experience": job.get("job_required_experience", "Not specified"),
                "employment_type": job.get("job_employment_type", "Full-time"),
                "apply_link": job.get("job_apply_link", "https://example.com/apply"),
                "posted_at": job.get("job_posted_at_datetime_utc", "Recent"),
                "description": job.get("job_description", "")[:200] + "..."  # Truncate description
            })
        
        # Return mock data if no jobs were found
        return top_jobs if top_jobs else get_mock_jobs(skill, country)
        
    except Exception as e:
        logger.error(f"Error fetching jobs: {str(e)}")
        # Fallback to mock data in case of any error
        return get_mock_jobs(skill, country)

def get_mock_jobs(skill, country="in"):
    """Provide mock job data when the API fails"""
    currency = "₹" if country == "in" else "$"
    locations = {
        "in": ["Bangalore", "Mumbai", "Hyderabad", "Delhi", "Pune"],
        "us": ["New York", "San Francisco", "Seattle", "Austin", "Boston"]
    }
    companies = {
        "in": ["TCS", "Infosys", "Wipro", "HCL", "Tech Mahindra"],
        "us": ["Google", "Microsoft", "Amazon", "Apple", "Meta"]
    }
    
    salary_ranges = {
        "in": ["8,00,000", "12,00,000", "15,00,000", "20,00,000", "25,00,000"],
        "us": ["100,000", "120,000", "150,000", "180,000", "200,000"]
    }
    
    return [
        {
            "title": f"Senior {skill.capitalize()} Developer",
            "company": companies[country][0],
            "location": f"{locations[country][0]}, {'India' if country == 'in' else 'USA'}",
            "salary": f"{currency}{salary_ranges[country][0]} - {currency}{salary_ranges[country][1]} per year",
            "experience": "5-8 years",
            "employment_type": "Full-time",
            "apply_link": "https://example.com/jobs/1",
            "posted_at": "2 days ago",
            "description": f"Looking for an experienced {skill} developer with strong problem-solving skills..."
        },
        {
            "title": f"{skill.capitalize()} Team Lead",
            "company": companies[country][1],
            "location": f"{locations[country][1]}, {'India' if country == 'in' else 'USA'}",
            "salary": f"{currency}{salary_ranges[country][1]} - {currency}{salary_ranges[country][2]} per year",
            "experience": "8-12 years",
            "employment_type": "Full-time",
            "apply_link": "https://example.com/jobs/2",
            "posted_at": "1 week ago",
            "description": f"Leading {skill} development team in building scalable applications..."
        },
        {
            "title": f"{skill.capitalize()} Developer",
            "company": companies[country][2],
            "location": f"{locations[country][2]}, {'India' if country == 'in' else 'USA'}",
            "salary": f"{currency}{salary_ranges[country][0]} - {currency}{salary_ranges[country][1]} per year",
            "experience": "2-5 years",
            "employment_type": "Full-time",
            "apply_link": "https://example.com/jobs/3",
            "posted_at": "3 days ago",
            "description": f"Developing and maintaining {skill} applications..."
        },
        {
            "title": f"Senior {skill.capitalize()} Engineer",
            "company": companies[country][3],
            "location": f"{locations[country][3]}, {'India' if country == 'in' else 'USA'}",
            "salary": f"{currency}{salary_ranges[country][2]} - {currency}{salary_ranges[country][3]} per year",
            "experience": "5-8 years",
            "employment_type": "Full-time",
            "apply_link": "https://example.com/jobs/4",
            "posted_at": "Just now",
            "description": f"Building next-generation {skill} solutions..."
        },
        {
            "title": f"{skill.capitalize()} Architect",
            "company": companies[country][4],
            "location": f"{locations[country][4]}, {'India' if country == 'in' else 'USA'}",
            "salary": f"{currency}{salary_ranges[country][3]} - {currency}{salary_ranges[country][4]} per year",
            "experience": "10-15 years",
            "employment_type": "Full-time",
            "apply_link": "https://example.com/jobs/5",
            "posted_at": "4 days ago",
            "description": f"Architecting and leading {skill} projects..."
        }
    ]