// theme_switcher.js - persistent dark/light theme switching

document.addEventListener('DOMContentLoaded', function() {
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    const htmlElement = document.documentElement;

    // Apply the saved theme or default to dark
    const savedTheme = localStorage.getItem('theme') || 'dark';
    applyTheme(savedTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', function() {
            const currentTheme = htmlElement.getAttribute('data-theme') || 'dark';
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            applyTheme(newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }

    function applyTheme(theme) {
        htmlElement.setAttribute('data-theme', theme);
        htmlElement.setAttribute('data-bs-theme', theme);
        const icon = themeToggleBtn ? themeToggleBtn.querySelector('i') : null;
        
        if (icon) {
            if (theme === 'dark') {
                icon.className = 'fas fa-sun';
                themeToggleBtn.title = "Switch to Light Mode";
            } else {
                icon.className = 'fas fa-moon';
                themeToggleBtn.title = "Switch to Dark Mode";
            }
        }
    }
});
