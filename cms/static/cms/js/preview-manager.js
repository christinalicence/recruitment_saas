/**
 * Manages the interaction between the Editor Form and the Preview Iframe.
 */
document.addEventListener('DOMContentLoaded', () => {
    const previewFrame = document.getElementById('preview-frame');
    const syncBtn = document.getElementById('refresh-preview-btn');
    const editorForm = document.getElementById('editor-form');

    if (!previewFrame || !editorForm) return;

    const basePreviewUrl = previewFrame.getAttribute('src');

    // --- 1. SYNC PREVIEW BUTTON LOGIC ---
    if (syncBtn) {
        syncBtn.addEventListener('click', () => {
            // Push colors immediately to the frame
            if (previewFrame.contentWindow) {
                const root = previewFrame.contentWindow.document.documentElement;
                root.style.setProperty('--brand-primary', document.getElementById('id_primary_color').value);
                root.style.setProperty('--brand-secondary', document.getElementById('id_secondary_color').value);
                root.style.setProperty('--brand-bg', document.getElementById('id_background_color').value);
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
                if (e.target.id === 'id_primary_color') variableName = '--brand-primary';
                if (e.target.id === 'id_secondary_color') variableName = '--brand-secondary';
                if (e.target.id === 'id_background_color') variableName = '--brand-bg';
                
                if (variableName && previewFrame.contentWindow) {
                    const root = previewFrame.contentWindow.document.documentElement;
                    root.style.setProperty(variableName, value);
                    
                    // Also check for the specific theme container if :root override fails
                    const themeContainer = previewFrame.contentWindow.document.querySelector('.agency-site');
                    if (themeContainer) themeContainer.style.setProperty(variableName, value);
                }
            } else {
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

    // --- 4. HELPER: RELOAD IFRAME WITH FORM DATA ---
    function updateIframeSource() {
        const formData = new FormData(editorForm);
        const params = new URLSearchParams(formData).toString();
        // Clear old params and add new ones
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