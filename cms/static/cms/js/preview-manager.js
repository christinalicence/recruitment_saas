/**
 * Manages the interaction between the Editor Form and the Preview Iframe.
 * Handles instant color updates, text debouncing, and ensures colors save properly.
 */
document.addEventListener('DOMContentLoaded', () => {
    const previewFrame = document.getElementById('preview-frame');
    const syncBtn = document.getElementById('refresh-preview-btn');
    const editorForm = document.getElementById('editor-form');

    if (!previewFrame || !editorForm) return;

    const basePreviewUrl = previewFrame.getAttribute('src');
    
    // Track current color values to ensure they save
    let currentColors = {
        primary: document.getElementById('id_primary_color')?.value || '#1e3a8a',
        secondary: document.getElementById('id_secondary_color')?.value || '#64748b',
        background: document.getElementById('id_background_color')?.value || '#ffffff'
    };

    // --- 1. SYNC PREVIEW BUTTON LOGIC ---
    if (syncBtn) {
        syncBtn.addEventListener('click', (e) => {
            e.preventDefault();
            // Push colors immediately to the frame
            if (previewFrame.contentWindow) {
                const root = previewFrame.contentWindow.document.documentElement;
                root.style.setProperty('--brand-primary', currentColors.primary);
                root.style.setProperty('--brand-secondary', currentColors.secondary);
                root.style.setProperty('--brand-bg', currentColors.background);
            }
            // Trigger a full content refresh
            updateIframeSource();
        });
    }

    // --- 2. INSTANT COLOR & SELECT UPDATES ---
    const instantFields = document.querySelectorAll('input[type="color"], select');
    instantFields.forEach(input => {
        const eventType = input.tagName === 'SELECT' ? 'change' : 'input';
        
        input.addEventListener(eventType, (e) => {
            const value = e.target.value;
            
            if (e.target.type === 'color') {
                let variableName = null;
                let colorKey = null;
                
                if (e.target.id === 'id_primary_color') {
                    variableName = '--brand-primary';
                    colorKey = 'primary';
                }
                if (e.target.id === 'id_secondary_color') {
                    variableName = '--brand-secondary';
                    colorKey = 'secondary';
                }
                if (e.target.id === 'id_background_color') {
                    variableName = '--brand-bg';
                    colorKey = 'background';
                }
                
                // Update tracked color value
                if (colorKey) {
                    currentColors[colorKey] = value;
                }
                
                // Update preview iframe instantly
                if (variableName && previewFrame.contentWindow) {
                    const root = previewFrame.contentWindow.document.documentElement;
                    root.style.setProperty(variableName, value);
                    
                    // Also update theme container if :root override fails
                    const themeContainer = previewFrame.contentWindow.document.querySelector('.agency-site');
                    if (themeContainer) themeContainer.style.setProperty(variableName, value);
                }
            } else {
                // For selects (like template_choice), refresh iframe
                updateIframeSource();
            }
        });
    });

    // --- 3. DEBOUNCED TEXT UPDATES ---
    let timeout = null;
    const textFields = document.querySelectorAll('input[type="text"], textarea');
    textFields.forEach(field => {
        field.addEventListener('input', () => {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                updateIframeSource();
            }, 600); 
        });
    });

    // --- 4. IMAGE UPLOAD PREVIEW ---
    const imageInputs = document.querySelectorAll('input[type="file"]');
    imageInputs.forEach(input => {
        input.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file && file.type.startsWith('image/')) {
                // Brief visual feedback
                const wrapper = document.getElementById('preview-wrapper');
                if (wrapper) {
                    wrapper.style.opacity = '0.7';
                    setTimeout(() => {
                        wrapper.style.opacity = '1';
                        updateIframeSource();
                    }, 500);
                }
            }
        });
    });

    // --- 5. FORM SUBMISSION - ENSURE COLORS ARE SAVED ---
    editorForm.addEventListener('submit', () => {
        // Make absolutely sure color inputs have the current values
        const primaryInput = document.getElementById('id_primary_color');
        const secondaryInput = document.getElementById('id_secondary_color');
        const backgroundInput = document.getElementById('id_background_color');
        
        if (primaryInput) primaryInput.value = currentColors.primary;
        if (secondaryInput) secondaryInput.value = currentColors.secondary;
        if (backgroundInput) backgroundInput.value = currentColors.background;
        
        // Form submits normally after this
    });

    // --- 6. HELPER: RELOAD IFRAME WITH FORM DATA ---
    function updateIframeSource() {
        const formData = new FormData(editorForm);
        
        // Explicitly add current colors to ensure they're in the preview
        formData.set('primary_color', currentColors.primary);
        formData.set('secondary_color', currentColors.secondary);
        formData.set('background_color', currentColors.background);
        
        const params = new URLSearchParams(formData).toString();
        const baseUrl = basePreviewUrl.split('?')[0];
        previewFrame.src = `${baseUrl}?${params}`;
    }
});

/**
 * Changes the preview iframe width based on device selection
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