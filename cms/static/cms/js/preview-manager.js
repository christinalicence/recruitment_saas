/**
 * Manages the interaction between the Editor Form and the Preview Iframe.
 */
document.addEventListener('DOMContentLoaded', () => {
    const previewFrame = document.getElementById('preview-frame');
    const form = document.querySelector('form');

    if (!previewFrame) return;

    // 1. Refresh preview when specific inputs change (colors, selects)
    const instantRefreshFields = document.querySelectorAll('input[type="color"], select');
    instantRefreshFields.forEach(input => {
        input.addEventListener('change', () => {
            console.log("Refreshing preview due to style change...");
            previewFrame.contentWindow.location.reload();
        });
    });

    // 2. Debounced refresh for text areas (prevents lag while typing)
    let timeout = null;
    const textFields = document.querySelectorAll('input[type="text"], textarea');
    textFields.forEach(field => {
        field.addEventListener('input', () => {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                console.log("Refreshing preview after typing...");
                previewFrame.contentWindow.location.reload();
            }, 1000); // Wait 1 second after last keystroke
        });
    });
});


/**
 * Changes the preview iframe width based on device selection
 * @param {string} device - 'desktop', 'tablet', or 'mobile'
 */
function setPreviewSize(device) {
    const wrapper = document.getElementById('preview-wrapper');
    const devices = ['desktop', 'tablet', 'mobile'];
    
    // 1. Swap the mode class on the wrapper
    devices.forEach(d => wrapper.classList.remove(`${d}-mode`));
    wrapper.classList.add(`${device}-mode`);
    
    // 2. Update Button UI states
    devices.forEach(d => {
        const btn = document.getElementById(`btn-${d}`);
        if (d === device) {
            btn.classList.add('active', 'btn-primary');
            btn.classList.remove('btn-outline-secondary');
        } else {
            btn.classList.remove('active', 'btn-primary');
            btn.classList.add('btn-outline-secondary');
        }
    });
}