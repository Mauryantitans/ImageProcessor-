class UI {
    constructor() {
        this.fileInput = document.getElementById('file-input');
        this.uploadBtn = document.getElementById('upload-btn');
        this.previewsVisible = true;
        this.init();
    }

    init() {
        this.setupFileInput();
        this.setupDownloadButton();
        this.setupPreviewToggle();
    }

    setupFileInput() {
        this.uploadBtn.addEventListener('click', () => {
            this.fileInput.click();
        });

        this.fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file && file.type.startsWith('image/')) {
                window.pipeline.setImage(file);
            } else if (file) {
                window.pipeline.showError('Please select an image file.');
            }
        });
    }

    setupDownloadButton() {
        const downloadBtn = document.getElementById('download-btn');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => {
                window.pipeline.downloadResult();
        });
        }
    }

    setupPreviewToggle() {
        const toggleBtn = document.getElementById('toggle-previews');
        const previewContainer = document.getElementById('preview-container');
        const btnText = toggleBtn.querySelector('.btn-text');

        toggleBtn.addEventListener('click', () => {
            this.previewsVisible = !this.previewsVisible;
            
            if (this.previewsVisible) {
                previewContainer.classList.remove('hidden');
                btnText.textContent = 'Hide Previews';
            } else {
                previewContainer.classList.add('hidden');
                btnText.textContent = 'Show Previews';
            }
        });
    }
}

// Initialize UI when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.ui = new UI();
}); 