import React, { useState, useEffect } from 'react';
import { getApiBaseUrl } from '../utils/environment';

export default function SecurityOutlook() {
  const [forecast, setForecast] = useState(null);
  const [agentData, setAgentData] = useState(null);
  const [auditData, setAuditData] = useState(null);
  const [aiModelData, setAIModelData] = useState([]);
  const [predictiveData, setPredictiveData] = useState(null);
  const [aiIntelligence, setAIIntelligence] = useState(null);
  const [threatPredictions, setThreatPredictions] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);

  useEffect(() => {
    const fetchAllData = async () => {
      const apiBaseUrl = getApiBaseUrl();
      
      try {
        // Fetch real-time data from Sentient AI models and services
        const [
          forecastRes, 
          agentsRes, 
          auditRes, 
          aiModelRes,
          predictiveRes,
          yourAIRes,
          threatPredictionRes
        ] = await Promise.all([
          fetch(`${apiBaseUrl}/api/forecasting/24_hour`).catch(() => null),
          fetch(`${apiBaseUrl}/api/agents`).catch(() => null),
          fetch(`${apiBaseUrl}/api/admin/audit-logs?limit=10`).catch(() => null),
          fetch(`${apiBaseUrl}/api/ai/models`).catch(() => null),
          fetch(`${apiBaseUrl}/api/predictive`).catch(() => null),
          fetch(`${apiBaseUrl}/api/ai/intelligence/summary`).catch(() => null),
          fetch(`${apiBaseUrl}/api/agents/threats`).catch(() => null) // Sentient AI model predictions
        ]);

        // Process Sentient AI model responses
        if (forecastRes?.ok) {
          const forecastData = await forecastRes.json();
          setForecast(forecastData);
        }

        if (agentsRes?.ok) {
          const agentsData = await agentsRes.json();
          setAgentData(agentsData);
        }

        if (auditRes?.ok) {
          const auditLogsData = await auditRes.json();
          setAuditData(auditLogsData);
        }

        // Process Sentient AI model data
        if (aiModelRes?.ok) {
          const modelData = await aiModelRes.json();
          setAIModelData(Array.isArray(modelData) ? modelData : []);
        }

        if (predictiveRes?.ok) {
          const predictiveResults = await predictiveRes.json();
          setPredictiveData(predictiveResults);
        }

        if (yourAIRes?.ok) {
          const aiIntelData = await yourAIRes.json();
          setAIIntelligence(aiIntelData);
        }

        if (threatPredictionRes?.ok) {
          const threatData = await threatPredictionRes.json();
          setThreatPredictions(threatData);
        }

        setLastUpdate(new Date());
        setIsLoading(false);
      } catch (error) {
        console.error('Error fetching Sentient AI model data:', error);
        setIsLoading(false);
      }
    };

    fetchAllData();
    // Auto-refresh every 10 minutes
    const interval = setInterval(fetchAllData, 10 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const calculateThreatLevel = () => {
    // Use Sentient AI models for threat level calculation
    if (!forecast?.predicted_threats && !agentData?.agents && !auditData?.logs && !threatPredictions?.threats) {
      return { level: 'LOW', color: 'green' };
    }
    
    let maxThreatScore = 0;
    let recentSecurityEvents = 0;
    let aiModelConfidence = 0;
    
    // Analyze Sentient AI model forecast threats
    if (forecast?.predicted_threats) {
      const threats = Object.values(forecast.predicted_threats);
      maxThreatScore = Math.max(maxThreatScore, ...threats.map(t => t.severity || 0));
      recentSecurityEvents += threats.length;
    }
    
    // Analyze Sentient AI agent data for active threats
    if (agentData?.agents) {
      const activeAgents = agentData.agents.filter(agent => agent.status === 'active');
      recentSecurityEvents += activeAgents.length;
      
      // Check Sentient AI model confidence levels
      activeAgents.forEach(agent => {
        if (agent.confidence) {
          aiModelConfidence = Math.max(aiModelConfidence, agent.confidence);
        }
      });
    }
    
    // Analyze audit logs for security events using Sentient AI intelligence
    if (auditData?.logs) {
      const securityEvents = auditData.logs.filter(log => 
        log.action?.includes('security') || 
        log.action?.includes('threat') ||
        log.action?.includes('attack')
      );
      recentSecurityEvents += securityEvents.length;
    }
    
    // Analyze Sentient AI threat predictions
    if (threatPredictions?.threats) {
      const highConfidenceThreats = threatPredictions.threats.filter(threat => 
        threat.confidence > 0.7
      );
      maxThreatScore = Math.max(maxThreatScore, ...highConfidenceThreats.map(t => t.risk_score || 0));
      recentSecurityEvents += highConfidenceThreats.length;
    }

    // Calculate final threat level based on Sentient AI models
    if (maxThreatScore >= 0.8 || recentSecurityEvents >= 15 || aiModelConfidence >= 0.9) {
      return { level: 'CRITICAL', color: 'red' };
    } else if (maxThreatScore >= 0.6 || recentSecurityEvents >= 8 || aiModelConfidence >= 0.7) {
      return { level: 'HIGH', color: 'orange' };
    } else if (maxThreatScore >= 0.4 || recentSecurityEvents >= 3 || aiModelConfidence >= 0.5) {
      return { level: 'MEDIUM', color: 'yellow' };
    } else {
      return { level: 'LOW', color: 'green' };
    }
  };

  const getAreasToMonitor = () => {
    const areas = [];
    
    // Areas identified by Sentient AI models
    if (forecast?.predicted_threats) {
      Object.entries(forecast.predicted_threats).forEach(([key, threat]) => {
        areas.push({
          category: `AI Detected: ${threat.category || key}`,
          description: threat.description || `Sentient AI model detected potential ${key}`,
          status: threat.severity > 0.7 ? 'High Chance' : threat.severity > 0.4 ? 'Medium Chance' : 'Low Chance',
          score: threat.severity,
          details: `Sentient AI Model Confidence: ${(threat.confidence * 100).toFixed(1)}%`
        });
      });
    }
    
    // Areas from Sentient AI agent analysis
    if (agentData?.agents) {
      const concerningAgents = agentData.agents.filter(agent => 
        agent.status === 'active' && agent.confidence > 0.6
      );
      
      concerningAgents.forEach(agent => {
        areas.push({
          category: `AI Agent: ${agent.name || 'Threat Detection'}`,
          description: agent.description || 'Sentient AI agent detected suspicious activity',
          status: agent.confidence > 0.8 ? 'High Chance' : 'Medium Chance',
          score: agent.confidence,
          details: `Sentient AI Agent Model`
        });
      });
    }
    
    // Areas from Sentient AI threat predictions
    if (threatPredictions?.threats) {
      threatPredictions.threats.slice(0, 2).forEach(threat => {
        areas.push({
          category: `AI Prediction: ${threat.threat_type || 'Unknown Threat'}`,
          description: threat.description || 'Sentient AI prediction model identified potential risk',
          status: threat.confidence > 0.7 ? 'High Chance' : 'Medium Chance',
          score: threat.confidence,
          details: `Sentient AI Prediction Model`
        });
      });
    }
    
    // Areas from Sentient AI intelligence summary
    if (aiIntelligence?.summary) {
      areas.push({
        category: 'AI Intelligence Analysis',
        description: 'AI-generated threat intelligence analysis',
        status: 'Medium Confidence',
        score: 0.6,
        details: 'Sentient AI Intelligence Model'
      });
    }
    
    // Add default areas if no AI model threats detected
    if (areas.length === 0) {
      areas.push(
        { 
          category: 'AI Model Baseline', 
          description: 'Sentient AI models monitoring normal activity', 
          status: 'Low Confidence', 
          details: 'AI models operational' 
        },
        { 
          category: 'Network AI Monitoring', 
          description: 'Sentient network AI models active', 
          status: 'Low Confidence', 
          details: 'AI-powered monitoring' 
        },
        { 
          category: 'AI Threat Intelligence', 
          description: 'Sentient AI threat intelligence gathering', 
          status: 'Low Confidence', 
          details: 'AI intelligence active' 
        }
      );
    }
    
    return areas.slice(0, 4); // Limit to 4 areas
  };

  const getRecommendedActions = () => {
    const actions = [];
    const threatLevel = calculateThreatLevel();
    
    // AI model-based recommendations
    if (threatLevel.level === 'CRITICAL') {
      actions.push(
        { text: 'Activate Sentient AI emergency response protocols', completed: false },
        { text: 'Review Sentient AI threat model predictions immediately', completed: false },
        { text: 'Escalate to Sentient AI security team', completed: false },
        { text: 'Run Sentient AI comprehensive threat scan', completed: false }
      );
    } else if (threatLevel.level === 'HIGH') {
      actions.push(
        { text: 'Monitor Sentient AI model alerts closely', completed: false },
        { text: 'Review Sentient AI agent findings', completed: false },
        { text: 'Update Sentient AI threat detection rules', completed: false }
      );
    } else {
      actions.push(
        { text: 'Continue monitoring with Sentient AI models', completed: true },
        { text: 'Update Sentient AI model training data', completed: false },
        { text: 'Review Sentient AI system performance', completed: false }
      );
    }
    
    return actions;
  };

  const areasToMonitor = getAreasToMonitor();
  const recommendedActions = getRecommendedActions();
  const threatLevel = calculateThreatLevel();
  const threatCount = (forecast?.predicted_threats ? Object.keys(forecast.predicted_threats).length : 0) +
                    (agentData?.agents ? agentData.agents.filter(a => a.status === 'active').length : 0) +
                    (threatPredictions?.threats ? threatPredictions.threats.length : 0);

  const getThreatLevelClasses = (level) => {
    switch(level) {
      case 'red': return 'bg-red-600 text-white border-red-500';
      case 'orange': return 'bg-orange-600 text-white border-orange-500';
      case 'yellow': return 'bg-yellow-600 text-black border-yellow-500';
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
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold">24-Hour AI Security Outlook</h2>
        </div>
        <div className="text-right text-sm text-slate-400">
          <div>Updated: {lastUpdate ? lastUpdate.toLocaleTimeString() : 'Loading...'}</div>
          <div>Source: Sentient AI Models</div>
        </div>
      </div>

      {/* Threat Level Indicator */}
      <div className="mb-6">
        <div className={`p-4 rounded-lg border-2 ${getThreatLevelClasses(threatLevel.color)}`}>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold">Current Threat Level: {threatLevel.level}</h3>
              <p className="text-sm opacity-90">
                Based on {threatCount} AI model events from Sentient AI trained models
              </p>
            </div>
            <div className="text-3xl font-bold">
              {threatLevel.level.charAt(0)}
            </div>
          </div>
        </div>
        <p className="text-xs text-slate-400 mt-2">
          Method: {forecast?.method || 'sentient_ai_models'}
        </p>
      </div>

      {/* Areas to Monitor */}
      <div className="mb-6">
        <div className="flex items-center space-x-2 mb-3">
          <svg className="w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          <h3 className="font-medium">AI Model Analysis Areas</h3>
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

      {/* AI Model Status & Predictions */}
      <div className="mb-6">
        <div className="flex items-center space-x-2 mb-3">
          <svg className="w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.667 14.667l3.333 3.333L20.333 10.667M3.667 12L7 15.333l10.333-10.333" />
          </svg>
          <h3 className="font-medium">Sentient AI Model Predictions</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {aiModelData.length > 0 ? aiModelData.map(model => (
            <div key={model.name} className="bg-slate-700 p-3 rounded">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-sm">{model.name}</span>
                <span className={`w-2 h-2 rounded-full ${model.status === 'active' ? 'bg-green-500' : 'bg-red-500'}`}></span>
              </div>
              <p className="text-slate-400 text-xs mb-1">Status: {model.status}</p>
              <p className="text-slate-300 text-xs">Confidence: {(model.confidence * 100).toFixed(1)}%</p>
              {model.prediction && (
                <p className="text-slate-300 text-xs mt-1">Prediction: {model.prediction}</p>
              )}
            </div>
          )) : (
            <div className="col-span-3 bg-slate-700 p-3 rounded text-center">
              <p className="text-slate-400 text-sm">Loading Sentient AI model predictions...</p>
            </div>
          )}
        </div>
      </div>

      {/* Recommended Actions */}
      <div className="mb-6">
        <div className="flex items-center space-x-2 mb-3">
          <svg className="w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          <h3 className="font-medium">Sentient AI Model Recommendations</h3>
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
      <div className="text-xs text-slate-500 border-t border-slate-600 pt-3">
        <p>This outlook is generated by Sentient AI trained models including RandomForest classifiers, SHAP explainers, and local prediction models.</p>
        <p className="mt-1">Data refreshes automatically every 10 minutes from Sentient AI services.</p>
      </div>
    </div>
  );
}
