// Dark Mode Toggle
const darkModeToggle = document.getElementById('darkModeToggle');
const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');

// Check for saved user preference or system preference
if (localStorage.getItem('theme') === 'dark' ||
    (!localStorage.getItem('theme') && prefersDarkScheme.matches)) {
    document.body.setAttribute('data-bs-theme', 'dark');
    darkModeToggle.checked = true;
}

// Toggle dark mode
darkModeToggle.addEventListener('change', function () {
    if (this.checked) {
        document.body.setAttribute('data-bs-theme', 'dark');
        localStorage.setItem('theme', 'dark');
    } else {
        document.body.setAttribute('data-bs-theme', 'light');
        localStorage.setItem('theme', 'light');
    }
});

// Sidebar Toggle for Mobile
document.getElementById('sidebarToggle').addEventListener('click', function () {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('active');

    // Add backdrop when sidebar is active
    if (sidebar.classList.contains('active')) {
        createBackdrop();
    } else {
        removeBackdrop();
    }
});

// Create backdrop function
function createBackdrop() {
    const backdrop = document.createElement('div');
    backdrop.id = 'sidebarBackdrop';
    backdrop.className = 'offcanvas-backdrop fade show';
    backdrop.style.zIndex = '999';
    document.body.appendChild(backdrop);

    // Close sidebar when clicking on backdrop
    backdrop.addEventListener('click', function () {
        document.getElementById('sidebar').classList.remove('active');
        removeBackdrop();
    });
}

// Remove backdrop function
function removeBackdrop() {
    const backdrop = document.getElementById('sidebarBackdrop');
    if (backdrop) {
        backdrop.remove();
    }
}

// Close sidebar when clicking on nav links (optional)
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', function () {
        if (window.innerWidth < 992) {
            document.getElementById('sidebar').classList.remove('active');
            removeBackdrop();
        }
    });
});

// Countdown Timer
function updateCountdown() {
    const endDate = new Date("2023-10-01T23:59:59");
    const now = new Date();
    const diff = endDate - now;

    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));

    document.getElementById('countdown').innerHTML = `${days}d ${hours}h`;
}
setInterval(updateCountdown, 3600000); // Update every hour
updateCountdown();

// Chart.js Implementation
document.addEventListener('DOMContentLoaded', function () {
    // Participation Chart
    const ctx = document.getElementById('participationChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Computer Science', 'Commerce', 'Accounting'],
            datasets: [{
                label: 'Voted Students',
                data: [420, 380, 224],
                backgroundColor: [
                    'rgba(67, 97, 238, 0.7)',
                    'rgba(67, 97, 238, 0.7)',
                    'rgba(67, 97, 238, 0.7)'
                ],
                borderColor: [
                    'rgba(67, 97, 238, 1)',
                    'rgba(67, 97, 238, 1)',
                    'rgba(67, 97, 238, 1)'
                ],
                borderWidth: 1
            }, {
                label: 'Total Students',
                data: [642, 720, 480],
                backgroundColor: [
                    'rgba(201, 203, 207, 0.7)',
                    'rgba(201, 203, 207, 0.7)',
                    'rgba(201, 203, 207, 0.7)'
                ],
                borderColor: [
                    'rgba(201, 203, 207, 1)',
                    'rgba(201, 203, 207, 1)',
                    'rgba(201, 203, 207, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: getComputedStyle(document.documentElement).getPropertyValue('--text-color')
                    },
                    grid: {
                        color: getComputedStyle(document.documentElement).getPropertyValue('--border-color')
                    }
                },
                x: {
                    ticks: {
                        color: getComputedStyle(document.documentElement).getPropertyValue('--text-color')
                    },
                    grid: {
                        color: getComputedStyle(document.documentElement).getPropertyValue('--border-color')
                    }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        color: getComputedStyle(document.documentElement).getPropertyValue('--text-color')
                    }
                }
            }
        }
    });
});