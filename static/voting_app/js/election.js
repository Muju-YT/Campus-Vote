// Sample election data
let elections = [
    {
        id: 1,
        title: "Student Union Election 2023",
        startDate: "2023-10-15T08:00",
        endDate: "2023-10-17T20:00",
        description: "Annual election for student union representatives",
        active: true
    },
    {
        id: 2,
        title: "Department Representatives",
        startDate: "2023-11-01T09:00",
        endDate: "2023-11-03T18:00",
        description: "Election for department student representatives",
        active: false
    },
    {
        id: 3,
        title: "Sports Committee Election",
        startDate: "2023-09-05T10:00",
        endDate: "2023-09-07T16:00",
        description: "Selection of sports committee members",
        active: false
    }
];

// DOM Elements
const electionsTableBody = document.getElementById('electionsTableBody');
const emptyState = document.getElementById('emptyState');
const searchInput = document.getElementById('searchInput');
const statusFilter = document.getElementById('statusFilter');
const resetFilters = document.getElementById('resetFilters');
const darkModeToggle = document.getElementById('darkModeToggle');
const saveElectionBtn = document.getElementById('saveElection');
const sidebarToggle = document.getElementById('sidebarToggle');
const sidebar = document.getElementById('sidebar');
const sidebarBackdrop = document.getElementById('sidebarBackdrop');

// Initialize the page
document.addEventListener('DOMContentLoaded', function () {
    renderElections();
    setupEventListeners();
    checkEmptyState();
    checkThemePreference();
});

// Render elections table
function renderElections(filteredElections = null) {
    electionsTableBody.innerHTML = '';

    const electionsToRender = filteredElections || elections;

    if (electionsToRender.length === 0) {
        emptyState.style.display = 'block';
        electionsTableBody.closest('.card').style.display = 'none';
        return;
    }

    emptyState.style.display = 'none';
    electionsTableBody.closest('.card').style.display = 'block';

    electionsToRender.forEach(election => {
        const row = document.createElement('tr');
        row.innerHTML = `
                    <td class="align-middle">${election.title}</td>
                    <td class="align-middle">${formatDateTime(election.startDate)}</td>
                    <td class="align-middle">${formatDateTime(election.endDate)}</td>
                    <td class="align-middle">
                        <span class="badge badge-status ${election.active ? 'badge-active' : 'badge-inactive'}">
                            <i class="bi ${election.active ? 'bi-check-circle-fill' : 'bi-pause-fill'} me-1"></i>
                            ${election.active ? 'Active' : 'Inactive'}
                        </span>
                    </td>
                    <td class="align-middle text-end">
                        <div class="d-flex justify-content-end">
                            <button class="btn-action btn ${election.active ? 'btn-warning' : 'btn-success'} me-2 toggle-btn" 
                                    data-id="${election.id}" title="${election.active ? 'Deactivate' : 'Activate'}">
                                <i class="bi ${election.active ? 'bi-pause-fill' : 'bi-play-fill'}"></i>
                            </button>
                            <button class="btn-action btn btn-danger delete-btn" data-id="${election.id}" title="Delete">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                    </td>
                `;
        electionsTableBody.appendChild(row);
    });

    // Add event listeners to the new buttons
    addButtonEventListeners();
}

// Setup event listeners
function setupEventListeners() {
    // Dark mode toggle
    darkModeToggle.addEventListener('change', toggleTheme);

    // Sidebar toggle with backdrop
    sidebarToggle.addEventListener('click', toggleSidebar);

    // Close sidebar when clicking on backdrop
    sidebarBackdrop.addEventListener('click', closeSidebar);

    // Close sidebar when clicking on nav links (mobile)
    document.querySelectorAll('.sidebar .nav-link').forEach(link => {
        link.addEventListener('click', function () {
            if (window.innerWidth < 992) {
                closeSidebar();
            }
        });
    });

    // Search and filter
    searchInput.addEventListener('input', filterElections);
    statusFilter.addEventListener('change', filterElections);
    resetFilters.addEventListener('click', resetFiltersHandler);

    // Save new election
    saveElectionBtn.addEventListener('click', saveElection);
}

// Toggle sidebar function
function toggleSidebar() {
    sidebar.classList.toggle('active');
    sidebarBackdrop.classList.toggle('active');

    // Prevent scrolling when sidebar is open
    if (sidebar.classList.contains('active')) {
        document.body.style.overflow = 'hidden';
    } else {
        document.body.style.overflow = '';
    }
}

// Close sidebar function
function closeSidebar() {
    sidebar.classList.remove('active');
    sidebarBackdrop.classList.remove('active');
    document.body.style.overflow = '';
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
        darkModeToggle.checked = true;
    }
}

// Format date for display
function formatDateTime(dateTimeString) {
    const options = {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return new Date(dateTimeString).toLocaleDateString('en-US', options);
}

// Filter elections based on search and filters
function filterElections() {
    const searchTerm = searchInput.value.toLowerCase();
    const status = statusFilter.value;

    const filtered = elections.filter(election => {
        const matchesSearch = election.title.toLowerCase().includes(searchTerm);
        const matchesStatus = status === '' ||
            (status === 'active' && election.active) ||
            (status === 'inactive' && !election.active);

        return matchesSearch && matchesStatus;
    });

    renderElections(filtered);
    checkEmptyState(filtered);
}

// Reset all filters
function resetFiltersHandler() {
    searchInput.value = '';
    statusFilter.value = '';
    renderElections();
    checkEmptyState();
}

// Check if we should show the empty state
function checkEmptyState(filteredElections = null) {
    const electionsToCheck = filteredElections || elections;
    if (electionsToCheck.length === 0) {
        emptyState.style.display = 'block';
        electionsTableBody.closest('.card').style.display = 'none';
    } else {
        emptyState.style.display = 'none';
        electionsTableBody.closest('.card').style.display = 'block';
    }
}

// Save new election
function saveElection() {
    const title = document.getElementById('electionTitle').value;
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    const description = document.getElementById('electionDescription').value;
    const activate = document.getElementById('activateElection').checked;

    if (!title || !startDate || !endDate) {
        showAlert('Please fill in all required fields', 'danger');
        return;
    }

    if (new Date(startDate) >= new Date(endDate)) {
        showAlert('End date must be after start date', 'danger');
        return;
    }

    const newElection = {
        id: Date.now(), // Simple unique ID
        title,
        startDate,
        endDate,
        description,
        active: activate
    };

    elections.push(newElection);
    renderElections();
    checkEmptyState();

    // Reset form and close modal
    document.getElementById('electionForm').reset();
    bootstrap.Modal.getInstance(document.getElementById('addElectionModal')).hide();

    // Show success message
    showAlert('Election added successfully!', 'success');
}

// Add event listeners to all buttons
function addButtonEventListeners() {
    document.querySelectorAll('.toggle-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const id = parseInt(this.dataset.id);
            const election = elections.find(e => e.id === id);

            if (election) {
                election.active = !election.active;
                renderElections();
                showAlert(`Election ${election.active ? 'activated' : 'deactivated'} successfully!`, 'info');
            }
        });
    });

    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const id = parseInt(this.dataset.id);
            if (confirm('Are you sure you want to delete this election?')) {
                elections = elections.filter(e => e.id !== id);
                renderElections();
                checkEmptyState();
                showAlert('Election deleted successfully!', 'danger');
            }
        });
    });
}

// Show alert message
function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
    alertDiv.setAttribute('role', 'alert');
    alertDiv.innerHTML = `
                <div class="d-flex align-items-center">
                    <i class="bi ${type === 'success' ? 'bi-check-circle-fill' : type === 'danger' ? 'bi-exclamation-triangle-fill' : 'bi-info-circle-fill'} me-2"></i>
                    <div>${message}</div>
                    <button type="button" class="btn-close ms-auto" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>
            `;

    document.body.appendChild(alertDiv);

    // Auto-remove after 3 seconds
    setTimeout(() => {
        alertDiv.classList.remove('show');
        setTimeout(() => alertDiv.remove(), 150);
    }, 3000);
}