// Initialize the page
document.addEventListener('DOMContentLoaded', function () {
    // Dark mode toggle
    const darkModeToggle = document.getElementById('darkModeToggle');
    darkModeToggle.addEventListener('change', toggleTheme);

    // Sidebar toggle functionality
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const sidebarBackdrop = document.getElementById('sidebarBackdrop');

    sidebarToggle.addEventListener('click', function () {
        toggleSidebar();
    });

    sidebarBackdrop.addEventListener('click', function () {
        toggleSidebar();
    });

    // Close sidebar when clicking on nav links (mobile)
    document.querySelectorAll('.sidebar .nav-link').forEach(link => {
        link.addEventListener('click', function () {
            if (window.innerWidth < 992) {
                toggleSidebar();
            }
        });
    });

    // Check for saved theme preference
    checkThemePreference();

    // Handle window resize
    window.addEventListener('resize', function () {
        if (window.innerWidth >= 992) {
            sidebar.classList.remove('active');
            sidebarBackdrop.classList.remove('active');
        }
    });
});

// Toggle sidebar function
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const sidebarBackdrop = document.getElementById('sidebarBackdrop');

    sidebar.classList.toggle('active');
    sidebarBackdrop.classList.toggle('active');

    // Prevent scrolling when sidebar is open
    if (sidebar.classList.contains('active')) {
        document.body.style.overflow = 'hidden';
    } else {
        document.body.style.overflow = '';
    }
}

// Toggle dark/light theme
function toggleTheme() {
    if (this.checked) {
        document.body.setAttribute('data-bs-theme', 'dark');
        localStorage.setItem('theme', 'dark');
    } else {
        document.body.setAttribute('data-bs-theme', 'light');
        localStorage.setItem('theme', 'light');
    }
}

// Check for saved theme preference
function checkThemePreference() {
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
    if (localStorage.getItem('theme') === 'dark' ||
        (!localStorage.getItem('theme') && prefersDarkScheme.matches)) {
        document.body.setAttribute('data-bs-theme', 'dark');
        document.getElementById('darkModeToggle').checked = true;
    }
}