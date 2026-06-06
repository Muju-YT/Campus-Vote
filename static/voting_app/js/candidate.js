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

// Sidebar Toggle
document.getElementById('sidebarToggle').addEventListener('click', function () {
    document.getElementById('sidebar').classList.toggle('active');
});

// Photo preview functionality
document.getElementById('photoUpload').addEventListener('change', function (e) {
    const preview = document.getElementById('photoPreview');
    const file = e.target.files[0];
    const reader = new FileReader();

    reader.onload = function (e) {
        preview.src = e.target.result;
        preview.style.display = 'block';
    }

    if (file) {
        reader.readAsDataURL(file);
    } else {
        preview.style.display = 'none';
    }
});

// Save candidate (dummy functionality)
document.getElementById('saveCandidate').addEventListener('click', function () {
    const fullName = document.getElementById('fullName').value;
    const department = document.getElementById('department').value;
    const position = document.getElementById('position').value;
    const photoUpload = document.getElementById('photoUpload');

    if (!fullName || !department || !position) {
        alert('Please fill in all required fields');
        return;
    }

    // Create a new table row
    const tbody = document.getElementById('candidatesTableBody');
    const newRow = document.createElement('tr');

    // Default photo or uploaded photo
    let photoSrc = 'https://randomuser.me/api/portraits/lego/1.jpg'; // Default
    if (photoUpload.files && photoUpload.files[0]) {
        photoSrc = URL.createObjectURL(photoUpload.files[0]);
    }

    newRow.innerHTML = `
                <td><img src="${photoSrc}" class="candidate-photo" alt="${fullName}"></td>
                <td>${fullName}</td>
                <td>${department}</td>
                <td>${position}</td>
                <td class="action-buttons">
                    <button class="btn btn-sm btn-warning edit-btn"><i class="bi bi-pencil"></i> Edit</button>
                    <button class="btn btn-sm btn-danger delete-btn"><i class="bi bi-trash"></i> Delete</button>
                </td>
            `;

    tbody.appendChild(newRow);

    // Reset form and close modal
    document.getElementById('candidateForm').reset();
    document.getElementById('photoPreview').style.display = 'none';
    bootstrap.Modal.getInstance(document.getElementById('addCandidateModal')).hide();

    // Show alert (could be replaced with a toast notification)
    alert('Candidate added successfully!');

    // Add event listeners to the new buttons
    addButtonEventListeners();
});

// Add event listeners to all delete buttons
function addButtonEventListeners() {
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            if (confirm('Are you sure you want to delete this candidate?')) {
                this.closest('tr').remove();
                alert('Candidate deleted successfully!');
            }
        });
    });

    document.querySelectorAll('.edit-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            alert('Edit functionality would go here');
        });
    });
}

// Initialize event listeners for existing buttons
document.addEventListener('DOMContentLoaded', function () {
    addButtonEventListeners();
});