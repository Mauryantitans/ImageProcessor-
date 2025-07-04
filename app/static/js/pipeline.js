class Pipeline {
    constructor() {
        this.steps = [];
        this.availableOperations = [];
        this.categories = {};
        this.currentImage = null;
        this.isProcessing = false;
        this.viewMode = 'list'; // 'list' or 'grid'
        this.previewSteps = new Set();
        this.operationCounts = {};
        this.lastProcessedParams = new Map();
        this.initialized = false;
        this.maxImageSize = 4096; // Maximum dimension size in pixels
        this.maxFileSize = 10 * 1024 * 1024; // 10MB limit
        this.liveProcessing = false; // New property for live processing toggle
        this.processingStartTime = 0;
        this.updatePipelineStats();
        this.processingTimeout = null; // For managing status indicator timeout
        this.previewsVisible = true; // Add this line for preview visibility state
        this.isCompareMode = false;
        this.compareSliderPosition = 50; // percentage
        this.isDragging = false;
        this.isDownloading = false;  // Add this line
    }

    async init() {
        try {
            console.log('Initializing pipeline...');
            this.updateDebugInfo('Loading operations...');
            
            // Initialize buttons first
            this.initializeButtons();
            
            console.log('Fetching operations from /api/operations...');
            const response = await fetch('/api/operations');
            console.log('Response status:', response.status);
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP error! status: ${response.status}, text: ${errorText}`);
            }
            
            const data = await response.json();
            
            if (!data.operations || !data.categories) {
                throw new Error('Invalid data format received from server');
            }
            
            this.availableOperations = data.operations;
            this.categories = data.categories;
            
            this.setupOperationsUI();
            this.setupSearch();
            this.setupPreviewToggle();
            
            this.initialized = true;
            this.clearDebugInfo();
            console.log('Pipeline initialization complete!');
        } catch (error) {
            this.handleError(error, 'Failed to initialize pipeline');
            // Show error in UI
            const container = document.getElementById('operations-container');
            if (container) {
                container.innerHTML = `
                    <div class="error-message" style="padding: 1rem; color: var(--error-color);">
                        <p>Failed to load operations:</p>
                        <p>${error.message}</p>
                        <button onclick="window.pipeline.init()" class="btn btn-error">
                            Try Again
                        </button>
                    </div>
                `;
            }
        }
    }

    initializeButtons() {
        // Initialize live processing button
        const liveProcessingBtn = document.getElementById('live-processing-btn');
        const applyPipelineBtn = document.getElementById('apply-pipeline-btn');
        const resetPipelineBtn = document.getElementById('reset-pipeline-btn');
        
        // Create and add status indicator
        if (liveProcessingBtn) {
            const statusIndicator = document.createElement('div');
            statusIndicator.id = 'processing-status';
            statusIndicator.className = 'processing-status';
            statusIndicator.innerHTML = `
                <div class="status-dot disabled"></div>
                <span class="status-text">Waiting for image</span>
            `;
            liveProcessingBtn.parentNode.insertBefore(statusIndicator, liveProcessingBtn.nextSibling);
            
            liveProcessingBtn.addEventListener('click', () => {
                this.liveProcessing = !this.liveProcessing;
                liveProcessingBtn.setAttribute('data-active', this.liveProcessing.toString());
                applyPipelineBtn.style.display = this.liveProcessing ? 'none' : 'inline-flex';
                
                // Update status based on current state
                if (!this.currentImage) {
                    this.updateProcessingStatus('waiting');
                } else if (this.steps.length === 0) {
                    this.updateProcessingStatus('add_steps');
                } else if (this.liveProcessing) {
                    this.processImage();
                } else {
                    this.updateProcessingStatus('action_needed');
                }
            });
        }

        if (applyPipelineBtn) {
            applyPipelineBtn.addEventListener('click', () => {
                if (this.currentImage) {
                    this.processImage();
                }
            });
        }

        if (resetPipelineBtn) {
            resetPipelineBtn.addEventListener('click', () => {
                this.resetPipeline();
            });
        }
    }

    updateProcessingStatus(status) {
        // Use requestAnimationFrame for status updates to avoid blocking processing
        requestAnimationFrame(() => {
            const statusIndicator = document.getElementById('processing-status');
            if (!statusIndicator) return;

            const statusDot = statusIndicator.querySelector('.status-dot');
            const statusText = statusIndicator.querySelector('.status-text');
            
            // Clear any existing timeout
            if (this.processingTimeout) {
                clearTimeout(this.processingTimeout);
                this.processingTimeout = null;
            }

            // If no image is present, always show "Waiting for image"
            if (!this.currentImage && status !== 'processing') {
                statusDot.className = 'status-dot disabled';
                statusText.textContent = 'Waiting for image';
                return;
            }

            switch (status) {
                case 'waiting':
                    statusDot.className = 'status-dot disabled';
                    statusText.textContent = 'Waiting for image';
                    break;
                case 'add_steps':
                    statusDot.className = 'status-dot ready';
                    statusText.textContent = 'Add steps to start';
                    break;
                case 'processing':
                    statusDot.className = 'status-dot processing';
                    statusText.textContent = 'Processing';
                    break;
                case 'ready':
                    statusDot.className = 'status-dot ready';
                    statusText.textContent = 'Ready to process';
                    break;
                case 'done':
                    statusDot.className = 'status-dot done';
                    statusText.textContent = 'Done';
                    // Reset to appropriate state after 1 second
                    this.processingTimeout = setTimeout(() => {
                        if (this.liveProcessing) {
                            if (!this.currentImage) {
                                this.updateProcessingStatus('waiting');
                            } else {
                                this.updateProcessingStatus(this.steps.length > 0 ? 'ready' : 'add_steps');
                            }
                        } else {
                            this.updateProcessingStatus('action_needed');
                        }
                    }, 1000);
                    break;
                case 'error':
                    statusDot.className = 'status-dot error';
                    statusText.textContent = 'Error';
                    // Reset to appropriate state after 2 seconds
                    this.processingTimeout = setTimeout(() => {
                        if (this.liveProcessing) {
                            if (!this.currentImage) {
                                this.updateProcessingStatus('waiting');
                            } else {
                                this.updateProcessingStatus(this.steps.length > 0 ? 'ready' : 'add_steps');
                            }
                        } else {
                            this.updateProcessingStatus('action_needed');
                        }
                    }, 2000);
                    break;
                case 'disabled':
                    statusDot.className = 'status-dot disabled';
                    statusText.textContent = 'Live processing off';
                    // If we have steps, show action needed message
                    if (this.steps.length > 0) {
                        this.processingTimeout = setTimeout(() => {
                            this.updateProcessingStatus('action_needed');
                        }, 1000);
                    }
                    break;
                case 'action_needed':
                    statusDot.className = 'status-dot ready';
                    statusText.textContent = 'Apply pipeline or enable live';
                    break;
            }
        });
    }

    updateDebugInfo(message) {
        const debugInfo = document.getElementById('debug-info');
        if (debugInfo) {
            debugInfo.textContent = message;
            debugInfo.style.display = 'block';
            console.log('Debug info:', message);
        }
    }

    clearDebugInfo() {
        const debugInfo = document.getElementById('debug-info');
        if (debugInfo) {
            debugInfo.style.display = 'none';
        }
    }

    setupOperationsUI() {
        console.log('Setting up operations UI...');
        const container = document.getElementById('operations-container');
        if (!container) {
            console.error('Operations container not found!');
            this.updateDebugInfo('Error: Operations container not found');
            return;
        }
        
        if (!this.categories || !this.availableOperations) {
            console.error('Categories or operations not loaded');
            this.updateDebugInfo('Error: Operations data not loaded');
            return;
        }
        
        const html = this.generateCategoryHTML();
        console.log('Generated HTML:', html);
        
        if (!html.trim()) {
            console.error('No HTML generated for operations');
            this.updateDebugInfo('Error: No operations available');
            return;
        }
        
        container.innerHTML = html;
        
        // Ensure all categories and subcategories are collapsed by default
        document.querySelectorAll('.category-group, .subcategory-group').forEach(group => {
            group.classList.add('collapsed');
        });

        // Calculate and set initial height after a short delay to ensure DOM is ready
        setTimeout(() => {
            this.setInitialOperationsHeight();
        }, 100);

        // Setup category toggles with height management
        document.querySelectorAll('.category-header').forEach(header => {
            header.addEventListener('click', (e) => {
                const group = header.closest('.category-group');
                group.classList.toggle('collapsed');
                e.stopPropagation();
            });
        });

        // Setup subcategory toggles
        document.querySelectorAll('.subcategory-header').forEach(header => {
            header.addEventListener('click', (e) => {
                const group = header.closest('.subcategory-group');
                group.classList.toggle('collapsed');
                e.stopPropagation();
            });
        });
    }

    setInitialOperationsHeight() {
        const operationsSection = document.querySelector('.operations-section');
        const categoriesContainer = document.querySelector('.operations-categories');
        if (!operationsSection || !categoriesContainer) return;

        // Store the current scroll position
        const scrollTop = categoriesContainer.scrollTop;

        // Temporarily remove collapsed state to measure full height
        const groups = document.querySelectorAll('.category-group, .subcategory-group');
        groups.forEach(group => group.classList.remove('collapsed'));

        // Get the full height
        const fullHeight = categoriesContainer.scrollHeight;

        // Restore collapsed state
        groups.forEach(group => group.classList.add('collapsed'));

        // Calculate the height with all categories collapsed
        const collapsedHeight = categoriesContainer.scrollHeight;

        // Set the height to the collapsed height plus some padding
        const finalHeight = collapsedHeight + 20; // 20px padding
        operationsSection.style.height = `${finalHeight}px`;

        // Store the height for future reference
        operationsSection.dataset.initialHeight = finalHeight;

        // Restore the scroll position
        categoriesContainer.scrollTop = scrollTop;
    }

    generateCategoryHTML() {
        if (!this.categories || !this.availableOperations) {
            console.error('Categories or operations not loaded');
            return '';
        }

        return Object.entries(this.categories).map(([categoryId, category]) => {
            const categoryOperations = this.availableOperations.filter(op => op.category === categoryId);
            
            // Only show categories that have operations
            if (categoryOperations.length === 0) {
                return '';
            }

            // Special handling for OpenCV category
            if (categoryId === 'opencv') {
                // Group operations by subcategory
                const subcategoryOperations = {};
                categoryOperations.forEach(op => {
                    const subcategory = op.subcategory || 'other';
                    if (!subcategoryOperations[subcategory]) {
                        subcategoryOperations[subcategory] = [];
                    }
                    subcategoryOperations[subcategory].push(op);
                });

                return `
                    <div class="category-group collapsed">
                        <div class="category-header">
                            <span class="category-icon">${category.icon}</span>
                            <span class="category-title">${category.name}</span>
                            <span class="category-toggle">▼</span>
                        </div>
                        <div class="category-content">
                            ${Object.entries(category.subcategories || {}).map(([subcategoryId, subcategory]) => {
                                const operations = subcategoryOperations[subcategoryId] || [];
                                if (operations.length === 0) return '';
                                
                                return `
                                    <div class="subcategory-group collapsed">
                                        <div class="subcategory-header">
                                            <span class="subcategory-icon">${subcategory.icon}</span>
                                            <span class="subcategory-title">${subcategory.name}</span>
                                            <span class="subcategory-toggle">▼</span>
                                        </div>
                                        <div class="subcategory-content">
                                            ${operations.map(op => this.renderOperationCard(op)).join('')}
                                        </div>
                                    </div>
                                `;
                            }).join('')}
                        </div>
                    </div>
                `;
            }
            
            // For non-OpenCV categories, display operations directly under the category
            return `
                <div class="category-group collapsed">
                    <div class="category-header">
                        <span class="category-icon">${category.icon}</span>
                        <span class="category-title">${category.name}</span>
                        <span class="category-toggle">▼</span>
                    </div>
                    <div class="category-content">
                        ${categoryOperations.map(op => this.renderOperationCard(op)).join('')}
                    </div>
                </div>
            `;
        }).join('');
    }

    renderOperationCard(operation) {
        return `
            <div class="operation-card" 
                 onclick="window.pipeline.addStep('${operation.id}')"
                 title="${operation.description}">
                <div class="operation-icon">${operation.icon}</div>
                <div class="operation-info">
                    <div class="operation-name">${operation.name}</div>
                    <div class="operation-description">${operation.description}</div>
                </div>
            </div>
        `;
    }

    setupSearch() {
        const searchInput = document.getElementById('operations-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                const searchTerm = e.target.value.trim();
                this.filterOperations(searchTerm);
            });

            // Add clear button functionality
            searchInput.addEventListener('keyup', (e) => {
                if (e.key === 'Escape') {
                    searchInput.value = '';
                    this.filterOperations('');
                }
            });
        }
    }

    setupViewToggle() {
        const viewToggle = document.getElementById('view-toggle');
        const container = document.getElementById('operations-container');
        
        viewToggle.addEventListener('click', () => {
            this.viewMode = this.viewMode === 'list' ? 'grid' : 'list';
            container.className = `operations-categories ${this.viewMode}-view`;
            viewToggle.innerHTML = `<span class="btn-icon">${this.viewMode === 'list' ? '📊' : '📝'}</span>`;
        });
    }

    filterOperations(searchTerm) {
        const operations = document.querySelectorAll('.operation-card');
        const categories = document.querySelectorAll('.category-group');
        const subcategories = document.querySelectorAll('.subcategory-group');
        const normalizedSearchTerm = searchTerm.toLowerCase().trim();

        if (!normalizedSearchTerm) {
            // Reset everything to default state when search is cleared
            operations.forEach(op => op.style.display = '');
            categories.forEach(cat => {
                cat.style.display = '';
                cat.classList.add('collapsed');
            });
            subcategories.forEach(subcat => {
                subcat.style.display = '';
                subcat.classList.add('collapsed');
            });
            
            // Reset to initial height
            this.setInitialOperationsHeight();
            return;
        }

        // First, find matching operations
        const matchingOps = Array.from(operations).filter(op => {
            const text = op.textContent.toLowerCase();
            return text.includes(normalizedSearchTerm);
        });

        if (matchingOps.length > 0) {
            // Show only matching operations
            operations.forEach(op => {
                const text = op.textContent.toLowerCase();
                const isVisible = text.includes(normalizedSearchTerm);
                op.style.display = isVisible ? '' : 'none';
                
                if (isVisible) {
                    // Get parent subcategory and category
                    const subcategory = op.closest('.subcategory-group');
                    const category = op.closest('.category-group');
                    
                    if (subcategory) {
                        subcategory.style.display = '';
                        subcategory.classList.remove('collapsed');
                    }
                    if (category) {
                        category.style.display = '';
                        category.classList.remove('collapsed');
                    }
                }
            });

            // Hide subcategories with no visible operations
            subcategories.forEach(subcategory => {
                const hasVisibleOps = Array.from(subcategory.querySelectorAll('.operation-card'))
                    .some(op => op.style.display !== 'none');
                subcategory.style.display = hasVisibleOps ? '' : 'none';
            });

            // Hide categories with no visible subcategories
            categories.forEach(category => {
                const hasVisibleContent = Array.from(category.querySelectorAll('.operation-card'))
                    .some(op => op.style.display !== 'none');
                category.style.display = hasVisibleContent ? '' : 'none';
            });
        } else {
            // No matches found
            operations.forEach(op => op.style.display = 'none');
            subcategories.forEach(subcat => subcat.style.display = 'none');
            categories.forEach(cat => cat.style.display = 'none');

            // Show "no results" message
            const container = document.getElementById('operations-container');
            const noResults = container.querySelector('.no-results');
            if (!noResults) {
                const message = document.createElement('div');
                message.className = 'no-results';
                message.style.padding = '1rem';
                message.style.color = 'var(--text-secondary)';
                message.textContent = `No operations found matching "${searchTerm}"`;
                container.appendChild(message);
            }
        }

        // Remove "no results" message if we have matches
        if (matchingOps.length > 0) {
            const noResults = document.querySelector('.no-results');
            if (noResults) {
                noResults.remove();
            }
        }
    }

    // Get the display name for an operation based on its count
    getOperationDisplayName(operationId, operationName) {
        // Count current instances of this operation in the pipeline
        const count = this.steps.filter(step => step.id === operationId).length + 1;
        return count > 1 ? `${operationName} (${count})` : operationName;
    }

    addStep(operationId) {
        const operation = this.availableOperations.find(op => op.id === operationId);
        if (operation) {
            // Create a new step with default parameter values
            const step = {
                id: operationId,
                params: {},
                displayName: this.getOperationDisplayName(operationId, operation.name)
            };

            // Initialize parameters with default values from schema
            if (operation.params) {
                Object.entries(operation.params).forEach(([key, config]) => {
                    step.params[key] = config.default !== undefined ? config.default : 0;
                });
            }

            this.steps.push(step);
            this.updatePipelineStats();
            this.renderPipeline();
            
            // Update status based on current state
            if (this.currentImage) {
                if (this.liveProcessing) {
            this.processImage();
                } else {
                    this.updateProcessingStatus('action_needed');
                }
            }
        }
    }

    removeStep(index) {
        // Store the preview state of the step being removed
        const wasPreviewEnabled = this.previewSteps.has(index);
        
        // Remove the step
        const removedStep = this.steps[index];
        this.steps.splice(index, 1);
        
        // Update preview states for all steps after the removed one
        const newPreviewSteps = new Set();
        this.previewSteps.forEach(previewIndex => {
            if (previewIndex < index) {
                // Keep preview states for steps before the removed one
                newPreviewSteps.add(previewIndex);
            } else if (previewIndex > index) {
                // Shift preview states for steps after the removed one
                newPreviewSteps.add(previewIndex - 1);
            }
            // Drop the preview state for the removed step
        });
        this.previewSteps = newPreviewSteps;
        
        // Update display names for remaining instances of the same operation
        const remainingSteps = this.steps.filter(step => step.id === removedStep.id);
        remainingSteps.forEach((step, i) => {
            step.displayName = i === 0 ? 
                this.availableOperations.find(op => op.id === step.id).name : 
                `${this.availableOperations.find(op => op.id === step.id).name} (${i + 1})`;
        });

        this.updatePipelineStats();
        this.renderPipeline();
        
        // If no steps remain, reset processed preview
        if (this.steps.length === 0) {
            this.resetProcessedPreview();
            if (this.liveProcessing) {
                this.updateProcessingStatus(this.currentImage ? 'add_steps' : 'waiting');
            }
        } else if (this.currentImage) {
            // Only process if we still have steps and an image
        this.processImage();
        }
        
        // If a preview was enabled for the removed step, adjust container height
        if (wasPreviewEnabled) {
            this.adjustPipelineContainerHeight();
        }
    }

    updateStepParams(index, params) {
        this.steps[index].params = { ...this.steps[index].params, ...params };
        this.processImage();
    }

    async processImage() {
        // If live processing is off and the request didn't come from the apply button, skip processing
        if (!this.liveProcessing && (!event || event.type !== 'click')) {
            return;
        }

        if (!this.currentImage || this.isProcessing) return;
        
        this.isProcessing = true;
        this.updateProcessingStatus('processing');
        
        try {
            const currentParams = this.steps.map(step => ({
                id: step.id,
                params: { ...step.params }
            }));

            const formData = new FormData();
            formData.append('image', this.currentImage);
            formData.append('pipeline', JSON.stringify(this.steps));
            
            // Prepare preview data before fetch
            const activePreviewSteps = Array.from(this.previewSteps).filter(stepIndex => 
                stepIndex < this.steps.length && 
                document.querySelector(`#preview-${stepIndex}:not([style*="display: none"])`)
            );
            formData.append('preview_steps', JSON.stringify(activePreviewSteps));
            
            // Process image
            const response = await fetch('/api/process', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(await response.text() || 'Image processing failed');
            }
            
            const result = await response.json();
            
            if (result.success) {
                // Update processing time from backend
                const timeElement = document.getElementById('processing-time');
                if (timeElement) {
                    timeElement.textContent = `${result.processing_time}ms`;
                }

                // Update previews
                if (result.image) {
                this.updatePreview(result.image);
                }

                // Update intermediate previews in batch
                if (result.intermediate_results) {
                    const previewUpdates = Object.entries(result.intermediate_results);
                    for (const [stepIndex, imageData] of previewUpdates) {
                        const previewContainer = document.querySelector(`#preview-${stepIndex}`);
                        if (previewContainer) {
                            const previewImg = previewContainer.querySelector('.preview-image');
                            if (previewImg) {
                                previewImg.src = imageData;
                                previewImg.style.display = 'block';
                            }
                        }
                    }
                }

                // Update params after all visual updates
                this.lastProcessedParams = new Map(
                    currentParams.map(step => [step.id, step.params])
                );

                // Update status last
                requestAnimationFrame(() => {
                    this.updateProcessingStatus('done');
                });
            } else {
                throw new Error(result.error || 'Processing failed');
            }
        } catch (error) {
            console.error('Processing error:', error);
            requestAnimationFrame(() => {
                this.updateProcessingStatus('error');
                const processedPreview = document.getElementById('processed-preview');
                if (processedPreview) {
                    processedPreview.style.border = '2px solid var(--danger-color)';
                    setTimeout(() => {
                        processedPreview.style.border = '';
                    }, 1000);
                }
            });
        } finally {
            this.isProcessing = false;
            // Batch cleanup operations
            requestAnimationFrame(() => {
                const processedPreview = document.getElementById('processed-preview');
                if (processedPreview) {
                    processedPreview.style.opacity = '';
                }
                document.querySelectorAll('.preview-loading').forEach(loader => {
                    loader.style.display = 'none';
                });
            });
        }
    }

    showNotification(type, message, duration = 1500) {
        const existingNotification = document.querySelector('.notification');
        if (existingNotification) {
            existingNotification.remove();
        }

        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-text">${message}</span>
            </div>
        `;
        document.body.appendChild(notification);

        setTimeout(() => notification.remove(), duration);
    }

    handleError(error, context) {
        console.error(`${context}:`, error);
        this.showNotification('error', error.message || 'An error occurred. Please try again.');
    }

    showError(message) {
        this.showNotification('error', message);
    }

    showSuccessNotification(hasSignificantChanges) {
        this.showNotification(
            'success',
            hasSignificantChanges 
                ? 'Processing complete! Changes applied successfully.'
                : 'Processing complete! Changes may be subtle or not visible.'
        );
    }

    setImage(file) {
        // Clear previous image and related data
        if (this.currentImage) {
            URL.revokeObjectURL(this.currentImage);
        }
        
        this.validateImage(file)
            .then(() => {
        this.currentImage = file;
        this.showOriginalPreview(file);
                
                // Enable compare button when image is loaded
                const compareBtn = document.getElementById('compare-btn');
                if (compareBtn && this.previewsVisible) {
                    compareBtn.disabled = false;
                }
                
                // Update status based on current state
                if (this.steps.length > 0) {
                    if (this.liveProcessing) {
        this.processImage();
                    } else {
                        this.updateProcessingStatus('action_needed');
                    }
                } else {
                    this.updateProcessingStatus('add_steps');
                }
                
                // Process the image only if we have steps and live processing
                if (this.steps.length > 0 && this.liveProcessing) {
        this.processImage();
                } else {
                    // Reset processed preview if no steps
                    this.resetProcessedPreview();
                }
                
                // Enable download button
                const downloadBtn = document.getElementById('download-btn');
                if (downloadBtn) {
                    downloadBtn.disabled = false;
                }
            })
            .catch(error => {
                this.showError(error.message);
                // Reset file input
                const fileInput = document.getElementById('file-input');
                if (fileInput) {
                    fileInput.value = '';
                }
                
                // Disable compare button
                const compareBtn = document.getElementById('compare-btn');
                if (compareBtn) {
                    compareBtn.disabled = true;
                }
            });
    }

    showOriginalPreview(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const preview = document.getElementById('original-preview');
            const placeholder = preview.previousElementSibling;
            
            if (preview) {
                // Clean up previous preview if it exists
                if (preview.src) {
                    URL.revokeObjectURL(preview.src);
                }
            preview.src = e.target.result;
                preview.style.display = 'block';
                if (placeholder) {
                    placeholder.style.display = 'none';
                }
            }
        };
        reader.readAsDataURL(file);
    }

    updatePreview(dataUrl) {
        const preview = document.getElementById('processed-preview');
        const comparePreview = document.getElementById('compare-processed');
        const placeholder = preview.previousElementSibling;
        
        if (preview) {
            if (preview.src) {
                URL.revokeObjectURL(preview.src);
            }
        preview.src = dataUrl;
            preview.style.display = 'block';
            if (placeholder) {
                placeholder.style.display = 'none';
            }

            // Update compare view if it exists and is active
            if (comparePreview && this.isCompareMode) {
                comparePreview.src = dataUrl;
                comparePreview.style.display = 'block';
            }
            
            // Enable download buttons
            const downloadBtnNormal = document.getElementById('download-btn-normal');
            const downloadBtnCompare = document.getElementById('download-btn-compare');
            if (downloadBtnNormal) {
                downloadBtnNormal.disabled = false;
            }
            if (downloadBtnCompare) {
                downloadBtnCompare.disabled = false;
            }
            
            // Adjust container height when preview is updated
            preview.onload = () => this.adjustPipelineContainerHeight();
        }
    }

    renderPipeline() {
        const container = document.getElementById('pipeline-steps');
        if (!this.steps.length) {
            container.innerHTML = `
                <div class="empty-pipeline-message">
                    <div class="message-icon">🔍</div>
                    <h3>No Steps Added</h3>
                    <p>Select operations from the left panel to build your pipeline</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.steps.map((step, index) => {
            const operation = this.availableOperations.find(op => op.id === step.id);
            if (!operation) return '';
            
            const isPreviewEnabled = this.previewSteps.has(index);
            const isFirstStep = index === 0;
            const isLastStep = index === this.steps.length - 1;
            
            return `
                <div class="pipeline-step">
                    <div class="step-header">
                        <div class="step-title">
                            <span class="step-number">${index + 1}</span>
                            <span class="step-icon">${operation.icon}</span>
                            <span class="step-name">${step.displayName}</span>
                        </div>
                        <div class="step-actions">
                            <button class="btn-icon-only move-btn ${isFirstStep ? 'disabled' : ''}"
                                    onclick="pipeline.moveStep(${index}, 'up')"
                                    title="Move up"
                                    ${isFirstStep ? 'disabled' : ''}>
                                ⬆️
                            </button>
                            <button class="btn-icon-only move-btn ${isLastStep ? 'disabled' : ''}"
                                    onclick="pipeline.moveStep(${index}, 'down')"
                                    title="Move down"
                                    ${isLastStep ? 'disabled' : ''}>
                                ⬇️
                            </button>
                            <button class="btn-icon-only save-step-btn"
                                    onclick="pipeline.saveStepOutput(${index})"
                                    title="Save step output">
                                💾
                            </button>
                            <button class="btn-icon-only preview-toggle ${isPreviewEnabled ? 'active' : ''}"
                                    onclick="pipeline.toggleStepPreview(${index})"
                                    title="${isPreviewEnabled ? 'Hide' : 'Show'} preview">
                                <span class="preview-icon">👁️</span>
                            </button>
                            <button class="btn-icon-only" 
                                    onclick="pipeline.removeStep(${index})"
                                    title="Remove step">
                            ❌
                        </button>
                    </div>
                    </div>
                    ${this.renderParamControls(operation, step.params, index)}
                    ${isPreviewEnabled ? this.renderStepPreview(index) : ''}
                </div>
            `;
        }).join('');

        // After rendering, scroll to the last step if it's not visible
        if (this.steps.length > 0) {
            const container = document.querySelector('.pipeline-container');
            const lastStep = container.lastElementChild;
            if (lastStep) {
                lastStep.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        }
    }

    renderParamControls(operation, currentParams, stepIndex) {
        if (!operation.params) return '';

        return `
            <div class="param-controls">
                ${Object.entries(operation.params).map(([key, config]) => {
                    const value = currentParams[key];
                    return this.renderParamControl(key, config, value, stepIndex);
                }).join('')}
            </div>
        `;
    }

    renderParamControl(key, config, value, stepIndex) {
        if (config.type === 'range') {
            return `
                <div class="param-group">
                    <div class="param-label">
                        <span class="param-name">${this.formatParamName(key)}</span>
                        <span class="param-value">${value}</span>
                    </div>
                    <input type="range"
                           class="param-slider"
                           min="${config.min}"
                           max="${config.max}"
                           step="1"
                           value="${value}"
                           oninput="pipeline.updateStepParams(${stepIndex}, {'${key}': parseInt(this.value, 10)}); 
                                   this.parentElement.querySelector('.param-value').textContent = this.value;">
                </div>
            `;
        } else if (config.type === 'select') {
            return `
                <div class="param-group">
                    <div class="param-label">
                        <span class="param-name">${this.formatParamName(key)}</span>
                    </div>
                    <select class="select-input"
                            onchange="pipeline.updateStepParams(${stepIndex}, {'${key}': this.value})">
                        ${config.options.map(option => `
                            <option value="${option}" ${value === option ? 'selected' : ''}>
                                ${this.formatParamName(option)}
                            </option>
                        `).join('')}
                    </select>
                </div>
            `;
        }
        return '';
    }

    formatParamName(name) {
        // Convert camelCase or snake_case to Title Case with spaces
        return name
            .replace(/([A-Z])/g, ' $1') // Add space before capital letters
            .replace(/_/g, ' ') // Replace underscores with spaces
            .replace(/^\w/, c => c.toUpperCase()) // Capitalize first letter
            .trim();
    }

    downloadResult(event) {
        // Prevent event bubbling
        event.preventDefault();
        event.stopPropagation();

        // Check if we're already downloading
        if (this.isDownloading) return;
        this.isDownloading = true;

        const processedPreview = document.getElementById('processed-preview');
        if (processedPreview && processedPreview.src) {
            // Create a temporary canvas to get the image data
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            
            // Set canvas dimensions to match the processed image
            canvas.width = processedPreview.naturalWidth;
            canvas.height = processedPreview.naturalHeight;
            
            // Draw only the processed image
            ctx.drawImage(processedPreview, 0, 0);
            
            // Convert to blob and download
            canvas.toBlob((blob) => {
                const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
                link.href = url;
            link.download = 'processed-image.png';
                
                // Use click() directly instead of adding to document
            link.click();
                
                // Clean up
                setTimeout(() => {
                    URL.revokeObjectURL(url);
                    this.isDownloading = false;
                }, 100);
            }, 'image/png');
        } else {
            this.isDownloading = false;
        }
    }

    renderStepPreview(stepIndex) {
        return `
            <div class="step-preview" id="preview-${stepIndex}">
                <div class="preview-image-container">
                    <img src="" alt="Step preview" class="preview-image" style="display: none;">
                    <div class="preview-loading" style="display: flex;">
                        <div class="loading-spinner"></div>
                    </div>
                </div>
            </div>
        `;
    }

    toggleStepPreview(stepIndex) {
        if (this.previewSteps.has(stepIndex)) {
            this.previewSteps.delete(stepIndex);
            const previewContainer = document.querySelector(`#preview-${stepIndex}`);
            if (previewContainer) {
                const previewImg = previewContainer.querySelector('.preview-image');
                if (previewImg && previewImg.src) {
                    URL.revokeObjectURL(previewImg.src);
                    previewImg.src = '';
                }
            }
            // Reset pipeline container height when removing preview
            this.adjustPipelineContainerHeight();
        } else {
            if (stepIndex < this.steps.length) {
                this.previewSteps.add(stepIndex);
            }
        }
        
        this.renderPipeline();
        
        // Process immediately without delay if needed
        if (this.currentImage && this.previewSteps.has(stepIndex)) {
            this.processImage();
            // Add a small delay to allow the image to load before adjusting height
            setTimeout(() => this.adjustPipelineContainerHeight(), 100);
        }
    }

    adjustPipelineContainerHeight() {
        const pipelineContainer = document.querySelector('.pipeline-container');
        const operationsSection = document.querySelector('.operations-section');
        
        if (!pipelineContainer || !operationsSection) return;

        // Reset to default height first
        pipelineContainer.style.maxHeight = '';
        
        // Check if there are any active previews
        const activePreviewImages = document.querySelectorAll('.step-preview .preview-image[src]:not([src=""])');
        
        if (activePreviewImages.length > 0) {
            // Calculate total content height
            const totalHeight = Array.from(activePreviewImages).reduce((height, img) => {
                const stepElement = img.closest('.pipeline-step');
                return height + (stepElement ? stepElement.offsetHeight : 0);
            }, 0);

            // Get the viewport height
            const viewportHeight = window.innerHeight;
            
            // Calculate the operations section position
            const operationsSectionRect = operationsSection.getBoundingClientRect();
            const availableHeight = viewportHeight - operationsSectionRect.top - 40; // 40px buffer
            
            // Set max height to either available viewport height or content height, whichever is larger
            const newMaxHeight = Math.max(availableHeight, totalHeight);
            pipelineContainer.style.maxHeight = `${newMaxHeight}px`;
        } else {
            // If no previews are active, reset to the initial height from data attribute
            const initialHeight = operationsSection.dataset.initialHeight;
            if (initialHeight) {
                pipelineContainer.style.maxHeight = `${initialHeight}px`;
            }
        }
    }

    moveStep(fromIndex, direction) {
        const toIndex = direction === 'up' ? fromIndex - 1 : fromIndex + 1;
        
        // Check if move is possible
        if (toIndex < 0 || toIndex >= this.steps.length) return;
        
        // Swap steps
        const step = this.steps.splice(fromIndex, 1)[0];
        this.steps.splice(toIndex, 0, step);
        
        // Update display names for all instances of affected operations
        const operationIds = new Set(this.steps.map(s => s.id));
        operationIds.forEach(opId => {
            const stepsWithOp = this.steps.filter(s => s.id === opId);
            const baseName = this.availableOperations.find(op => op.id === opId).name;
            stepsWithOp.forEach((s, i) => {
                s.displayName = i === 0 ? baseName : `${baseName} (${i + 1})`;
            });
        });

        this.renderPipeline();
        this.processImage();
    }

    // Add this new method for image size validation
    async validateImage(file) {
        // Check file size
        if (file.size > this.maxFileSize) {
            throw new Error(`Image file size must be less than ${this.maxFileSize / (1024 * 1024)}MB`);
        }

        // Check image dimensions
        return new Promise((resolve, reject) => {
            const img = new Image();
            const url = URL.createObjectURL(file);

            img.onload = () => {
                URL.revokeObjectURL(url); // Clean up the object URL
                if (img.width > this.maxImageSize || img.height > this.maxImageSize) {
                    reject(new Error(`Image dimensions must be ${this.maxImageSize}x${this.maxImageSize} pixels or smaller`));
                } else {
                    resolve(true);
                }
            };

            img.onerror = () => {
                URL.revokeObjectURL(url); // Clean up the object URL
                reject(new Error('Failed to load image for validation'));
            };

            img.src = url;
        });
    }

    cleanupPreviews() {
        // Clean up all preview images
        document.querySelectorAll('.preview-image').forEach(img => {
            if (img.src) {
                URL.revokeObjectURL(img.src);
                img.src = '';
                img.style.display = 'none';
            }
        });

        // Reset loading states
        document.querySelectorAll('.preview-loading').forEach(loader => {
            loader.style.display = 'none';
        });

        // Remove any error indicators
        document.querySelectorAll('.preview-error').forEach(error => {
            error.remove();
        });
    }

    updatePipelineStats() {
        const stepsCount = document.getElementById('steps-count');
        if (stepsCount) {
            stepsCount.textContent = `${this.steps.length} step${this.steps.length !== 1 ? 's' : ''}`;
        }
    }

    resetPipeline() {
        // Clear all steps
        this.steps = [];
        // Clear all previews
        this.previewSteps.clear();
        // Reset operation counts
        this.operationCounts = {};
        // Reset processed preview
        this.resetProcessedPreview();
        // Update UI
        this.updatePipelineStats();
        this.renderPipeline();
        
        // Update status based on current state
        if (this.currentImage) {
            this.updateProcessingStatus('add_steps');
        } else {
            this.updateProcessingStatus('waiting');
        }
        
        // Reset container height
        this.adjustPipelineContainerHeight();
    }

    resetProcessedPreview() {
        const processedPreview = document.getElementById('processed-preview');
        const compareProcessed = document.getElementById('compare-processed');
        
        if (processedPreview) {
            if (processedPreview.src) {
                URL.revokeObjectURL(processedPreview.src);
            }
            processedPreview.src = '';
            processedPreview.style.display = 'none';
            
            // Show placeholder if it exists
            const placeholder = processedPreview.previousElementSibling;
            if (placeholder) {
                placeholder.style.display = 'flex';
            }
        }

        if (compareProcessed) {
            if (compareProcessed.src) {
                URL.revokeObjectURL(compareProcessed.src);
            }
            compareProcessed.src = '';
            compareProcessed.style.display = 'none';
        }

        // Disable download buttons
        const downloadBtn = document.getElementById('download-btn');
        const downloadBtnCompare = document.getElementById('download-btn-compare');
        if (downloadBtn) {
            downloadBtn.disabled = true;
        }
        if (downloadBtnCompare) {
            downloadBtnCompare.disabled = true;
        }
    }

    async saveStepOutput(stepIndex) {
        if (!this.currentImage || !this.steps[stepIndex]) return;

        try {
            // Create a form data with just the steps up to this index
            const formData = new FormData();
            formData.append('image', this.currentImage);
            formData.append('pipeline', JSON.stringify(this.steps.slice(0, stepIndex + 1)));
            
            const response = await fetch('/api/process', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error('Failed to process step output');
            }
            
            const result = await response.json();
            
            if (result.success && result.image) {
                // Create a temporary link to download the image
                const link = document.createElement('a');
                link.href = result.image;
                link.download = `step_${stepIndex + 1}_output.png`;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }
        } catch (error) {
            console.error('Failed to save step output:', error);
            this.showError('Failed to save step output');
        }
    }

    resetImage() {
        // Clear current image
        if (this.currentImage) {
            URL.revokeObjectURL(this.currentImage);
            this.currentImage = null;
        }

        // Reset file input
        const fileInput = document.getElementById('file-input');
        if (fileInput) {
            fileInput.value = '';
        }

        // Reset original preview
        const originalPreview = document.getElementById('original-preview');
        const compareOriginal = document.getElementById('compare-original');
        if (originalPreview) {
            originalPreview.src = '';
            originalPreview.style.display = 'none';
            // Show placeholder
            const placeholder = originalPreview.previousElementSibling;
            if (placeholder) {
                placeholder.style.display = 'flex';
            }
        }
        if (compareOriginal) {
            compareOriginal.src = '';
            compareOriginal.style.display = 'none';
        }

        // Reset processed preview
        this.resetProcessedPreview();

        // Reset status
        this.updateProcessingStatus('waiting');

        // Disable download buttons
        const downloadBtn = document.getElementById('download-btn');
        const downloadBtnCompare = document.getElementById('download-btn-compare');
        if (downloadBtn) {
            downloadBtn.disabled = true;
        }
        if (downloadBtnCompare) {
            downloadBtnCompare.disabled = true;
        }

        // Disable compare button
        const compareBtn = document.getElementById('compare-btn');
        if (compareBtn) {
            compareBtn.disabled = true;
        }

        // Exit compare mode if active
        if (this.isCompareMode) {
            this.toggleCompareMode();
        }
    }

    setupPreviewToggle() {
        const toggleBtn = document.getElementById('toggle-previews');
        const previewContainer = document.getElementById('preview-container');
        const compareBtn = document.getElementById('compare-btn');
        
        if (toggleBtn && previewContainer) {
            // Set initial state
            this.previewsVisible = true;
            this.updatePreviewToggleState(toggleBtn, this.previewsVisible);

            toggleBtn.addEventListener('click', () => {
                this.previewsVisible = !this.previewsVisible;
                previewContainer.classList.toggle('hidden', !this.previewsVisible);
                this.updatePreviewToggleState(toggleBtn, this.previewsVisible);
                
                // Disable compare button when previews are hidden
                if (compareBtn) {
                    compareBtn.disabled = !this.previewsVisible || !this.currentImage;
                }
            });
        }

        // Setup compare button
        if (compareBtn) {
            compareBtn.addEventListener('click', () => {
                this.toggleCompareMode();
            });
        }
    }

    updatePreviewToggleState(toggleBtn, isVisible) {
        const btnText = toggleBtn.querySelector('.btn-text');
        const btnIcon = toggleBtn.querySelector('.btn-icon');
        if (btnText && btnIcon) {
            btnText.textContent = isVisible ? 'Hide Previews' : 'Show Previews';
            btnIcon.textContent = isVisible ? '👁️' : '👁️‍🗨️';
        }
    }

    toggleCompareMode() {
        this.isCompareMode = !this.isCompareMode;
        const normalMode = document.getElementById('normal-preview-mode');
        const compareMode = document.getElementById('compare-preview-mode');
        const compareBtn = document.getElementById('compare-btn');

        if (this.isCompareMode) {
            // Switch to compare mode
            normalMode.classList.add('hidden');
            compareMode.classList.remove('hidden');
            compareBtn.querySelector('.btn-text').textContent = 'Exit Compare';
            
            // Setup compare view
            this.setupCompareView();

            // Enable/disable download buttons based on processed image
            const processedPreview = document.getElementById('processed-preview');
            const downloadBtnCompare = document.getElementById('download-btn-compare');
            if (downloadBtnCompare) {
                downloadBtnCompare.disabled = !processedPreview.src;
            }
        } else {
            // Switch back to normal mode
            normalMode.classList.remove('hidden');
            compareMode.classList.add('hidden');
            compareBtn.querySelector('.btn-text').textContent = 'Compare';
            
            // Cleanup compare view
            this.cleanupCompareView();
        }
    }

    setupCompareView() {
        const originalImg = document.getElementById('compare-original');
        const processedImg = document.getElementById('compare-processed');
        const originalPreview = document.getElementById('original-preview');
        const processedPreview = document.getElementById('processed-preview');

        // Copy images to compare view
        originalImg.src = originalPreview.src;
        processedImg.src = processedPreview.src;
        originalImg.style.display = 'block';
        processedImg.style.display = 'block';

        // Setup slider
        const container = document.querySelector('.compare-container');
        const slider = document.querySelector('.compare-slider');
        const processedSide = document.querySelector('.compare-image.processed');

        // Initialize slider position
        this.updateSliderPosition(50);

        // Setup event listeners
        container.addEventListener('mousedown', this.startDragging.bind(this));
        document.addEventListener('mousemove', this.handleDrag.bind(this));
        document.addEventListener('mouseup', this.stopDragging.bind(this));
        
        // Touch events
        container.addEventListener('touchstart', this.startDragging.bind(this));
        document.addEventListener('touchmove', this.handleDrag.bind(this));
        document.addEventListener('touchend', this.stopDragging.bind(this));
    }

    startDragging(e) {
        this.isDragging = true;
        // Prevent image dragging
        e.preventDefault();
    }

    handleDrag(e) {
        if (!this.isDragging) return;

        const container = document.querySelector('.compare-container');
        const containerRect = container.getBoundingClientRect();
        
        // Get X position for either mouse or touch event
        const clientX = e.type.startsWith('touch') ? 
            e.touches[0].clientX : e.clientX;
        
        // Calculate percentage
        let percentage = ((clientX - containerRect.left) / containerRect.width) * 100;
        
        // Clamp percentage between 0 and 100
        percentage = Math.max(0, Math.min(100, percentage));
        
        this.updateSliderPosition(percentage);
    }

    stopDragging() {
        this.isDragging = false;
    }

    updateSliderPosition(percentage) {
        const slider = document.querySelector('.compare-slider');
        const processedSide = document.querySelector('.compare-image.processed');
        
        if (slider && processedSide) {
            this.compareSliderPosition = percentage;
            slider.style.left = `${percentage}%`;
            processedSide.style.clipPath = `inset(0 0 0 ${percentage}%)`;
        }
    }

    cleanupCompareView() {
        // Remove event listeners
        const container = document.querySelector('.compare-container');
        if (container) {
            container.removeEventListener('mousedown', this.startDragging.bind(this));
            container.removeEventListener('touchstart', this.startDragging.bind(this));
        }
        document.removeEventListener('mousemove', this.handleDrag.bind(this));
        document.removeEventListener('touchmove', this.handleDrag.bind(this));
        document.removeEventListener('mouseup', this.stopDragging.bind(this));
        document.removeEventListener('touchend', this.stopDragging.bind(this));
    }
}

// Initialize pipeline when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.pipeline = new Pipeline();
    pipeline.init();
}); 