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



import React from 'react';

const Alert = ({ children, className = '', variant = 'default', ...props }) => {
  const baseClasses = 'relative rounded-lg border p-4 mb-4';
  
  const variants = {
    default: 'bg-gray-50 border-gray-200 text-gray-900',
    success: 'bg-green-50 border-green-200 text-green-900',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-900',
    error: 'bg-red-50 border-red-200 text-red-900',
    info: 'bg-blue-50 border-blue-200 text-blue-900'
  };
  
  return (
    <div 
      className={`${baseClasses} ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};

const AlertDescription = ({ children, className = '', ...props }) => {
  return (
    <div 
      className={`text-sm ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};

export { Alert, AlertDescription };
