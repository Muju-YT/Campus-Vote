// Dark Mode Toggle
const darkModeToggle = document.getElementById('darkModeToggle');
const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');

// Check localStorage for user preference
const currentTheme = localStorage.getItem('theme');
if (currentTheme === 'dark') {
    document.body.setAttribute('data-bs-theme', 'dark');
    darkModeToggle.checked = true;
} else if (currentTheme === 'light') {
    document.body.setAttribute('data-bs-theme', 'light');
    darkModeToggle.checked = false;
} else if (prefersDarkScheme.matches) {
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

// Countdown Timer
function updateCountdown() {
    const endDate = new Date("2023-10-01T23:59:59");
    const now = new Date();
    const diff = endDate - now;

    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((diff % (1000 * 60)) / 1000);

    document.getElementById('countdown').innerHTML =
        `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}
setInterval(updateCountdown, 1000);
updateCountdown();

// Department Chart
document.addEventListener('DOMContentLoaded', function () {
    new Chart(document.getElementById('deptChart'), {
        type: 'doughnut',
        data: {
            labels: ['Computer', 'Commerce', 'Accounting'],
            datasets: [{
                data: [42, 28, 30],
                backgroundColor: [
                    getComputedStyle(document.documentElement).getPropertyValue('--primary-blue'),
                    getComputedStyle(document.documentElement).getPropertyValue('--secondary-blue'),
                    getComputedStyle(document.documentElement).getPropertyValue('--accent-green')
                ]
            }]
        },
        options: {
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        boxWidth: 12,
                        padding: 20,
                        color: getComputedStyle(document.documentElement).getPropertyValue('--text-light')
                    }
                }
            }
        }
    });
});