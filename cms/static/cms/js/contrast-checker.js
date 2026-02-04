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
 * Updates a dynamic contrast status bar and friendly labels.
 */
function validateContrast() {
    const primaryInput = document.querySelector('#id_primary_color');
    const bgInput = document.querySelector('#id_background_color');
    const statusBar = document.querySelector('#contrast-bar'); // Fixed naming mismatch
    const statusText = document.querySelector('#contrast-status-text');
    const statusBadge = document.querySelector('#contrast-status-badge');

    if (!primaryInput || !bgInput || !statusBar || !statusText) return;

    const brightnessPrimary = getBrightness(primaryInput.value);
    const brightnessBG = getBrightness(bgInput.value);
    const diff = Math.abs(brightnessPrimary - brightnessBG);

    const score = Math.min(100, Math.round((diff / 125) * 50)); 
    statusBar.style.width = `${score}%`;
    
    if (diff < 90) {
        statusBar.className = 'progress-bar bg-danger';
        statusText.innerText = 'Hard to read - try a darker primary or lighter background.';
        statusBadge.innerText = 'Poor';
        statusBadge.className = 'badge bg-danger';
    } else if (diff < 150) {
        statusBar.className = 'progress-bar bg-warning';
        statusText.innerText = 'Looks okay, but could be clearer.';
        statusBadge.innerText = 'Good';
        statusBadge.className = 'badge bg-warning text-dark';
    } else {
        statusBar.className = 'progress-bar bg-success';
        statusText.innerText = 'Great! Very easy for candidates to read.';
        statusBadge.innerText = 'Perfect';
        statusBadge.className = 'badge bg-success';
    }
}

// Initializing listeners
document.addEventListener('DOMContentLoaded', () => {
    const primaryInput = document.querySelector('#id_primary_color');
    const bgInput = document.querySelector('#id_background_color');

    if (primaryInput && bgInput) {
        primaryInput.addEventListener('input', validateContrast);
        bgInput.addEventListener('input', validateContrast);
        validateContrast(); 
    }
});