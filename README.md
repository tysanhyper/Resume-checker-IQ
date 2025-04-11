# ResumeIQ - AI-Powered Resume Analyzer

ResumeIQ is an AI-powered resume analysis and job matching platform that helps users optimize their resumes and find relevant job opportunities.

## Features
- Resume parsing and analysis
- Skill extraction
- ATS compatibility check
- Job recommendations
- Resume optimization suggestions
- User authentication
- Mobile-responsive design

## Prerequisites
- Python 3.8 or higher
- Node.js 14+ (optional, for frontend development)
- Git

## Local Development Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd resumeiq
```

2. **Create and activate a virtual environment**
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
Create a `.env` file in the root directory:
```env
SECRET_KEY=your_secret_key_here
DEBUG=True
DATABASE_URL=sqlite:///./resumeiq.db
```

5. **Run the application**
```bash
# Start the FastAPI server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at `http://localhost:8000`

## Project Structure
```
resumeiq/
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── scoring.py
│   ├── resume_parser.py
│   ├── job_api.py
│   └── suggestions.py
├── frontend/
│   ├── static/
│   │   ├── js/
│   │   │   └── main.js
│   │   ├── css/
│   │   │   └── style.css
│   │   └── img/
│   └── templates/
│       ├── index.html
│       ├── results.html
│       ├── about.html
│       └── ...
├── requirements.txt
├── .env
└── README.md
```

## Deployment Guide

### Option 1: Deploy to Heroku

1. **Install Heroku CLI and login**
```bash
# Install Heroku CLI from https://devcenter.heroku.com/articles/heroku-cli
heroku login
```

2. **Create a new Heroku app**
```bash
heroku create resumeiq-app
```

3. **Add Heroku-specific files**

Create a `Procfile` in the root directory:
```
web: uvicorn backend.main:app --host=0.0.0.0 --port=${PORT:-5000}
```

4. **Deploy to Heroku**
```bash
git push heroku main
```

### Option 2: Deploy to DigitalOcean App Platform

1. Fork this repository to your GitHub account
2. Sign up for DigitalOcean
3. In the DigitalOcean dashboard:
   - Create a new app
   - Connect your GitHub repository
   - Select the Python environment
   - Configure environment variables
   - Deploy

### Option 3: Deploy using Docker

1. **Build the Docker image**
```bash
docker build -t resumeiq .
```

2. **Run the container**
```bash
docker run -d -p 8000:8000 resumeiq
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| SECRET_KEY | Application secret key | None |
| DEBUG | Debug mode | False |
| DATABASE_URL | Database connection string | sqlite:///./resumeiq.db |

## API Documentation

Once the application is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/improvement`)
3. Make changes and commit (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Create a Pull Request

## Support

For support, email support@resumeiq.com or create an issue in the repository.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 