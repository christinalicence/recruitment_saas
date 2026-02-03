/**
 * Calculates perceived brightness using the YIQ formula.
 */
function getBrightness(hexcolor) {
    hexcolor = hexcolor.replace("#", "");
    const r = parseInt(hexcolor.substr(0, 2), 16);
    const g = parseInt(hexcolor.substr(2, 2), 16);
    const b = parseInt(hexcolor.substr(4, 2), 16);
    return ((r * 299) + (g * 587) + (b * 114)) / 1000;
}

/**
 * Updates a dynamic contrast status bar.
 */
function validateContrast() {
    const primaryInput = document.querySelector('#id_primary_color');
    const bgInput = document.querySelector('#id_background_color');
    const statusBar = document.querySelector('#contrast-status-bar');
    const statusText = document.querySelector('#contrast-status-text');

    if (!primaryInput || !bgInput || !statusBar || !statusText) return;

    const brightnessPrimary = getBrightness(primaryInput.value);
    const brightnessBG = getBrightness(bgInput.value);
    const diff = Math.abs(brightnessPrimary - brightnessBG);

    // Calculate percentage (max diff is 255)
    const score = Math.min(100, Math.round((diff / 125) * 50)); 
    
    statusBar.style.width = `${score}%`;
    
    if (diff < 70) {
        statusBar.className = 'progress-bar bg-danger';
        statusText.innerHTML = '<i class="bi bi-x-circle"></i> Very Poor Contrast';
    } else if (diff < 125) {
        statusBar.className = 'progress-bar bg-warning';
        statusText.innerHTML = '<i class="bi bi-exclamation-triangle"></i> Fair Contrast';
    } else {
        statusBar.className = 'progress-bar bg-success';
        statusText.innerHTML = '<i class="bi bi-check-circle"></i> Good Contrast';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const primaryInput = document.querySelector('#id_primary_color');
    const bgInput = document.querySelector('#id_background_color');

    if (primaryInput && bgInput) {
        primaryInput.addEventListener('input', validateContrast);
        bgInput.addEventListener('input', validateContrast);
        validateContrast(); // Initial check
    }
});