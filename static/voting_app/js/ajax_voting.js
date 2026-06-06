// ajax_voting.js - asynchronous AJAX Fetch API voting engine

document.addEventListener('DOMContentLoaded', function() {
    const voteForm = document.getElementById('voteForm');
    if (!voteForm) return;

    voteForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const electionId = document.getElementById('formElectionId').value;
        const candidateId = document.getElementById('formCandidateId').value;
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        if (!electionId || !candidateId) {
            showToast('Ballot error: missing parameters.', 'error');
            return;
        }

        // Disable confirm buttons
        const submitBtn = voteForm.querySelector('[type=submit]');
        const cancelBtn = voteForm.querySelector('[type=button]');
        submitBtn.disabled = true;
        cancelBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Recording...';

        // Post AJAX vote choice to server Fetch API
        fetch(voteForm.action, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({
                election_id: electionId,
                candidate_id: candidateId
            })
        })
        .then(response => response.json().then(data => ({ status: response.status, body: data })))
        .then(result => {
            if (result.status === 200 && result.body.success) {
                // Close confirmation modal
                bootstrap.Modal.getInstance(document.getElementById('confirmVoteModal')).hide();
                
                // Show dynamic success overlay screen
                showVoteSuccessScreen(result.body.receipt);
            } else {
                // Re-enable confirm controls
                submitBtn.disabled = false;
                cancelBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-check-double me-1"></i> Confirm & Vote';
                
                showToast(result.body.message || 'Ballot failed. Try again.', 'error');
            }
        })
        .catch(err => {
            submitBtn.disabled = false;
            cancelBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-check-double me-1"></i> Confirm & Vote';
            
            showToast('Network error processing ballot request.', 'error');
        });
    });

    // Triggers full screen GSAP success check animation
    function showVoteSuccessScreen(receiptHash) {
        // Create full screen success overlay dynamically
        const overlay = document.createElement('div');
        overlay.className = 'vote-success-overlay';
        overlay.innerHTML = `
            <div class="text-center p-5 rounded-4 glass-card shadow" style="max-width: 450px; background: rgba(11, 15, 25, 0.95);">
                <div class="success-icon-box text-success mx-auto mb-4">
                    <i class="fas fa-check-double fa-3x animate-check"></i>
                </div>
                <h3 class="fw-bold text-white mb-2">Ballot Cast Successfully!</h3>
                <p class="text-secondary small mb-4">Your vote has been cryptographically signed and compiled in the college registry.</p>
                <div class="p-3 bg-dark rounded border text-start mb-4">
                    <small class="text-muted font-monospace d-block text-uppercase" style="font-size: 0.65rem;">Voter Receipt Hash</small>
                    <code class="text-primary small font-monospace text-break">${receiptHash}</code>
                </div>
                <button class="btn-premium w-100 py-3" id="btnSuccessClose">Done <i class="fas fa-arrow-right ms-2"></i></button>
            </div>
        `;
        document.body.appendChild(overlay);

        // GSAP success fade in
        gsap.fromTo(overlay, { opacity: 0 }, { opacity: 1, duration: 0.4, ease: 'power2.out' });
        gsap.fromTo('.success-icon-box', { scale: 0.5, opacity: 0 }, { scale: 1.1, opacity: 1, delay: 0.2, duration: 0.5, ease: 'back.out' });
        
        document.getElementById('btnSuccessClose').addEventListener('click', function() {
            gsap.to(overlay, { 
                opacity: 0, 
                duration: 0.3, 
                onComplete: () => {
                    overlay.remove();
                    window.location.href = '/student/vote-status/';
                } 
            });
        });
    }

    // Helper toast alerts
    function showToast(message, type) {
        const toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) return;

        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : 'success'} border-0 show`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas ${type === 'error' ? 'fa-exclamation-triangle' : 'fa-check-circle'} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        toastContainer.appendChild(toast);
        setTimeout(() => {
            gsap.to(toast, { opacity: 0, duration: 0.3, onComplete: () => toast.remove() });
        }, 4000);
    }
});
