/**
 * Changes the preview iframe width based on device selection.
 * This is defined OUTSIDE DOMContentLoaded so it is globally accessible to the onclick attributes.
 */
function setPreviewSize(device) {
    const wrapper = document.getElementById('preview-wrapper');
    const devices = ['desktop', 'tablet', 'mobile'];
    if (!wrapper) return;

    // Toggle wrapper classes
    devices.forEach(d => wrapper.classList.remove(`${d}-mode`));
    wrapper.classList.add(`${device}-mode`);
    
    // Toggle button active states
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

    const basePreviewUrl = previewFrame.getAttribute('src');
    
    // Track current color values
    let currentColors = {
        primary: document.getElementById('id_primary_color')?.value || '#1e3a8a',
        secondary: document.getElementById('id_secondary_color')?.value || '#64748b',
        background: document.getElementById('id_background_color')?.value || '#ffffff'
    };

    // --- 1. INSTANT COLOR UPDATES ---
    ['primary', 'secondary', 'background'].forEach(type => {
        const input = document.getElementById(`id_${type}_color`);
        if (input) {
            input.addEventListener('input', (e) => {
                const newColor = e.target.value;
                currentColors[type] = newColor;
                
                // Inject style directly into iframe for zero-lag preview
                if (previewFrame.contentWindow) {
                    const root = previewFrame.contentWindow.document.documentElement;
                    const cssVar = type === 'background' ? '--brand-bg' : `--brand-${type}`;
                    root.style.setProperty(cssVar, newColor);
                }
            });
            
            // Trigger full refresh on change (mouse release) to sync with other logic
            input.addEventListener('change', updateIframeSource);
        }
    });

    // --- 2. DEBOUNCED TEXT UPDATES ---
    let debounceTimer;
    editorForm.querySelectorAll('input[type="text"], textarea').forEach(input => {
        input.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(updateIframeSource, 500);
        });
    });

    // --- 3. TEMPLATE SWITCHER ---
    const templateSelect = document.getElementById('id_template_choice');
    if (templateSelect) {
        templateSelect.addEventListener('change', updateIframeSource);
    }

    // --- 4. HELPER: RELOAD IFRAME WITH FORM DATA ---
    function updateIframeSource() {
        const formData = new FormData(editorForm);
        
        // REMOVE file data to prevent "submit a file" validation errors in preview
        formData.delete('hero_image');
        formData.delete('hero_image-clear');
        formData.delete('team_photo');
        formData.delete('team_photo-clear');
        formData.delete('logo');
        formData.delete('logo-clear');

        // Explicitly ensure current color values are sent
        formData.set('primary_color', currentColors.primary);
        formData.set('secondary_color', currentColors.secondary);
        formData.set('background_color', currentColors.background);
        
        const params = new URLSearchParams(formData).toString();
        const baseUrl = basePreviewUrl.split('?')[0];
        
        previewFrame.src = `${baseUrl}?${params}`;
    }
});


document.addEventListener('DOMContentLoaded', function() {
    // Stats toggle functionality
    const statsToggle = document.getElementById('{{ form.show_stats.id_for_label }}');
    const statsFields = document.getElementById('stats-fields');
    
    if (statsToggle && statsFields) {
        statsToggle.addEventListener('change', function() {
            if (this.checked) {
                statsFields.classList.remove('d-none');
            } else {
                statsFields.classList.add('d-none');
            }
        });
    }
});