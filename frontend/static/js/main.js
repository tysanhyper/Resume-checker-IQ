// Common utility functions
function showLoading() {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) {
        spinner.style.display = 'flex';
    }
}

function hideLoading() {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) {
        spinner.style.display = 'none';
    }
}

// Form validation
function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('error');
        } else {
            field.classList.remove('error');
        }
    });
    
    return isValid;
}

// Error handling
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    
    document.body.appendChild(errorDiv);
    
    setTimeout(() => {
        errorDiv.remove();
    }, 3000);
}

// Success message
function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.textContent = message;
    
    document.body.appendChild(successDiv);
    
    setTimeout(() => {
        successDiv.remove();
    }, 3000);
}

// Resume upload functionality
function setupResumeUpload() {
    const fileInput = document.getElementById('resume-upload');
    const uploadContainer = document.querySelector('.upload-container');
    
    if (!fileInput || !uploadContainer) return;
    
    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            uploadContainer.innerHTML = `
                <div class="upload-icon">
                    <i class="fas fa-spinner fa-spin" style="color: var(--primary-color)"></i>
                </div>
                <p class="upload-text">Uploading ${this.files[0].name}...</p>
                <p>Please wait while we analyze your resume...</p>
            `;
            
            // Create form data and send to server
            const formData = new FormData();
            formData.append("file", this.files[0]);
            
            fetch("/upload_resume/", {
                method: "POST",
                body: formData,
                headers: {
                    'Accept': 'application/json'
                }
            })
            .then(response => {
                console.log('Response status:', response.status);
                console.log('Response headers:', response.headers);
                if (!response.ok) {
                    return response.text().then(text => {
                        console.error('Error response:', text);
                        throw new Error(`Network response was not ok: ${response.status} ${response.statusText}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    throw new Error(data.error);
                }
                
                // Store the results in localStorage for the results page
                localStorage.setItem('resumeResults', JSON.stringify(data));
                
                // Update UI to show success
                uploadContainer.innerHTML = `
                    <div class="upload-icon">
                        <i class="fas fa-check-circle" style="color: var(--success-color)"></i>
                    </div>
                    <p class="upload-text">${this.files[0].name} analyzed successfully!</p>
                    <p>Your resume analysis is complete.</p>
                    <a href="/results" class="btn" style="margin-top: 15px; display: inline-block;">View Results</a>
                `;
            })
            .catch(error => {
                console.error('Error:', error);
                uploadContainer.innerHTML = `
                    <div class="upload-icon">
                        <i class="fas fa-exclamation-circle" style="color: var(--danger-color)"></i>
                    </div>
                    <p class="upload-text">Error: ${error.message}</p>
                    <p>Please try again or contact support if the problem persists.</p>
                    <button class="btn" onclick="location.reload()">Try Again</button>
                `;
            });
        }
    });

    uploadContainer.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadContainer.style.borderColor = 'var(--primary-color)';
        uploadContainer.style.backgroundColor = 'rgba(67, 97, 238, 0.05)';
    });

    uploadContainer.addEventListener('dragleave', () => {
        uploadContainer.style.borderColor = '#ccc';
        uploadContainer.style.backgroundColor = 'transparent';
    });

    uploadContainer.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadContainer.style.borderColor = '#ccc';
        uploadContainer.style.backgroundColor = 'transparent';
        
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            const event = new Event('change');
            fileInput.dispatchEvent(event);
        }
    });
}

// Legacy upload function (kept for backward compatibility)
async function uploadResume() {
    const fileInput = document.getElementById("upload");
    if (!fileInput || !fileInput.files[0]) return;
    
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    try {
        const response = await fetch("/upload_resume/", {
            method: "POST",
            body: formData,
        });

        const result = await response.json();
        if (result.error) {
            throw new Error(result.error);
        }
        
        // Store results and redirect
        localStorage.setItem('resumeResults', JSON.stringify(result));
        window.location.href = '/results';
    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'Failed to upload resume');
    }
}

// Initialize all functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navLinks = document.querySelector('.nav-links');
    
    if (mobileMenuBtn && navLinks) {
        mobileMenuBtn.addEventListener('click', function() {
            navLinks.style.display = navLinks.style.display === 'flex' ? 'none' : 'flex';
        });
    }
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Setup resume upload functionality
    setupResumeUpload();
    
    // Check for successful sign-in
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('signin') === 'success') {
        // Show success message
        const successMessage = document.createElement('div');
        successMessage.style.position = 'fixed';
        successMessage.style.top = '20px';
        successMessage.style.right = '20px';
        successMessage.style.padding = '15px 25px';
        successMessage.style.background = 'var(--success-color)';
        successMessage.style.color = 'white';
        successMessage.style.borderRadius = 'var(--border-radius)';
        successMessage.style.boxShadow = 'var(--box-shadow)';
        successMessage.style.zIndex = '1000';
        successMessage.style.animation = 'fadeIn 0.3s, fadeOut 0.3s 2.7s forwards';
        successMessage.innerHTML = '<i class="fas fa-check-circle"></i> Successfully signed in!';
        
        document.body.appendChild(successMessage);
        
        // Remove the sign-in parameter from URL
        window.history.replaceState({}, document.title, window.location.pathname);
    }

    // Check authentication status
    const isAuthenticated = localStorage.getItem('isAuthenticated');
    
    if (isAuthenticated) {
        // Update UI for authenticated user
        const nav = document.querySelector('.nav-links');
        if (nav) {
            const userEmail = localStorage.getItem('userEmail');
            nav.innerHTML = `
                <li><a href="#features">Features</a></li>
                <li><a href="#how-it-works">How It Works</a></li>
                <li><a href="dashboard.html">Dashboard</a></li>
                <li>
                    <div class="user-dropdown">
                        <button class="user-btn">
                            <i class="fas fa-user-circle"></i> ${userEmail || 'My Account'}
                            <i class="fas fa-caret-down"></i>
                        </button>
                        <div class="dropdown-content">
                            <a href="dashboard.html"><i class="fas fa-tachometer-alt"></i> Dashboard</a>
                            <a href="profile.html"><i class="fas fa-user"></i> Profile</a>
                            <a href="#" id="signout-btn"><i class="fas fa-sign-out-alt"></i> Sign Out</a>
                        </div>
                    </div>
                </li>
            `;
            
            // Add sign out functionality
            document.getElementById('signout-btn')?.addEventListener('click', function(e) {
                e.preventDefault();
                localStorage.removeItem('isAuthenticated');
                localStorage.removeItem('userEmail');
                window.location.href = 'index.html';
            });
        }
    }
}); 