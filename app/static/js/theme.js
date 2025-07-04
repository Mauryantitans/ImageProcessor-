class ThemeManager {
    constructor() {
        this.theme = localStorage.getItem('theme') || 'light';
        this.init();
    }

    init() {
        // Set initial theme
        this.setTheme(this.theme);
        
        // Add theme toggle button
        this.addThemeToggle();
        
        // Listen for system theme changes
        this.listenForSystemTheme();
    }

    setTheme(theme) {
        this.theme = theme;
        // Remove existing theme classes
        document.body.classList.remove('light-theme', 'dark-theme');
        // Add new theme class
        document.body.classList.add(`${theme}-theme`);
        localStorage.setItem('theme', theme);
        
        // Update toggle button icon
        const toggleBtn = document.querySelector('.theme-toggle');
        if (toggleBtn) {
            toggleBtn.innerHTML = this.theme === 'dark' ? '☀️' : '🌙';
            toggleBtn.setAttribute('title', `Switch to ${this.theme === 'dark' ? 'light' : 'dark'} mode`);
        }
    }

    toggleTheme() {
        this.setTheme(this.theme === 'dark' ? 'light' : 'dark');
    }

    addThemeToggle() {
        const toggleBtn = document.createElement('button');
        toggleBtn.className = 'theme-toggle';
        toggleBtn.innerHTML = this.theme === 'dark' ? '☀️' : '🌙';
        toggleBtn.setAttribute('aria-label', 'Toggle theme');
        toggleBtn.setAttribute('title', `Switch to ${this.theme === 'dark' ? 'light' : 'dark'} mode`);
        toggleBtn.onclick = () => this.toggleTheme();
        document.body.appendChild(toggleBtn);
    }

    listenForSystemTheme() {
        // Only apply system theme if user hasn't set a preference
        if (!localStorage.getItem('theme')) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            
            const handleChange = (e) => {
                this.setTheme(e.matches ? 'dark' : 'light');
            };
            
            mediaQuery.addEventListener('change', handleChange);
            handleChange(mediaQuery);
        }
    }
}

// Initialize theme manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.themeManager = new ThemeManager();
}); 