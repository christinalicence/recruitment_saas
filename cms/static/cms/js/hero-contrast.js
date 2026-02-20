/**
 * hero-contrast.js
 * Sets --brand-computed-hero-text on :root based on the hero background brightness.
 * Loaded on all tenant pages via base_tenant.html.
 * Uses the same YIQ formula as contrast-checker.js (which only runs on the editor).
 */
(function () {
    var el = document.documentElement;
    var hex = getComputedStyle(el).getPropertyValue('--brand-primary').trim().replace('#', '');

    if (!hex || hex.length < 6) return;

    var r = parseInt(hex.substr(0, 2), 16);
    var g = parseInt(hex.substr(2, 2), 16);
    var b = parseInt(hex.substr(4, 2), 16);
    var brightness = (r * 299 + g * 587 + b * 114) / 1000;

    el.style.setProperty(
        '--brand-computed-hero-text',
        brightness > 128 ? '#1a1a1a' : '#ffffff'
    );
}());