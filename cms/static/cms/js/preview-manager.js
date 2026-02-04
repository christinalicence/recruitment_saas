/**
 * Changes the preview iframe width based on device selection.
 * Defined outside DOMContentLoaded for global access by onclick attributes.
 */
function setPreviewSize(device) {
    const wrapper = document.getElementById('preview-wrapper');
    const devices = ['desktop', 'tablet', 'mobile'];
    if (!wrapper) return;

    devices.forEach(d => wrapper.classList.remove(`${d}-mode`));
    wrapper.classList.add(`${device}-mode`);
    
    devices.forEach(d => {
        const btn = document.getElementById(`btn-${d}`);
        if (btn) {
            btn.classList.toggle('active', d === device);
            btn.classList.toggle('btn-primary', d === device);
            btn.classList.toggle('btn-outline-secondary', d !== device);
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const previewFrame = document.getElementById('preview-frame');
    const editorForm = document.getElementById('editor-form');

    if (!previewFrame || !editorForm) return;

    // --- 1. INSTANT COLOR & CONTENT PREVIEW ---
    
    // Track current values to send to the iframe
    let currentColors = {
        primary: document.getElementById('id_primary_color')?.value || '#1e3a8a',
        secondary: document.getElementById('id_secondary_color')?.value || '#64748b',
        background: document.getElementById('id_background_color')?.value || '#ffffff'
    };

    const updateIframe = () => {
        if (previewFrame.contentWindow) {
            // Send message to iframe to update styles without a full reload
            previewFrame.contentWindow.postMessage({
                type: 'updateStyles',
                colors: currentColors
            }, '*');
        }
    };

    // Listen for color input changes
    ['primary', 'secondary', 'background'].forEach(type => {
        const input = document.getElementById(`id_${type}_color`);
        if (input) {
            input.addEventListener('input', (e) => {
                currentColors[type] = e.target.value;
                updateIframe();
                
                // If the contrast checker script is loaded, trigger it
                if (window.updateContrastUI) {
                    window.updateContrastUI(currentColors.primary, currentColors.background);
                }
            });
        }
    });

    // --- 2. CHARACTER COUNTERS WITH MULTIPLE LIMITS ---

    const trackedFields = document.querySelectorAll('input[type="text"], textarea');

    trackedFields.forEach(field => {
        const counter = document.querySelector(`.char-count[data-for="${field.id}"]`);
        
        if (counter) {
            const updateCount = () => {
                const currentLength = field.value.length;
                let maxLength = 200; // Default limit
                
                // Apply specific limits based on field ID
                if (field.id.includes('about_title')) {
                    maxLength = 100;
                } else if (field.id.includes('about_content')) {
                    maxLength = 600;
                } else if (field.id.includes('jobs_header_text')) {
                    maxLength = 150;
                }

                counter.innerText = `${currentLength} / ${maxLength}`;
                
                // Visual feedback if over limit
                if (currentLength > maxLength) {
                    counter.classList.add('text-danger');
                    counter.classList.remove('text-muted');
                } else {
                    counter.classList.remove('text-danger');
                    counter.classList.add('text-muted');
                }
            };

            // Run on load and on every keystroke
            updateCount();
            field.addEventListener('input', updateCount);
        }
    });

    // --- 3. SMART SCROLLING ---

    // Automatically scroll the editor to the right section when navigating the preview
    previewFrame.onload = function() {
        try {
            const path = previewFrame.contentWindow.location.pathname;
            
            if (path.includes('/about/')) {
                const aboutSection = document.querySelector('[data-section="about"]');
                if (aboutSection) aboutSection.scrollIntoView({ behavior: 'smooth' });
            } else if (path.includes('/jobs/')) {
                const jobsSection = document.querySelector('[data-section="jobs"]');
                if (jobsSection) jobsSection.scrollIntoView({ behavior: 'smooth' });
            }
        } catch (e) {
            console.log("Cross-origin preview prevented scroll-sync");
        }
    };
});