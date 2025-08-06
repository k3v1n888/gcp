export const sanitizeApiResponse = (data) => {
  if (Array.isArray(data)) {
    return data.map(item => sanitizeApiResponse(item));
  } else if (data !== null && typeof data === 'object') {
    const sanitized = {};
    for (const [key, value] of Object.entries(data)) {
      if (typeof value === 'number' && (isNaN(value) || !isFinite(value))) {
        if (key.includes('score') || key.includes('value') || key.includes('impact')) {
          sanitized[key] = 0;
        } else {
          sanitized[key] = null;
        }
      } else {
        sanitized[key] = sanitizeApiResponse(value);
      }
    }
    return sanitized;
  }
  return data;
};

export const formatNumber = (num, decimals = 2) => {
  if (num === null || num === undefined || isNaN(num) || !isFinite(num)) {
    return 'N/A';
  }
  return Number(num).toFixed(decimals);
};