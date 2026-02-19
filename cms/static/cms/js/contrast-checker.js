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
Make appropriate text colour CSS variables based on brightness of the primary and secondary pickers.
This allows us to have dynamic text colours on the homepage hero and throughout the site that automatically update to maintain contrast as users adjust their colours.
 */
function updateCSSColourVariables() {
    const primaryInput   = document.querySelector('#id_primary_color');
    const secondaryInput = document.querySelector('#id_secondary_color');
    const root = document.documentElement;

    if (primaryInput && primaryInput.value) {
        const onPrimary = getBrightness(primaryInput.value) > 128 ? '#1a1a1a' : '#ffffff';
        root.style.setProperty('--brand-computed-text', onPrimary);
    }

    if (secondaryInput && secondaryInput.value) {
        const onSecondary = getBrightness(secondaryInput.value) > 128 ? '#1a1a1a' : '#ffffff';
        root.style.setProperty('--brand-computed-hero-text', onSecondary);
    }
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

    // Keep CSS colour variables in sync with picker state
    updateCSSColourVariables();
}

// Initializing listeners
document.addEventListener('DOMContentLoaded', () => {
    const primaryInput   = document.querySelector('#id_primary_color');
    const bgInput        = document.querySelector('#id_background_color');
    const secondaryInput = document.querySelector('#id_secondary_color');

    if (primaryInput && bgInput) {
        primaryInput.addEventListener('input', validateContrast);
        bgInput.addEventListener('input', validateContrast);
        validateContrast(); 
    }

    // Secondary picker doesn't affect the contrast bar, but does affect
    // hero text colour on startup theme — listen independently
    if (secondaryInput) {
        secondaryInput.addEventListener('input', updateCSSColourVariables);
    }
});