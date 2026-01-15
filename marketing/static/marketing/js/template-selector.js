/* to add a co name to the preview links dynamically */
document.addEventListener('DOMContentLoaded', function() {
    const companyInput = document.getElementById('companyNameInput');
    const links = document.querySelectorAll('.dynamic-link');

    if (companyInput) {
        companyInput.addEventListener('input', function(e) {
            const currentName = e.target.value.trim();
            const encodedName = encodeURIComponent(currentName);

            links.forEach(link => {
                const url = new URL(link.href, window.location.origin);
                
                if (currentName.length > 0) {
                    url.searchParams.set('company_name', currentName);
                } else {
                    url.searchParams.delete('company_name');
                }
                
                link.href = url.toString();
            });
        });
    }
});