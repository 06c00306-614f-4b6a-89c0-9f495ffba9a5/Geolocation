/**
 * Device Information Collection Module
 */
const DeviceInfo = {
    /**
     * Collects comprehensive device information
     * @returns {Object} Device information object
     */
    collect: function() {
        const deviceInfo = {};
        
        // Platform info
        deviceInfo.platform = navigator.platform || 'Not Available';
        deviceInfo.hardwareConcurrency = navigator.hardwareConcurrency || 'Not Available';
        deviceInfo.deviceMemory = navigator.deviceMemory || 'Not Available';
        deviceInfo.userAgent = navigator.userAgent;
        
        // Screen info
        deviceInfo.screenHeight = window.screen.height;
        deviceInfo.screenWidth = window.screen.width;
        
        // Browser detection
        deviceInfo.browser = this.detectBrowser();
        
        // OS detection
        deviceInfo.os = this.detectOS();
        
        // GPU info
        const gpuInfo = this.getGPUInfo();
        deviceInfo.gpuVendor = gpuInfo.vendor;
        deviceInfo.gpuRenderer = gpuInfo.renderer;
        
        return deviceInfo;
    },
    
    /**
     * Detects browser name and version
     * @returns {string} Browser info
     */
    detectBrowser: function() {
        let browserInfo = 'Not Available';
        const ua = navigator.userAgent;
        
        if (ua.indexOf('Firefox') !== -1) {
            browserInfo = 'Firefox ' + ua.match(/Firefox\/([0-9.]+)/)[1];
        } else if (ua.indexOf('Chrome') !== -1 && ua.indexOf('Edge') === -1 && ua.indexOf('Edg') === -1) {
            browserInfo = 'Chrome ' + ua.match(/Chrome\/([0-9.]+)/)[1];
        } else if (ua.indexOf('Safari') !== -1 && ua.indexOf('Chrome') === -1) {
            browserInfo = 'Safari ' + (ua.match(/Version\/([0-9.]+)/) ? ua.match(/Version\/([0-9.]+)/)[1] : 'Unknown');
        } else if (ua.indexOf('Edge') !== -1 || ua.indexOf('Edg') !== -1) {
            browserInfo = 'Edge ' + (ua.match(/Edge\/([0-9.]+)/) || ua.match(/Edg\/([0-9.]+)/) || ['', 'Unknown'])[1];
        } else if (ua.indexOf('Opera') !== -1 || ua.indexOf('OPR') !== -1) {
            browserInfo = 'Opera ' + (ua.match(/Opera\/([0-9.]+)/) || ua.match(/OPR\/([0-9.]+)/) || ['', 'Unknown'])[1];
        }
        
        return browserInfo;
    },
    
    /**
     * Detects operating system
     * @returns {string} OS name
     */
    detectOS: function() {
        let os = 'Not Available';
        const userAgent = navigator.userAgent;
        
        if (userAgent.indexOf("Win") !== -1) os = "Windows";
        else if (userAgent.indexOf("Mac") !== -1) os = "MacOS";
        else if (userAgent.indexOf("Linux") !== -1) os = "Linux";
        else if (userAgent.indexOf("Android") !== -1) os = "Android";
        else if (userAgent.indexOf("iPhone") !== -1 || userAgent.indexOf("iPad") !== -1 || userAgent.indexOf("iPod") !== -1) os = "iOS";
        
        return os;
    },
    
    /**
     * Gets GPU information using WebGL
     * @returns {Object} GPU vendor and renderer
     */
    getGPUInfo: function() {
        let gpuVendor = 'Not Available';
        let gpuRenderer = 'Not Available';
        
        try {
            const canvas = document.createElement('canvas');
            const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
            
            if (gl) {
                const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                if (debugInfo) {
                    gpuVendor = gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
                    gpuRenderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
                }
            }
        } catch (e) {
            // Silent fail
        }
        
        return {
            vendor: gpuVendor,
            renderer: gpuRenderer
        };
    }
};