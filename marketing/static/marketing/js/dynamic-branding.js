// Apply dynamic CSS variables from data attributes
(function() {
    const body = document.body;
    const primary = body.dataset.primaryColor;
    const secondary = body.dataset.secondaryColor;
    const bg = body.dataset.bgColor;
    const logo = body.dataset.logoUrl;
    
    if (primary) body.style.setProperty('--brand-primary', primary);
    if (secondary) body.style.setProperty('--brand-accent', secondary);
    if (bg) body.style.backgroundColor = bg;
    if (logo) {
        const logoEl = document.querySelector('.navbar-brand-img');
        if (logoEl) logoEl.style.backgroundImage = `url(${logo})`;
    }
})();