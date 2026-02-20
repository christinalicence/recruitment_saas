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
 * Injects --brand-computed-hero-text onto :root.
 * This is the text colour used inside the hero section.
 * Computed from --brand-primary (the hero bg) brightness:
 *   bright primary  → dark text (#1a1a1a)
 *   dark primary    → white text (#ffffff)
 *
 * Threshold 128: midpoint of 0–255 luminosity scale.
 */
function updateCSSColourVariables() {
    const primaryInput = document.querySelector('#id_primary_color');
    if (primaryInput && primaryInput.value) {
        const heroText = getBrightness(primaryInput.value) > 128 ? '#1a1a1a' : '#ffffff';
        document.documentElement.style.setProperty('--brand-computed-hero-text', heroText);
    }
}

/**
 * Updates the contrast status bar.
 * Now checks secondary (text colour) vs background — the actual
 * reading experience for candidates visiting the site.
 */
function validateContrast() {
    const secondaryInput = document.querySelector('#id_secondary_color');
    const bgInput        = document.querySelector('#id_background_color');
    const statusBar      = document.querySelector('#contrast-bar');
    const statusText     = document.querySelector('#contrast-status-text');
    const statusBadge    = document.querySelector('#contrast-status-badge');

    if (!secondaryInput || !bgInput || !statusBar || !statusText) return;

    const brightnessText = getBrightness(secondaryInput.value);
    const brightnessBG   = getBrightness(bgInput.value);
    const diff           = Math.abs(brightnessText - brightnessBG);

    const score = Math.min(100, Math.round((diff / 125) * 50));
    statusBar.style.width = `${score}%`;

    if (diff < 90) {
        statusBar.className  = 'progress-bar bg-danger';
        statusText.innerText = 'Hard to read — try a darker text colour or lighter background.';
        statusBadge.innerText = 'Poor';
        statusBadge.className = 'badge bg-danger';
    } else if (diff < 150) {
        statusBar.className  = 'progress-bar bg-warning';
        statusText.innerText = 'Looks okay, but could be clearer.';
        statusBadge.innerText = 'Good';
        statusBadge.className = 'badge bg-warning text-dark';
    } else {
        statusBar.className  = 'progress-bar bg-success';
        statusText.innerText = 'Great! Very easy for candidates to read.';
        statusBadge.innerText = 'Perfect';
        statusBadge.className = 'badge bg-success';
    }

    // Keep hero text colour in sync with primary picker
    updateCSSColourVariables();
}

// Initializing listeners
document.addEventListener('DOMContentLoaded', () => {
    const primaryInput   = document.querySelector('#id_primary_color');
    const secondaryInput = document.querySelector('#id_secondary_color');
    const bgInput        = document.querySelector('#id_background_color');

    // Contrast bar watches secondary vs background
    if (secondaryInput && bgInput) {
        secondaryInput.addEventListener('input', validateContrast);
        bgInput.addEventListener('input', validateContrast);
        validateContrast();
    }

    // Primary picker changes hero bg colour — recompute hero text independently
    if (primaryInput) {
        primaryInput.addEventListener('input', updateCSSColourVariables);
        updateCSSColourVariables();
    }
});