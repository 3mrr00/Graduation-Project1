// Language Switcher JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Language switcher functionality
    const languageLinks = document.querySelectorAll('.language-switch');
    
    if (languageLinks.length > 0) {
        languageLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                
                const language = this.getAttribute('data-language');
                
                // Set a cookie to remember the language choice
                document.cookie = `lang_preference=${language}; path=/; max-age=31536000`; // 1 year
                
                // Redirect to the language change URL
                window.location.href = this.getAttribute('href');
            });
        });
    }
    
    // Add RTL support when Arabic is selected
    const htmlElement = document.documentElement;
    if (htmlElement.getAttribute('lang') === 'ar') {
        htmlElement.setAttribute('dir', 'rtl');
        
        // Add RTL version of Bootstrap if needed
        const currentBootstrap = document.querySelector('link[href*="bootstrap.min.css"]');
        if (currentBootstrap) {
            currentBootstrap.setAttribute('href', 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css');
        }
    }
    
    // Form label animation for RTL
    if (htmlElement.getAttribute('dir') === 'rtl') {
        const formLabels = document.querySelectorAll('.form-floating > label');
        formLabels.forEach(label => {
            label.style.right = '0';
            label.style.left = 'auto';
        });
    }
}); 