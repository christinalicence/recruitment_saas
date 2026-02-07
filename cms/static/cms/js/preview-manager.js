/**
 * Changes the preview iframe width based on device selection.
 */
function setPreviewSize(size) {
    const wrapper = document.getElementById('preview-wrapper');
    const buttons = {
        'desktop': document.getElementById('btn-desktop'),
        'tablet': document.getElementById('btn-tablet'),
        'mobile': document.getElementById('btn-mobile')
    };
    
    if (!wrapper) return;

    wrapper.classList.remove('desktop-mode', 'tablet-mode', 'mobile-mode');
    wrapper.classList.add(size + '-mode');

    Object.values(buttons).forEach(btn => {
        if (btn) btn.classList.replace('btn-secondary', 'btn-outline-secondary');
    });

    if (buttons[size]) {
        buttons[size].classList.replace('btn-outline-secondary', 'btn-secondary');
    }
}

/**
 * Handles instant local thumbnail updates
 */
const setupImagePreview = (inputId, previewId, fallbackId) => {
    const input = document.getElementById(inputId);
    const preview = document.getElementById(previewId);
    const fallback = document.getElementById(fallbackId);

    if (input && preview) {
        input.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    preview.src = e.target.result;
                    preview.classList.remove('d-none');
                    if (fallback) fallback.classList.add('d-none');
                };
                reader.readAsDataURL(file);
            }
        });
    }
};

document.addEventListener('DOMContentLoaded', () => {
    const previewFrame = document.getElementById('preview-frame');
    
    // 1. Image Previews
    setupImagePreview('id_logo', 'logo-preview', 'logo-text-fallback');
    setupImagePreview('id_hero_image', 'id_hero_image-preview');
    setupImagePreview('id_team_photo', 'team_photo-preview');

    // 2. Color Sync to Iframe
    const colorFields = ['primary', 'secondary', 'background'];
    colorFields.forEach(type => {
        const el = document.getElementById(`id_${type}_color`);
        if (el) {
            el.addEventListener('input', (e) => {
                if (previewFrame && previewFrame.contentWindow) {
                    previewFrame.contentWindow.postMessage({
                        type: 'updateColor',
                        colorType: type,
                        value: e.target.value
                    }, '*');
                }
            });
        }
    });

    // 3. Theme Switcher Sync
    document.querySelectorAll('input[name="template_choice"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            if (previewFrame && previewFrame.contentWindow) {
                previewFrame.contentWindow.postMessage({
                    type: 'updateTheme',
                    theme: e.target.value
                }, '*');
            }
        });
    });

    // 4. Success Toast (Cleaned up logic)
    const toastEl = document.getElementById('messageToast');
    if (toastEl && toastEl.querySelector('.toast-body').innerText.trim().length > 0) {
        new bootstrap.Toast(toastEl, { delay: 3000 }).show();
    }
});