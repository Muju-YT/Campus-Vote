// Initialize DataTable
$(document).ready(function () {
    var table = $('#studentsTable').DataTable({
        responsive: true,
        dom: '<"top"f>rt<"bottom"lip><"clear">',
        language: {
            search: "_INPUT_",
            searchPlaceholder: "Search students...",
            lengthMenu: "Show _MENU_ students per page",
            info: "Showing _START_ to _END_ of _TOTAL_ students",
            infoEmpty: "No students found",
            infoFiltered: "(filtered from _MAX_ total students)"
        }
    });

    // Search input handler
    $('#searchInput').keyup(function () {
        table.search($(this).val()).draw();
    });

    // Department filter handler
    $('#departmentFilter').change(function () {
        var department = $(this).val();
        if (department) {
            table.column(2).search('^' + department + '$', true, false).draw();
        } else {
            table.column(2).search('').draw();
        }
    });

    // Dark mode toggle
    const darkModeToggle = document.getElementById('darkModeToggle');
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');

    if (localStorage.getItem('theme') === 'dark' ||
        (!localStorage.getItem('theme') && prefersDarkScheme.matches)) {
        document.body.setAttribute('data-bs-theme', 'dark');
        darkModeToggle.checked = true;
    }

    darkModeToggle.addEventListener('change', function () {
        if (this.checked) {
            document.body.setAttribute('data-bs-theme', 'dark');
            localStorage.setItem('theme', 'dark');
        } else {
            document.body.setAttribute('data-bs-theme', 'light');
            localStorage.setItem('theme', 'light');
        }
    });

    // Form submission handlers
    $('#addStudentForm').submit(function (e) {
        e.preventDefault();
        // Add your form submission logic here
        alert('Student added successfully!');
        $('#addStudentModal').modal('hide');
        this.reset();
    });

    $('#uploadCSVForm').submit(function (e) {
        e.preventDefault();
        // Add your CSV upload logic here
        alert('CSV uploaded successfully!');
        $('#uploadCSVModal').modal('hide');
        this.reset();
    });
});