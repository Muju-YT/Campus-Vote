document.addEventListener('DOMContentLoaded', function() {
    // Password toggle functionality
    function setupPasswordToggle(passwordId, toggleId) {
        const passwordField = document.getElementById(passwordId);
        const toggleIcon = document.getElementById(toggleId);
        
        if (passwordField && toggleIcon) {
            toggleIcon.addEventListener('click', function() {
                if (passwordField.type === 'password') {
                    passwordField.type = 'text';
                    toggleIcon.classList.remove('fa-eye');
                    toggleIcon.classList.add('fa-eye-slash');
                } else {
                    passwordField.type = 'password';
                    toggleIcon.classList.remove('fa-eye-slash');
                    toggleIcon.classList.add('fa-eye');
                }
            });
        }
    }
    
    // Initialize password toggles
    setupPasswordToggle('studentPassword', 'toggleStudentPassword');
    setupPasswordToggle('adminPassword', 'toggleAdminPassword');
});