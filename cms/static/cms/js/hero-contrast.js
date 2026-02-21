/**
 * hero-contrast.js
 * Sets --brand-computed-hero-text on :root based on the hero background brightness.
 * Loaded on all tenant pages via base_tenant.html.
 * Uses the same YIQ formula as contrast-checker.js.
 */
(function () {
    const applyHeroContrast = () => {
        // get hero background color from CSS variable
        const bodyStyles = getComputedStyle(document.body);
        const hex = bodyStyles.getPropertyValue('--brand-primary').trim().replace('#', '');

        // Fallback if color isn't loaded yet
        if (!hex || hex.length < 6) return;

        // The YIQ Brightness Formula (Best for Grey/Muted tones)
        const r = parseInt(hex.substr(0, 2), 16);
        const g = parseInt(hex.substr(2, 2), 16);
        const b = parseInt(hex.substr(4, 2), 16);

        const brightness = (r * 299 + g * 587 + b * 114) / 1000;

        const contrastColor = brightness > 128 ? '#1a1a1a' : '#ffffff';
        
        document.documentElement.style.setProperty('--brand-computed-hero-text', contrastColor);
    };

    // Run on load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', applyHeroContrast);
    } else {
        applyHeroContrast();
    }
})();