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



import React, { useState, useEffect } from 'react';

export default function SecurityOutlook() {
  const [forecast, setForecast] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);

  useEffect(() => {
    const fetchForecast = () => {
      fetch(`${process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8001'}/api/forecasting/24_hour`)
        .then(res => res.json())
        .then(data => {
          setForecast(data);
          setLastUpdate(new Date());
        })
        .catch(() => {
          setForecast({ 
            error: 'Failed to load forecast',
            predicted_threats: {},
            method: 'error_fallback'
          });
          setLastUpdate(new Date());
        })
        .finally(() => {
          setIsLoading(false);
        });
    };

    fetchForecast();
    // Auto-refresh every 10 minutes
    const interval = setInterval(fetchForecast, 10 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const calculateThreatLevel = () => {
    if (!forecast?.predicted_threats) return { level: 'LOW', color: 'green' };
    
    const threats = Object.values(forecast.predicted_threats);
    if (threats.length === 0) return { level: 'LOW', color: 'green' };
    
    const maxThreat = Math.max(...threats.map(t => typeof t === 'number' ? (t > 1 ? t/100 : t) : 0));
    
    if (maxThreat > 0.15) return { level: 'HIGH', color: 'red' };
    if (maxThreat > 0.08) return { level: 'MEDIUM', color: 'yellow' };
    return { level: 'LOW', color: 'green' };
  };

  const getStatusMessage = (level) => {
    switch(level) {
      case 'HIGH': return 'Elevated threat activity detected';
      case 'MEDIUM': return 'Moderate security activity observed';
      case 'LOW': return 'Normal security posture maintained';
      default: return 'Security status evaluation in progress';
    }
  };

  const getWhatThisMeans = (level, threatCount) => {
    switch(level) {
      case 'HIGH': return `Higher than normal security activity detected.`;
      case 'MEDIUM': return `Moderate increase in security events observed.`;
      case 'LOW': return `Security operations within normal parameters.`;
      default: return 'Evaluating current security posture...';
    }
  };

  const getAreasToMonitor = () => {
    if (!forecast?.predicted_threats) return [];
    
    const threats = Object.entries(forecast.predicted_threats);
    const areas = [];
    
    threats.forEach(([threat, score]) => {
      const normalizedScore = typeof score === 'number' ? (score > 1 ? score/100 : score) : 0;
      let category = 'General Security';
      let status = 'Low Chance';
      
      // Categorize threats
      if (threat.toLowerCase().includes('powershell') || threat.toLowerCase().includes('command')) {
        category = 'Endpoint Security';
      } else if (threat.toLowerCase().includes('login') || threat.toLowerCase().includes('auth')) {
        category = 'Identity & Access';
      } else if (threat.toLowerCase().includes('network') || threat.toLowerCase().includes('traffic')) {
        category = 'Network Monitoring';
      } else if (threat.toLowerCase().includes('sql') || threat.toLowerCase().includes('injection')) {
        category = 'Web Application Security';
      } else if (threat.toLowerCase().includes('log4j') || threat.toLowerCase().includes('exploit')) {
        category = 'Vulnerability Management';
      }
      
      // Determine status
      if (normalizedScore > 0.15) status = 'High Chance';
      else if (normalizedScore > 0.08) status = 'Medium Chance';
      else status = 'Low Chance';
      
      areas.push({
        category,
        description: threat,
        status,
        score: normalizedScore,
        details: `${Math.round(normalizedScore * 100)}% probability`
      });
    });
    
    // Add default areas if no threats detected
    if (areas.length === 0) {
      areas.push(
        { category: 'Email Security', description: 'Routine email filtering active', status: 'Low Chance', details: 'Normal operations' },
        { category: 'Network Monitoring', description: 'Standard network monitoring', status: 'Low Chance', details: 'Routine activity' }
      );
    }
    
    return areas.slice(0, 4); // Limit to 4 areas
  };

  const getRecommendedActions = (level) => {
    const baseActions = [
      { text: 'Continue normal security practices', completed: true },
      { text: 'Maintain regular system updates', completed: false },
      { text: 'Verify backup systems are functioning', completed: false }
    ];
    
    if (level === 'HIGH') {
      return [
        { text: 'Review and validate all recent security alerts', completed: false },
        { text: 'Increase monitoring frequency for critical systems', completed: false },
        { text: 'Verify incident response team readiness', completed: false },
        ...baseActions
      ];
    } else if (level === 'MEDIUM') {
      return [
        { text: 'Review recent security events and patterns', completed: false },
        { text: 'Validate security controls are functioning properly', completed: false },
        ...baseActions
      ];
    }
    
    return baseActions;
  };

  if (isLoading) {
    return (
      <div className="bg-slate-800 text-slate-100 p-6 rounded-lg shadow-lg animate-pulse">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-6 h-6 bg-slate-600 rounded"></div>
          <div className="h-6 bg-slate-600 rounded w-48"></div>
        </div>
        <div className="space-y-4">
          <div className="h-4 bg-slate-600 rounded w-full"></div>
          <div className="h-4 bg-slate-600 rounded w-3/4"></div>
        </div>
      </div>
    );
  }

  const threatLevel = calculateThreatLevel();
  const threatCount = forecast?.predicted_threats ? Object.keys(forecast.predicted_threats).length : 0;
  const areasToMonitor = getAreasToMonitor();
  const recommendedActions = getRecommendedActions(threatLevel.level);

  const getColorClasses = (color) => {
    switch(color) {
      case 'red': return 'bg-red-600 text-white border-red-500';
      case 'yellow': return 'bg-yellow-500 text-black border-yellow-400';
      case 'green': return 'bg-green-600 text-white border-green-500';
      default: return 'bg-slate-600 text-white border-slate-500';
    }
  };

  const getStatusClasses = (status) => {
    switch(status) {
      case 'High Chance': return 'bg-red-500 text-white';
      case 'Medium Chance': return 'bg-yellow-500 text-black';
      case 'Low Chance': return 'bg-green-500 text-white';
      default: return 'bg-slate-500 text-white';
    }
  };

  return (
    <div className="bg-slate-800 text-slate-100 p-6 rounded-lg shadow-lg">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="w-6 h-6 bg-blue-500 rounded flex items-center justify-center">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.031 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold">24-Hour Security Outlook</h2>
        </div>
        <button className="text-slate-400 hover:text-slate-200">
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>

      {/* Current Status */}
      <div className="flex items-center space-x-4 mb-6">
        <div className={`w-4 h-4 rounded-full ${threatLevel.color === 'red' ? 'bg-red-500' : threatLevel.color === 'yellow' ? 'bg-yellow-500' : 'bg-green-500'}`}></div>
        <div>
          <div className="flex items-center space-x-2">
            <span className={`px-3 py-1 rounded text-sm font-bold ${getColorClasses(threatLevel.color)}`}>
              {threatLevel.level}
            </span>
            <span className="text-sm font-medium">Current Status</span>
          </div>
          <p className="text-slate-400 text-sm mt-1">{getStatusMessage(threatLevel.level)}</p>
        </div>
      </div>

      {/* What This Means */}
      <div className="bg-slate-700 p-4 rounded-lg mb-6">
        <div className="flex items-center space-x-2 mb-2">
          <svg className="w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 className="font-medium">What This Means</h3>
        </div>
        <p className="text-slate-300 text-sm">{getWhatThisMeans(threatLevel.level, threatCount)}</p>
        <p className="text-slate-400 text-xs mt-1">Based on {threatCount} recent security events</p>
      </div>

      {/* Areas to Monitor */}
      <div className="mb-6">
        <div className="flex items-center space-x-2 mb-3">
          <svg className="w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
          </svg>
          <h3 className="font-medium">Areas to Monitor</h3>
        </div>
        <div className="space-y-3">
          {areasToMonitor.map((area, index) => (
            <div key={index} className="bg-slate-700 p-3 rounded flex items-center justify-between">
              <div>
                <h4 className="font-medium text-sm">{area.category}</h4>
                <p className="text-slate-400 text-xs">{area.description}</p>
                <p className="text-slate-500 text-xs">{area.details}</p>
              </div>
              <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusClasses(area.status)}`}>
                {area.status}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Recommended Actions */}
      <div className="mb-4">
        <div className="flex items-center space-x-2 mb-3">
          <svg className="w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 className="font-medium">Recommended Actions</h3>
        </div>
        <div className="space-y-2">
          {recommendedActions.slice(0, 3).map((action, index) => (
            <div key={index} className="flex items-start space-x-2">
              <div className={`w-4 h-4 rounded-sm mt-0.5 flex-shrink-0 ${action.completed ? 'bg-green-500' : 'border border-slate-500'} flex items-center justify-center`}>
                {action.completed && (
                  <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                  </svg>
                )}
              </div>
              <span className="text-sm text-slate-300">{action.text}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="flex justify-between items-center text-xs text-slate-400 pt-4 border-t border-slate-600">
        <div className="flex items-center space-x-1">
          <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>Updated: {lastUpdate ? lastUpdate.toLocaleTimeString() : 'Loading...'}</span>
          <span className="ml-2">Next update in 10 minutes</span>
        </div>
        <span>Based on {threatCount} recent events</span>
      </div>
    </div>
  );
}
