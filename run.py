import uvicorn
import logging
import os
import sys
import socket

# Setup logging with more detailed format
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG for more detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required directories exist"""
    required_dirs = [
        "frontend/static",
        "frontend/templates",
        "backend"
    ]
    
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            logger.error(f"Required directory not found: {dir_path}")
            return False
        else:
            logger.info(f"Found directory: {dir_path}")
    return True

def check_port_available(port):
    """Check if the port is available"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('localhost', port))
        sock.close()
        return True
    except OSError:
        return False

if __name__ == "__main__":
    try:
        # Check if required directories exist
        if not check_dependencies():
            logger.error("Missing required directories. Please ensure all project directories are present.")
            sys.exit(1)
            
        # Check if port is available
        port = 8000
        if not check_port_available(port):
            logger.error(f"Port {port} is already in use. Please free up the port or use a different one.")
            sys.exit(1)
            
        logger.info("Starting ResumeIQ server...")
        logger.info(f"Server will be available at http://localhost:{port}")
        logger.info("Press Ctrl+C to stop the server")
        
        # Run the server with more detailed logging
        uvicorn.run(
            "backend.main:app",
            host="localhost",
            port=port,
            reload=True,
            log_level="debug",  # Changed to debug for more detailed logs
            access_log=True
        )
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        logger.error("Full error details:", exc_info=True)
        sys.exit(1)