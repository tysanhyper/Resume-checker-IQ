from fastapi import FastAPI, File, UploadFile, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os, tempfile, traceback, logging, fitz
import docx2txt
from PIL import Image
import pytesseract

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="ResumeIQ")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Fixed path resolution
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "frontend", "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "frontend", "templates")

# Mount static files and templates
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Import dependencies
from backend.scoring import score_resume, calculate_ats_score
from backend.resume_parser import extract_resume_data
from backend.job_api import get_real_jobs
from backend.suggestions import suggest_improvements

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the main upload page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    """Serve the about page"""
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    """Serve the contact page"""
    return templates.TemplateResponse("contact.html", {"request": request})

@app.get("/signin", response_class=HTMLResponse)
async def signin(request: Request):
    """Serve the signin page"""
    return templates.TemplateResponse("signin.html", {"request": request})

@app.get("/signup", response_class=HTMLResponse)
async def signup(request: Request):
    """Serve the signup page"""
    return templates.TemplateResponse("signup.html", {"request": request})

@app.get("/terms", response_class=HTMLResponse)
async def terms(request: Request):
    """Serve the terms of service page"""
    return templates.TemplateResponse("termsofservice.html", {"request": request})

@app.get("/privacy", response_class=HTMLResponse)
async def privacy(request: Request):
    """Serve the privacy policy page"""
    return templates.TemplateResponse("privacy.html", {"request": request})

@app.get("/forgotpassword", response_class=HTMLResponse)
async def forgotpassword(request: Request):
    """Serve the forgot password page"""
    return templates.TemplateResponse("forgotpassword.html", {"request": request})

@app.get("/results", response_class=HTMLResponse)
async def results(request: Request):
    """Serve the results page"""
    return templates.TemplateResponse("results.html", {"request": request})

@app.post("/upload_resume/")
async def upload_resume(file: UploadFile = File(...)):
    """Process uploaded resume and return analysis"""
    logger.info(f"Received resume upload: {file.filename}")
    tmp_path = None
    text = ""
    
    try:
        contents = await file.read()
        if not contents:
            return {"error": "The uploaded file is empty"}
            
        ext = file.filename.split('.')[-1].lower()
        logger.info(f"File extension: {ext}")

        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        # Extract text based on file type
        if ext == "pdf":
            try:
                with fitz.open(tmp_path) as doc:
                    text = "\n".join(page.get_text() for page in doc)
            except Exception as e:
                logger.error(f"Error processing PDF: {str(e)}")
                raise
        elif ext in ("docx", "doc"):
            text = docx2txt.process(tmp_path)
        elif ext == "txt":
            with open(tmp_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        elif ext in ("png", "jpg", "jpeg"):
            try:
                image = Image.open(tmp_path)
                text = pytesseract.image_to_string(image)
            except Exception as e:
                logger.error(f"Error processing image: {str(e)}")
                raise
        else:
            return {"error": f"Unsupported file format: {ext}"}

        if not text.strip():
            return {"error": "No text could be extracted from the file"}

        # Process the resume
        data = extract_resume_data(text)
        
        # Calculate scores
        score, missing_skills, skill_categories = score_resume(data["skills"])
        ats_score_data = calculate_ats_score(text, data["skills"])
        
        # Get job recommendations
        first_skill = data["skills"][0] if data["skills"] else "developer"
        indian_jobs = get_real_jobs(first_skill, country="in")
        us_jobs = get_real_jobs(first_skill, country="us")
        
        # Get improvement suggestions
        improvement = suggest_improvements(text)
        
        # Format suggestions properly
        formatted_suggestions = []
        if isinstance(improvement, dict) and "suggestions" in improvement:
            if isinstance(improvement["suggestions"], dict):
                for category, items in improvement["suggestions"].items():
                    if isinstance(items, list):
                        for item in items:
                            formatted_suggestions.append({
                                "category": category.replace("_", " ").title(),
                                "text": item
                            })
                    else:
                        formatted_suggestions.append({
                            "category": category.replace("_", " ").title(),
                            "text": items
                        })
            elif isinstance(improvement["suggestions"], list):
                formatted_suggestions = improvement["suggestions"]
            else:
                formatted_suggestions = [{"category": "General", "text": str(improvement["suggestions"])}]
        elif isinstance(improvement, list):
            formatted_suggestions = improvement
        else:
            formatted_suggestions = [{"category": "General", "text": str(improvement)}]

        response_data = {
            "scores": {
                "overall": score,
                "ats": ats_score_data["ats_score"],
                "content": int((score + ats_score_data["ats_score"]) / 2)
            },
            "skills": [
                {"name": skill, "score": 85} for skill in data["skills"]
            ],
            "suggestions": formatted_suggestions,
            "jobs": [
                {
                    "title": job["title"],
                    "company": job["company"],
                    "location": job["location"],
                    "match": int((score + ats_score_data["ats_score"]) / 2),
                    "url": job["apply_link"]
                }
                for job in indian_jobs + us_jobs
            ]
        }

        return response_data

    except Exception as e:
        logger.error(f"Error processing resume: {str(e)}")
        logger.error(traceback.format_exc())
        return {"error": f"Error processing resume: {str(e)}"}
        
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                import time
                time.sleep(0.1)
                os.unlink(tmp_path)
            except Exception as e:
                logger.warning(f"Failed to remove temporary file {tmp_path}: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "ResumeIQ API is running"}

@app.get("/welcome")
async def welcome(request: Request):
    """Returns a welcome message and logs request metadata"""
    logger.info(f"Request received: {request.method} {request.url.path}")
    return {"message": "Welcome to the ResumeIQ API!"}
