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