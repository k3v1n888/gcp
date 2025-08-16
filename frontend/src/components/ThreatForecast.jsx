

/*
Copyright (c) 2025 Kevin Zachary
All rights reserved.

This software and associated documentation files (the "Software") are the 
exclusive property of Kevin Zachary. The Software is protected by copyright 
laws and international copyright treaties, as well as other intellectual 
property laws and treaties.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
KEVIN ZACHARY BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER 
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN 
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Unauthorized copying, modification, distribution, or use of this software, 
via any medium, is strictly prohibited without the express written permission 
of Kevin Zachary.
*/

import React, { useState, useEffect } from 'react';
import { getApiBaseUrl } from '../utils/environment';

export default function ThreatForecast() {
  const [forecast, setForecast] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const apiBaseUrl = getApiBaseUrl();
    fetch(`${apiBaseUrl}/api/forecasting/24_hour`)
      .then(res => res.json())
      .then(data => {
        setForecast(data);
      })
      .catch(() => {
        setForecast({ 
          error: 'Failed to load forecast',
          predicted_threats: {},
          method: 'error_fallback'
        });
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, []);

  const getMethodLabel = (method) => {
    switch(method) {
      case 'ml_based': return 'AI/ML Prediction';
      case 'statistical': return 'Statistical Analysis';
      case 'mock': return 'Demo Mode';
      case 'emergency_fallback': return 'System Fallback';
      default: return 'Threat Analysis';
    }
  };

  const formatProbability = (score) => {
    if (typeof score !== 'number') return '';
    
    // Handle different score formats
    if (score > 100) {
      // Score is already a percentage > 100, likely needs normalization
      return `(${Math.round(score / 100)}% probability)`;
    } else if (score > 1) {
      // Score is already a percentage
      return `(${Math.round(score)}% probability)`;
    } else {
      // Score is a decimal between 0-1, convert to percentage
      return `(${Math.round(score * 100)}% probability)`;
    }
  };

  const renderContent = () => {
    if (isLoading) {
      return <p className="text-sm text-gray-500">Generating 24-hour forecast...</p>;
    }
    
    // Handle the case where predicted_threats exists but is empty
    if (!forecast?.predicted_threats || Object.keys(forecast.predicted_threats).length === 0) {
      if (forecast?.error && forecast?.method !== 'mock') {
        return <p className="text-sm text-red-500">{forecast.error}</p>;
      }
      return <p className="text-sm text-gray-500">No significant threats predicted in the next 24 hours.</p>;
    }
    
    return (
      <div>
        <ul className="list-disc list-inside space-y-1 text-sm text-gray-700 mb-3">
          {Object.entries(forecast.predicted_threats).map(([threat, score]) => (
            <li key={threat}>
              <span className="font-medium">{threat}</span>
              {typeof score === 'number' && (
                <span className="text-gray-500 ml-2">
                  {formatProbability(score)}
                </span>
              )}
            </li>
          ))}
        </ul>
        {forecast.method && (
          <div className="text-xs text-gray-400 border-t pt-2">
            Method: {getMethodLabel(forecast.method)}
            {forecast.warning && (
              <div className="text-amber-600 mt-1">{forecast.warning}</div>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md mb-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mr-2 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
        </svg>
        Predicted Threats (Next 24 Hours)
      </h2>
      {renderContent()}
    </div>
  );
}
