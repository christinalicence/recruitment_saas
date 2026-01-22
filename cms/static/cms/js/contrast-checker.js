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
 * Checks contrast between primary and background colors.
 */
function validateContrast() {
    const primaryInput = document.querySelector('#id_primary_color');
    const bgInput = document.querySelector('#id_background_color');
    const warning = document.querySelector('#contrast-warning');

    if (!primaryInput || !bgInput || !warning) return;

    const brightnessPrimary = getBrightness(primaryInput.value);
    const brightnessBG = getBrightness(bgInput.value);

    // Standard threshold: a difference less than 125 indicates poor readability
    const diff = Math.abs(brightnessPrimary - brightnessBG);

    if (diff < 125) {
        warning.classList.remove('d-none');
    } else {
        warning.classList.add('d-none');
    }
}

// Initialize listeners
document.addEventListener('DOMContentLoaded', () => {
    const primaryInput = document.querySelector('#id_primary_color');
    const bgInput = document.querySelector('#id_background_color');

    if (primaryInput && bgInput) {
        primaryInput.addEventListener('input', validateContrast);
        bgInput.addEventListener('input', validateContrast);
        validateContrast(); // Run once on load
    }
});