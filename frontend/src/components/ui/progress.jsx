

import React from 'react';

const Progress = ({ 
  value = 0, 
  max = 100, 
  className = '', 
  showLabel = false,
  ...props 
}) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);
  
  return (
    <div className={`w-full ${className}`} {...props}>
      <div className="bg-gray-200 rounded-full h-2 overflow-hidden">
        <div 
          className="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-out"
          style={{ width: `${percentage}%` }}
        />
      </div>
      {showLabel && (
        <div className="text-sm text-gray-600 mt-1">
          {Math.round(percentage)}%
        </div>
      )}
    </div>
  );
};

export { Progress };
