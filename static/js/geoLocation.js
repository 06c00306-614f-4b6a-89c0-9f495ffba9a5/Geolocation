/**
 * Geolocation Module
 */
const GeoLocation = {
    watchId: null,
    lastPosition: null,
    
    /**
     * Get geolocation with specified mode
     * @param {string} mode - 'single' for one-time position or 'watch' for continuous tracking
     * @param {Function} successCallback - Called when location is successfully gathered
     * @param {Function} errorCallback - Called when there's an error getting location
     * @param {number} timeout - Optional timeout in ms (default: 10000)
     */
    getLocation: function(mode, successCallback, errorCallback, timeout = 10000) {
        if (!navigator.geolocation) {
            const error = {
                code: 0,
                message: "Geolocation is not supported by this browser."
            };
            errorCallback && errorCallback(error);
            return;
        }
        
        const options = {
            enableHighAccuracy: true,
            timeout: timeout,
            maximumAge: 0
        };
        
        if (mode === 'watch') {
            // Clear any existing watch
            this.clearWatch();
            
            // Start continuous location tracking
            this.watchId = navigator.geolocation.watchPosition(
                (position) => {
                    this.lastPosition = position;
                    successCallback && successCallback(position);
                },
                (error) => {
                    errorCallback && errorCallback(error);
                },
                options
            );
        } else {
            // One-time location request
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    this.lastPosition = position;
                    successCallback && successCallback(position);
                },
                (error) => {
                    errorCallback && errorCallback(error);
                },
                options
            );
        }
    },
    
    /**
     * Stop watching for location updates
     */
    clearWatch: function() {
        if (this.watchId !== null) {
            navigator.geolocation.clearWatch(this.watchId);
            this.watchId = null;
        }
    },
    
    /**
     * Get last known position
     * @returns {Object|null} Position object or null if no position available
     */
    getLastPosition: function() {
        return this.lastPosition;
    },
    
    /**
     * Format position data for submission
     * @param {Object} position - The position object from geolocation API
     * @returns {Object} Formatted position data
     */
    formatPositionData: function(position) {
        if (!position || !position.coords) {
            return {
                geolocationStatus: 'error',
                geolocationError: 'Invalid position data'
            };
        }
        
        return {
            geolocationStatus: 'success',
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
            altitude: position.coords.altitude,
            altitudeAccuracy: position.coords.altitudeAccuracy,
            heading: position.coords.heading,
            speed: position.coords.speed,
            timestamp: position.timestamp
        };
    },
    
    /**
     * Format error data for submission
     * @param {Object} error - The error object from geolocation API
     * @returns {Object} Formatted error data
     */
    formatErrorData: function(error) {
        let errorMessage = "Unknown error";
        
        switch(error.code) {
            case 1:
                errorMessage = "Permission denied";
                break;
            case 2:
                errorMessage = "Position unavailable";
                break;
            case 3:
                errorMessage = "Timeout";
                break;
        }
        
        return {
            geolocationStatus: 'error',
            geolocationError: errorMessage,
            errorCode: error.code,
            errorMessage: error.message || errorMessage
        };
    }
};
