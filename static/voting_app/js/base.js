// home.js - Theme Toggle Functionality

document.addEventListener('DOMContentLoaded', function() {
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    const htmlElement = document.documentElement;
    const themeIconLight = document.querySelector('.theme-icon-light');
    const themeIconDark = document.querySelector('.theme-icon-dark');
    
    // Check for saved theme preference or use preferred color scheme
    const savedTheme = localStorage.getItem('theme') || 
                      (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    
    // Apply the saved theme with animation
    applyTheme(savedTheme, false);
    
    // Toggle theme when button is clicked
    themeToggleBtn.addEventListener('click', function() {
        const currentTheme = htmlElement.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        // Add click animation
        this.classList.add('clicked');
        setTimeout(() => this.classList.remove('clicked'), 300);
        
        applyTheme(newTheme, true);
        localStorage.setItem('theme', newTheme);
        
        // Dispatch event for other components
        document.dispatchEvent(new CustomEvent('themeChanged', { detail: newTheme }));
    });
    
    // Watch for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
        if (!localStorage.getItem('theme')) {
            const newTheme = e.matches ? 'dark' : 'light';
            applyTheme(newTheme, true);
        }
    });
    
    function applyTheme(theme, animate) {
        // Set theme attribute
        htmlElement.setAttribute('data-bs-theme', theme);
        
        // Animate the toggle
        if (animate) {
            themeToggleBtn.style.transform = 'scale(0.8)';
            setTimeout(() => {
                themeToggleBtn.style.transform = 'scale(1.1)';
                setTimeout(() => {
                    themeToggleBtn.style.transform = 'scale(1)';
                }, 100);
            }, 100);
        }
        
        // Update icons
        if (theme === 'dark') {
            themeToggleBtn.classList.remove('btn-outline-light');
            themeToggleBtn.classList.add('btn-outline-warning');
            
            themeIconLight.classList.add('fade-out');
            themeIconLight.classList.remove('fade-in');
            setTimeout(() => {
                themeIconLight.classList.add('d-none');
                themeIconDark.classList.remove('d-none');
                themeIconDark.classList.add('fade-in');
                themeIconDark.classList.remove('fade-out');
            }, 150);
        } else {
            themeToggleBtn.classList.remove('btn-outline-warning');
            themeToggleBtn.classList.add('btn-outline-light');
            
            themeIconDark.classList.add('fade-out');
            themeIconDark.classList.remove('fade-in');
            setTimeout(() => {
                themeIconDark.classList.add('d-none');
                themeIconLight.classList.remove('d-none');
                themeIconLight.classList.add('fade-in');
                themeIconLight.classList.remove('fade-out');
            }, 150);
        }
        
        // Update pulse animation color
        if (theme === 'dark') {
            themeToggleBtn.style.setProperty('--pulse-color', 'rgba(255, 193, 7, 0.5)');
        } else {
            themeToggleBtn.style.setProperty('--pulse-color', 'rgba(248, 249, 250, 0.5)');
        }
    }
    
    // Add animation to theme toggle on page load
    setTimeout(() => {
        themeToggleBtn.classList.add('animate__animated', 'animate__pulse');
    }, 1000);
});