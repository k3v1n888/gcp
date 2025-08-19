

import React from 'react';

const Card = ({ children, className = '', ...props }) => (
  <div 
    className={`bg-white shadow-lg rounded-lg border border-gray-200 ${className}`}
    {...props}
  >
    {children}
  </div>
);

const CardHeader = ({ children, className = '', ...props }) => (
  <div 
    className={`px-6 py-4 border-b border-gray-200 ${className}`}
    {...props}
  >
    {children}
  </div>
);

const CardTitle = ({ children, className = '', ...props }) => (
  <h3 
    className={`text-lg font-semibold text-gray-900 ${className}`}
    {...props}
  >
    {children}
  </h3>
);

const CardContent = ({ children, className = '', ...props }) => (
  <div 
    className={`px-6 py-4 ${className}`}
    {...props}
  >
    {children}
  </div>
);

export { Card, CardContent, CardHeader, CardTitle };
