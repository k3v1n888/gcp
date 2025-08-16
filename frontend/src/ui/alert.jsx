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



// Simple Alert components for development
import React from 'react';

export const Alert = ({ 
  children, 
  variant = 'default', 
  className = '' 
}) => {
  const baseClasses = 'p-4 rounded-md border';
  const variants = {
    default: 'bg-blue-50 border-blue-200 text-blue-800',
    destructive: 'bg-red-50 border-red-200 text-red-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    success: 'bg-green-50 border-green-200 text-green-800'
  };
  
  return (
    <div className={`${baseClasses} ${variants[variant]} ${className}`}>
      {children}
    </div>
  );
};

export const AlertDescription = ({ children, className = '' }) => (
  <div className={`text-sm ${className}`}>
    {children}
  </div>
);
