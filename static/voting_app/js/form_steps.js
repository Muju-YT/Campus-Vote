// form_steps.js - multi-step slide registration form handler

document.addEventListener('DOMContentLoaded', function() {
    const signupForm = document.getElementById('registrationForm');
    if (!signupForm) return;

    const slides = Array.from(document.querySelectorAll('.form-step-slide'));
    const nodes = Array.from(document.querySelectorAll('.signup-step-node'));
    const btnNext = document.getElementById('btnNextStep');
    const btnBack = document.getElementById('btnPrevStep');
    const btnSubmit = document.getElementById('btnSubmitForm');
    
    let currentStep = typeof initialStepIndex !== 'undefined' ? initialStepIndex : 0;

    // Slide transition layout helper
    function updateSteps() {
        slides.forEach((slide, idx) => {
            if (idx === currentStep) {
                slide.classList.add('active');
                slide.style.transform = 'translateX(0)';
            } else if (idx < currentStep) {
                slide.classList.remove('active');
                slide.style.transform = 'translateX(-120%)';
            } else {
                slide.classList.remove('active');
                slide.style.transform = 'translateX(120%)';
            }
        });

        // Update progress indicators
        nodes.forEach((node, idx) => {
            if (idx < currentStep) {
                node.className = 'signup-step-node completed';
                node.innerHTML = '<i class="fas fa-check"></i>';
            } else if (idx === currentStep) {
                node.className = 'signup-step-node active';
                node.innerHTML = idx + 1;
            } else {
                node.className = 'signup-step-node';
                node.innerHTML = idx + 1;
            }
        });

        // Toggle navigation buttons
        if (currentStep === 0) {
            btnBack.style.display = 'none';
            btnNext.style.display = 'inline-block';
            btnSubmit.style.display = 'none';
        } else if (currentStep === slides.length - 1) {
            btnBack.style.display = 'inline-block';
            btnNext.style.display = 'none';
            btnSubmit.style.display = 'inline-block';
        } else {
            btnBack.style.display = 'inline-block';
            btnNext.style.display = 'inline-block';
            btnSubmit.style.display = 'none';
        }
    }

    // Step 1 Validation
    function validateStep1() {
        const fullName = document.getElementById('id_full_name').value.trim();
        const username = document.getElementById('id_username').value.trim();
        const email = document.getElementById('id_email').value.trim();
        const password = document.getElementById('id_password').value;
        const confirmPassword = document.getElementById('id_confirm_password').value;

        if (!fullName || !username || !email || !password || !confirmPassword) {
            alert('Please fill out all credential fields.');
            return false;
        }

        // Email format validation (Regex check)
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            alert('Please enter a valid email address.');
            return false;
        }

        if (password !== confirmPassword) {
            alert('Passwords do not match.');
            return false;
        }

        if (password.length < 8) {
            alert('Password must be at least 8 characters long.');
            return false;
        }

        return true;
    }

    if (btnNext) {
        btnNext.addEventListener('click', function() {
            if (currentStep === 0) {
                if (!validateStep1()) return;
            }
            currentStep = Math.min(currentStep + 1, slides.length - 1);
            updateSteps();
        });
    }

    if (btnBack) {
        btnBack.addEventListener('click', function() {
            currentStep = Math.max(currentStep - 1, 0);
            updateSteps();
        });
    }

    // Initial load
    updateSteps();
});
