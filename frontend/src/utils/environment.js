// Environment detection utility
export const isDevelopment = () => {
  // Check if we're running on the VM (development environment)
  const hostname = window.location.hostname;
  const isDev = hostname === '192.168.64.13' || hostname === 'localhost';
  
  // Also check for dev mode parameter
  const urlParams = new URLSearchParams(window.location.search);
  const devMode = urlParams.get('dev_mode') === 'true';
  
  return isDev || devMode || process.env.NODE_ENV === 'development';
};

export const getApiBaseUrl = () => {
  if (isDevelopment()) {
    return 'http://192.168.64.13:8000';
  }
  return window.location.origin;
};
