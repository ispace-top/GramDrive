document.addEventListener('DOMContentLoaded', function() {
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.querySelector('.nav-menu');

    // Toggle mobile menu
    if (navToggle) {
        navToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
        });
    }

    // Set active navigation link
    const currentLocation = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-menu a');

    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentLocation) {
            link.classList.add('active');
        }
    });

    // Add loading indicator for navigation links
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            // Only show loading for internal navigation
            const href = link.getAttribute('href');
            if (href && href.startsWith('/') && !href.startsWith('//')) {
                // Create or show global loading overlay
                let loader = document.getElementById('page-loader');
                if (!loader) {
                    loader = document.createElement('div');
                    loader.id = 'page-loader';
                    loader.style.cssText = 'position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.3); z-index: 9999; display: flex; align-items: center; justify-content: center;';
                    loader.innerHTML = '<div style="width: 48px; height: 48px; border: 4px solid rgba(255,255,255,0.3); border-top-color: white; border-radius: 50%; animation: spin 0.8s linear infinite;"></div>';
                    document.body.appendChild(loader);

                    // Add keyframes if not exists
                    if (!document.querySelector('style[data-nav-loader]')) {
                        const style = document.createElement('style');
                        style.setAttribute('data-nav-loader', '');
                        style.textContent = '@keyframes spin { to { transform: rotate(360deg); } }';
                        document.head.appendChild(style);
                    }
                }
                loader.style.display = 'flex';
            }
        });
    });
});