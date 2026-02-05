/**
 * Changes the preview iframe width based on device selection.
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

    // --- 1. INSTANT COLOR PREVIEW ---
    let currentColors = {
        primary: document.getElementById('id_primary_color')?.value || '#1e3a8a',
        secondary: document.getElementById('id_secondary_color')?.value || '#64748b',
        background: document.getElementById('id_background_color')?.value || '#ffffff'
    };

    const updateIframe = () => {
        if (previewFrame.contentWindow) {
            previewFrame.contentWindow.postMessage({
                type: 'updateStyles',
                colors: currentColors
            }, '*');
        }
    };

    ['primary', 'secondary', 'background'].forEach(type => {
        const input = document.getElementById(`id_${type}_color`);
        if (input) {
            input.addEventListener('input', (e) => {
                currentColors[type] = e.target.value;
                updateIframe();
            });
        }
    });

    // --- 2. CHARACTER COUNTERS ---
    const trackedFields = document.querySelectorAll('input[type="text"], textarea');
    trackedFields.forEach(field => {
        const counter = document.querySelector(`.char-count[data-for="${field.id}"]`);
        if (counter) {
            const updateCount = () => {
                const currentLength = field.value.length;
                let maxLength = field.id.includes('about_content') ? 600 : 
                               field.id.includes('about_title') ? 100 : 
                               field.id.includes('jobs_header_text') ? 150 : 200;

                counter.innerText = `${currentLength} / ${maxLength}`;
                counter.classList.toggle('text-danger', currentLength > maxLength);
            };
            updateCount();
            field.addEventListener('input', updateCount);
        }
    });

    // --- 3. TOAST NOTIFICATIONS ---
    const toastEl = document.getElementById('messageToast');
    const toastMsgEl = document.getElementById('toastMessage');
    if (toastEl && toastMsgEl && toastMsgEl.innerText.trim() !== "" && window.bootstrap) {
        const toast = new bootstrap.Toast(toastEl, { delay: 4000 });
        toast.show();
    }

    // --- 4. SMART SCROLLING (Fixed & Moved Inside) ---
    previewFrame.onload = function() {
        try {
            const path = previewFrame.contentWindow.location.pathname;
            let targetSection = null;

            if (path.includes('/about/')) {
                targetSection = document.querySelector('[data-section="about"]');
            } else if (path.includes('/jobs/') || path.includes('/apply/')) {
                targetSection = document.querySelector('[data-section="jobs"]');
            }

            if (targetSection) {
                targetSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                
                // Optional: Add a brief "glow" effect so the user sees which section changed
                targetSection.style.backgroundColor = '#fff3cd';
                setTimeout(() => {
                    targetSection.style.transition = 'background-color 1s ease';
                    targetSection.style.backgroundColor = 'transparent';
                }, 500);
            }
        } catch (e) {
            console.log("Navigation sync paused: External link.");
        }
    };
});

// Function to update the sidebar thumbnails instantly when a file is chosen
const setupImagePreview = (inputId, previewId) => {
    const input = document.getElementById(inputId);
    const preview = document.getElementById(previewId);
    
    // Check for specific fallbacks we might want to hide
    const textFallback = document.getElementById('logo-text-fallback');
    const heroPlaceholder = document.getElementById('hero-placeholder-text');

    if (input && preview) {
        input.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    preview.src = e.target.result;
                    preview.classList.remove('d-none'); // Show the image if it was hidden
                    
                    // Hide the text placeholders
                    if (textFallback) textFallback.style.display = 'none';
                    if (heroPlaceholder) heroPlaceholder.style.display = 'none';
                };
                reader.readAsDataURL(file);
            }
        });
    }
};

// Initialize the logic for your three image fields
document.addEventListener('DOMContentLoaded', () => {
    setupImagePreview('id_logo', 'logo-preview');
    setupImagePreview('id_hero_image', 'id_hero_image-preview');
    setupImagePreview('id_team_photo', 'team_photo-preview');
});

// --- INSTANT THEME PREVIEW ---
const themeRadios = document.querySelectorAll('input[name="template_choice"]');
themeRadios.forEach(radio => {
    radio.addEventListener('change', (e) => {
        if (previewFrame.contentWindow) {
            previewFrame.contentWindow.postMessage({
                type: 'updateTheme',
                theme: e.target.value
            }, '*');
        }
    });
});