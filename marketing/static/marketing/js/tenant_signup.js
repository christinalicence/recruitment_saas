/**
 * Handles the loading state and progress bar for tenant creation.
 */
document.addEventListener('DOMContentLoaded', function() {
    const signupForm = document.getElementById('signup-form');
    
    if (signupForm) {
        signupForm.onsubmit = function() {
            const btn = document.getElementById('submit-btn');
            const btnText = document.getElementById('btn-text');
            const spinner = document.getElementById('btn-spinner');
            const progressContainer = document.getElementById('progress-container');
            const progressBar = document.getElementById('signup-progress-bar');
            const statusText = document.getElementById('progress-status');

            // 1. UI Feedback
            btn.disabled = true;
            btnText.innerText = "Setting things up...";
            spinner.classList.remove('d-none');
            progressContainer.classList.remove('d-none');

            // 2. Simulated Progress Animation
            let width = 0;
            const interval = setInterval(function() {
                if (width >= 95) {
                    clearInterval(interval);
                    statusText.innerText = "Almost there! Redirecting to login...";
                } else {
                    // Easing curve: jumps quickly then slows down as it nears 95%
                    width += (100 - width) * 0.08; 
                    progressBar.style.width = width + '%';
                    
                    if (width > 20) statusText.innerText = "Building your secure database...";
                    if (width > 50) statusText.innerText = "Applying branding styles...";
                    if (width > 80) statusText.innerText = "Finalizing account...";
                }
            }, 450);
        };
    }
});