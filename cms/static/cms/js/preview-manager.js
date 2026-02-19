/**
 * preview-manager.js
 * Handles: device toggle, local image previews, character counters.
 * Preview updates on Save only — no live iframe sync.
 */

// Device toggle

function setPreviewSize(size) {
    // Check if the screen is actually wide enough
    if (window.innerWidth < 992 && (size === 'desktop' || size === 'tablet')) {
        return;
    }
    const wrapper = document.getElementById('preview-wrapper');
    if (!wrapper) return;

    wrapper.classList.remove('desktop-mode', 'tablet-mode', 'mobile-mode');
    wrapper.classList.add(size + '-mode');

    ['desktop', 'tablet', 'mobile'].forEach(s => {
        const btn = document.getElementById('btn-' + s);
        if (!btn) return;
        if (s === size) {
            btn.classList.remove('btn-outline-secondary');
            btn.classList.add('btn-secondary');
        } else {
            btn.classList.remove('btn-secondary');
            btn.classList.add('btn-outline-secondary');
        }
    });
}

// Image previews

function setupImagePreview(inputId, previewId, fallbackId) {
    const input    = document.getElementById(inputId);
    const preview  = document.getElementById(previewId);
    const fallback = fallbackId ? document.getElementById(fallbackId) : null;

    if (!input || !preview) return;

    input.addEventListener('change', function () {
        const file = this.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (e) => {
            preview.src = e.target.result;
            preview.classList.remove('d-none');
            if (fallback) fallback.classList.add('d-none');
        };
        reader.readAsDataURL(file);
    });
}

// character counters

function setupCharCounter(wrapperEl) {
    const max     = parseInt(wrapperEl.dataset.maxchars, 10);
    const inputEl = wrapperEl.querySelector('input, textarea');
    if (!max || !inputEl) return;

    const counter = document.createElement('div');
    counter.className = 'char-counter text-end small mt-1 mb-2';
    wrapperEl.appendChild(counter);

    function update() {
        const len       = inputEl.value.length;
        const remaining = max - len;
        counter.textContent = `${len} / ${max}`;
        counter.classList.toggle('text-danger', remaining < 0);
        counter.classList.toggle('text-warning', remaining >= 0 && remaining < Math.round(max * 0.1));
        counter.classList.toggle('text-muted',   remaining >= Math.round(max * 0.1));
    }

    inputEl.addEventListener('input', update);
    update(); // show count immediately on page load
}


// initialization

document.addEventListener('DOMContentLoaded', () => {

    // Image previews
    setupImagePreview('id_logo',       'logo-preview',       'logo-text-fallback');
    setupImagePreview('id_hero_image', 'id_hero_image-preview');
    setupImagePreview('id_team_photo', 'team_photo-preview');

    // Character counters — finds every field with data-maxchars
    document.querySelectorAll('[data-maxchars]').forEach(setupCharCounter);

    // Success toast
    const toastEl = document.getElementById('messageToast');
    if (toastEl) {
        const body = toastEl.querySelector('.toast-body');
        if (body && body.innerText.trim().length > 0) {
            new bootstrap.Toast(toastEl, { delay: 3000 }).show();
        }
    }
});