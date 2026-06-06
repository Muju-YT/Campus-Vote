document.addEventListener('DOMContentLoaded', function() {
    // Animation for feature cards and steps
    const animateElements = () => {
        const featureCards = document.querySelectorAll('.feature-card');
        const stepItems = document.querySelectorAll('.step-item');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animated');
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        featureCards.forEach((card, index) => {
            observer.observe(card);
            card.style.transitionDelay = `${index * 100}ms`;
        });

        stepItems.forEach((item, index) => {
            observer.observe(item);
            item.style.transitionDelay = `${index * 150}ms`;
        });
    };

    // Initialize animations
    animateElements();

    // Add hover effect to cards
    document.querySelectorAll('.feature-card').forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-5px)';
        });
        card.addEventListener('mouseleave', () => {
            if (card.classList.contains('animated')) {
                card.style.transform = 'translateY(0)';
            }
        });
    });
});