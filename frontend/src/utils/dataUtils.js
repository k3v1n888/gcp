/*
 * Copyright (c) 2025 Kevin Zachary
 * All rights reserved.
 *
 * This software and associated documentation files (the "Software") are the 
 * exclusive property of Kevin Zachary. Unauthorized copying, distribution, 
 * modification, or use of this software is strictly prohibited.
 *
 * For licensing inquiries, contact: kevin@zachary.com
 */

/*
 * Author: Kevin Zachary
 * Copyright: Sentient Spire
 */



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