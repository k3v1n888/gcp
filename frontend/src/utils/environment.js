

// Environment detection utility
export const isDevelopment = () => {
  // Primary detection: Check React environment variables set in docker-compose
  const reactDevMode = process.env.REACT_APP_DEV_MODE === 'true';
  const reactBypassAuth = process.env.REACT_APP_BYPASS_AUTH === 'true';
  
  // Secondary detection: Check hostname (VM detection)
  const hostname = window.location.hostname;
  const isVmHostname = hostname === '192.168.64.13' || hostname === 'localhost';
  
  // Tertiary detection: Check URL parameters
  const urlParams = new URLSearchParams(window.location.search);
  const devModeParam = urlParams.get('dev_mode') === 'true';
  
  // Development environment if any condition is true
  const result = reactDevMode || reactBypassAuth || isVmHostname || devModeParam || process.env.NODE_ENV === 'development';
  
  console.log('🔍 Environment detection:', {
    hostname,
    reactDevMode,
    reactBypassAuth,
    isVmHostname,
    devModeParam,
    nodeEnv: process.env.NODE_ENV,
    finalResult: result
  });
  
  return result;
};

export const getApiBaseUrl = () => {
  if (isDevelopment()) {
    return 'http://localhost:8001';
  }
  return window.location.origin;
};
