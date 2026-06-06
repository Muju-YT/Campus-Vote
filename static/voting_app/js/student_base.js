document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    const themeToggle = document.getElementById('themeToggle');
    const mobileBreakpoint = 992;
    let isMobile = window.innerWidth <= mobileBreakpoint;

    // Theme functionality
    function initTheme() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        updateThemeIcon(savedTheme);
    }

    function toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme);
    }

    function updateThemeIcon(theme) {
        const icon = themeToggle.querySelector('i');
        if (theme === 'dark') {
            icon.classList.remove('fa-moon');
            icon.classList.add('fa-sun');
            themeToggle.title = "Switch to Light Mode";
        } else {
            icon.classList.remove('fa-sun');
            icon.classList.add('fa-moon');
            themeToggle.title = "Switch to Dark Mode";
        }
    }

    // Initialize theme (default to light)
    initTheme();

    // Theme toggle event
    themeToggle.addEventListener('click', toggleTheme);

    // Initialize sidebar state
    function initSidebar() {
        if (isMobile) {
            // Mobile - sidebar starts closed
            closeSidebar();
        } else {
            // Desktop - sidebar starts open
            openSidebar();
        }
    }

    // Toggle sidebar function
    function toggleSidebar() {
        if (isMobile) {
            // Mobile behavior - toggle with overlay
            if (sidebar.style.transform === 'translateX(0px)') {
                closeSidebar();
            } else {
                openSidebar();
            }
        }
    }

    // Mobile functions
    function openSidebar() {
        if (isMobile) {
            sidebar.style.transform = 'translateX(0)';
            sidebarOverlay.style.display = 'block';
            document.body.style.overflow = 'hidden';
        } else {
            // Desktop - always visible
            sidebar.style.transform = '';
            sidebarOverlay.style.display = 'none';
            document.body.style.overflow = '';
        }
    }

    function closeSidebar() {
        if (isMobile) {
            sidebar.style.transform = 'translateX(-100%)';
            sidebarOverlay.style.display = 'none';
            document.body.style.overflow = '';
        }
    }

    // Initialize sidebar
    initSidebar();

    // Toggle sidebar on button click
    sidebarToggle.addEventListener('click', toggleSidebar);

    // Close sidebar when clicking overlay on mobile
    sidebarOverlay.addEventListener('click', closeSidebar);

    // Handle window resize
    window.addEventListener('resize', function () {
        const newIsMobile = window.innerWidth <= mobileBreakpoint;

        if (newIsMobile !== isMobile) {
            isMobile = newIsMobile;
            initSidebar();

            // On mobile, ensure toggle button is visible
            if (isMobile) {
                sidebarToggle.style.display = 'flex';
            } else {
                // On desktop, hide toggle button
                sidebarToggle.style.display = 'none';
            }
        }
    });

    // Initialize toggle button visibility
    if (isMobile) {
        sidebarToggle.style.display = 'flex';
    } else {
        sidebarToggle.style.display = 'none';
    }
});