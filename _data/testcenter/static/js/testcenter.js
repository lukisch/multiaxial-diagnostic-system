/* Diagnostic Testcenter - Client-side utilities */

// Keyboard navigation for test forms
document.addEventListener('keydown', function(e) {
    if (!document.getElementById('testForm')) return;

    // Number keys 0-4 to select response for focused item
    if (e.key >= '0' && e.key <= '9') {
        const active = document.activeElement;
        if (active && active.closest('.test-item')) {
            const card = active.closest('.test-item');
            const radio = card.querySelector(`input[value="${e.key}"]`);
            if (radio) {
                radio.checked = true;
                radio.dispatchEvent(new Event('change', { bubbles: true }));
                // Move to next item
                const nextCard = card.nextElementSibling;
                if (nextCard && nextCard.classList.contains('test-item')) {
                    const firstRadio = nextCard.querySelector('input[type="radio"]');
                    if (firstRadio) firstRadio.focus();
                }
            }
        }
    }
});

// Auto-scroll to next unanswered item after selection
document.addEventListener('change', function(e) {
    if (e.target.type !== 'radio') return;
    const card = e.target.closest('.test-item');
    if (!card) return;

    // Small delay for visual feedback
    setTimeout(function() {
        const nextCard = card.nextElementSibling;
        if (nextCard && nextCard.classList.contains('test-item')) {
            // Check if next item is already answered
            const radios = nextCard.querySelectorAll('input[type="radio"]');
            let answered = false;
            radios.forEach(r => { if (r.checked) answered = true; });
            if (!answered) {
                nextCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
    }, 150);
});
