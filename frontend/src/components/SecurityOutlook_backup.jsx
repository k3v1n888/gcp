

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
        // Fetch real-time data from YOUR AI models and services
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
          fetch(`${apiBaseUrl}/api/agents/threats`).catch(() => null) // Your trained model predictions
        ]);

        // Process YOUR AI model responses
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

        // Process YOUR AI model data
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
        console.error('Error fetching AI model data:', error);
        setIsLoading(false);
      }
    };

    fetchAllData();
    // Auto-refresh every 10 minutes
    const interval = setInterval(fetchAllData, 10 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const calculateThreatLevel = () => {
    // Use YOUR AI models for threat level calculation
    if (!forecast?.predicted_threats && !agentData?.agents && !auditData?.logs && !threatPredictions?.threats) {
      return { level: 'LOW', color: 'green' };
    }
    
    let maxThreatScore = 0;
    let recentSecurityEvents = 0;
    let aiModelConfidence = 0;
    
    // Analyze YOUR AI model forecast threats
    if (forecast?.predicted_threats) {
      const threats = Object.values(forecast.predicted_threats);
      maxThreatScore = Math.max(maxThreatScore, ...threats.map(t => t.severity || 0));
      recentSecurityEvents += threats.length;
    }
    
    // Analyze YOUR AI agent data for active threats
    if (agentData?.agents) {
      const activeAgents = agentData.agents.filter(agent => agent.status === 'active');
      recentSecurityEvents += activeAgents.length;
      
      // Check YOUR AI model confidence levels
      activeAgents.forEach(agent => {
        if (agent.confidence) {
          aiModelConfidence = Math.max(aiModelConfidence, agent.confidence);
        }
      });
    }
    
    // Analyze audit logs for security events using YOUR AI intelligence
    if (auditData?.logs) {
      const securityEvents = auditData.logs.filter(log => 
        log.action?.includes('security') || 
        log.action?.includes('threat') ||
        log.action?.includes('attack')
      );
      recentSecurityEvents += securityEvents.length;
    }
    
    // Analyze YOUR AI threat predictions
    if (threatPredictions?.threats) {
      const highConfidenceThreats = threatPredictions.threats.filter(threat => 
        threat.confidence > 0.7
      );
      maxThreatScore = Math.max(maxThreatScore, ...highConfidenceThreats.map(t => t.risk_score || 0));
      recentSecurityEvents += highConfidenceThreats.length;
    }

    // Calculate final threat level based on YOUR AI models
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
    
    // Areas identified by YOUR AI models
    if (forecast?.predicted_threats) {
      Object.entries(forecast.predicted_threats).forEach(([key, threat]) => {
        areas.push({
          category: `AI Detected: ${threat.category || key}`,
          description: threat.description || `YOUR AI model detected potential ${key}`,
          status: threat.severity > 0.7 ? 'High Chance' : threat.severity > 0.4 ? 'Medium Chance' : 'Low Chance',
          score: threat.severity,
          details: `YOUR AI Model Confidence: ${(threat.confidence * 100).toFixed(1)}%`
        });
      });
    }
    
    // Areas from YOUR AI agent analysis
    if (agentData?.agents) {
      const concerningAgents = agentData.agents.filter(agent => 
        agent.status === 'active' && agent.confidence > 0.6
      );
      
      concerningAgents.forEach(agent => {
        areas.push({
          category: `AI Agent: ${agent.name || 'Threat Detection'}`,
          description: agent.description || 'YOUR AI agent detected suspicious activity',
          status: agent.confidence > 0.8 ? 'High Chance' : 'Medium Chance',
          score: agent.confidence,
          details: `YOUR AI Agent Model`
        });
      });
    }
    
    // Areas from YOUR AI threat predictions
    if (threatPredictions?.threats) {
      threatPredictions.threats.slice(0, 2).forEach(threat => {
        areas.push({
          category: `AI Prediction: ${threat.threat_type || 'Unknown Threat'}`,
          description: threat.description || 'YOUR AI prediction model identified potential risk',
          status: threat.confidence > 0.7 ? 'High Chance' : 'Medium Chance',
          score: threat.confidence,
          details: `YOUR AI Prediction Model`
        });
      });
    }
    
    // Areas from YOUR AI intelligence summary
    if (aiIntelligence?.summary) {
      areas.push({
        category: 'AI Intelligence Analysis',
        description: 'AI-generated threat intelligence analysis',
        status: 'Medium Confidence',
        score: 0.6,
        details: 'YOUR AI Intelligence Model'
      });
    }
    
    // Add default areas if no AI model threats detected
    if (areas.length === 0) {
      areas.push(
        { 
          category: 'AI Model Baseline', 
          description: 'YOUR AI models monitoring normal activity', 
          status: 'Low Confidence', 
          details: 'AI models operational' 
        },
        { 
          category: 'Network AI Monitoring', 
          description: 'YOUR network AI models active', 
          status: 'Low Confidence', 
          details: 'AI-powered monitoring' 
        },
        { 
          category: 'AI Threat Intelligence', 
          description: 'YOUR AI threat intelligence gathering', 
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
        { text: 'Activate YOUR AI emergency response protocols', completed: false },
        { text: 'Review YOUR AI threat model predictions immediately', completed: false },
        { text: 'Escalate to YOUR AI security team', completed: false },
        { text: 'Run YOUR AI comprehensive threat scan', completed: false }
      );
    } else if (threatLevel.level === 'HIGH') {
      actions.push(
        { text: 'Monitor YOUR AI model alerts closely', completed: false },
        { text: 'Review YOUR AI agent findings', completed: false },
        { text: 'Update YOUR AI threat detection rules', completed: false }
      );
    } else {
      actions.push(
        { text: 'Continue monitoring with YOUR AI models', completed: true },
        { text: 'Update YOUR AI model training data', completed: false },
        { text: 'Review YOUR AI system performance', completed: false }
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
          <div>Source: YOUR AI Models</div>
        </div>
      </div>

      {/* Threat Level Indicator */}
      <div className="mb-6">
        <div className={`p-4 rounded-lg border-2 ${getThreatLevelClasses(threatLevel.color)}`}>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold">Current Threat Level: {threatLevel.level}</h3>
              <p className="text-sm opacity-90">
                Based on {threatCount} AI model events from YOUR trained models
              </p>
            </div>
            <div className="text-3xl font-bold">
              {threatLevel.level.charAt(0)}
            </div>
          </div>
        </div>
        <p className="text-xs text-slate-400 mt-2">
          Method: {forecast?.method || 'your_ai_models'}
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
          <h3 className="font-medium">Your AI Model Predictions</h3>
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
              <p className="text-slate-400 text-sm">Loading your AI model predictions...</p>
            </div>
          )}
        </div>
      </div>

      {/* Recommended Actions */}
      <div className="mb-6">
        <div className="flex items-center space-x-2 mb-3">
          <svg className="w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          <h3 className="font-medium">AI Model Recommendations</h3>
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
        <p>This outlook is generated by YOUR trained AI models including RandomForest classifiers, SHAP explainers, and local prediction models.</p>
        <p className="mt-1">Data refreshes automatically every 10 minutes from YOUR AI services.</p>
      </div>
    </div>
  );
}
        ]);

        // Process YOUR AI model forecast data
        if (forecastRes?.ok) {
          const forecastData = await forecastRes.json();
          setForecast(forecastData);
        } else {
          setForecast({ 
            error: 'Failed to load AI forecast',
            predicted_threats: {},
            method: 'ai_model_fallback'
          });
        }

        // Process YOUR AI agent data (trained models)
        if (agentsRes?.ok) {
          const agentsData = await agentsRes.json();
          setAgentData(agentsData);
        }

        // Process audit data
        if (auditRes?.ok) {
          const auditLogsData = await auditRes.json();
          setAuditData(auditLogsData);
        }

        // Process YOUR AI model status
        if (aiModelRes?.ok) {
          const aiModelsData = await aiModelRes.json();
          setAIModelData(aiModelsData);
        }

        // Process YOUR predictive AI insights
        if (predictiveRes?.ok) {
          const predictiveData = await predictiveRes.json();
          setPredictiveData(predictiveData);
        }

        // Process YOUR AI intelligence summary
        if (yourAIRes?.ok) {
          const aiIntelligenceData = await yourAIRes.json();
          setAIIntelligence(aiIntelligenceData);
        }

        // Process YOUR trained threat prediction models
        if (threatPredictionRes?.ok) {
          const threatPredictions = await threatPredictionRes.json();
          setThreatPredictions(threatPredictions);
        }

        setLastUpdate(new Date());
      } catch (error) {
        console.error('Error fetching AI model data:', error);
        setForecast({ 
          error: 'Failed to load YOUR AI models',
          predicted_threats: {},
          method: 'ai_fallback'
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchAllData();
    // Auto-refresh every 10 minutes
    const interval = setInterval(fetchAllData, 10 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const calculateThreatLevel = () => {
    // Use YOUR AI models for threat level calculation
    if (!forecast?.predicted_threats && !agentData?.agents && !auditData?.logs && !threatPredictions?.threats) {
      return { level: 'LOW', color: 'green' };
    }
    
    let maxThreatScore = 0;
    let recentSecurityEvents = 0;
    let aiModelConfidence = 0;
    
    // Analyze YOUR AI model forecast threats
    if (forecast?.predicted_threats) {
      const threats = Object.values(forecast.predicted_threats);
      if (threats.length > 0) {
        maxThreatScore = Math.max(...threats.map(t => typeof t === 'number' ? (t > 1 ? t/100 : t) : 0));
      }
    }
    
    // Analyze YOUR trained threat prediction models
    if (threatPredictions?.threats) {
      const aiPredictions = threatPredictions.threats.map(t => t.confidence || 0);
      if (aiPredictions.length > 0) {
        aiModelConfidence = Math.max(...aiPredictions);
        maxThreatScore = Math.max(maxThreatScore, aiModelConfidence);
      }
    }
    
    // Analyze YOUR AI models health and activity
    if (aiModelData?.models) {
      const activeModels = aiModelData.models.filter(model => model.status === 'healthy');
      const modelThreatScore = activeModels.length > 0 ? 
        activeModels.reduce((acc, model) => acc + (model.accuracy || 0), 0) / activeModels.length : 0;
      
      // Higher accuracy models contribute to better threat detection
      if (modelThreatScore > 0.9) {
        maxThreatScore = Math.max(maxThreatScore, 0.05); // Very confident models = lower threat baseline
      }
    }
    
    // Analyze recent agent data for security events (YOUR AI agents)
    if (agentData?.agents) {
      const activeAgents = agentData.agents.filter(agent => agent.status === 'active');
      recentSecurityEvents = activeAgents.length;
    }
    
    // Analyze YOUR predictive AI insights
    if (predictiveData?.correlated_score) {
      const correlatedThreat = predictiveData.correlated_score / 10.0; // Normalize to 0-1
      maxThreatScore = Math.max(maxThreatScore, correlatedThreat);
    }
    
    // Analyze recent security events from audit logs
    if (auditData?.logs) {
      const securityEvents = auditData.logs.filter(log => 
        log.action?.includes('auth') || 
        log.action?.includes('login') || 
        log.action?.includes('security') ||
        log.action?.includes('agent') ||
        log.action?.includes('threat') ||
        log.action?.includes('model')
      );
      recentSecurityEvents += securityEvents.length;
    }
    
    // YOUR AI model-enhanced threat level calculation
    if (maxThreatScore > 0.15 || recentSecurityEvents > 10 || aiModelConfidence > 0.8) {
      return { level: 'HIGH', color: 'red' };
    }
    if (maxThreatScore > 0.08 || recentSecurityEvents > 5 || aiModelConfidence > 0.6) {
      return { level: 'MEDIUM', color: 'yellow' };
    }
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
    const activeAgents = agentData?.agents?.filter(a => a.status === 'active')?.length || 0;
    const recentEvents = auditData?.logs?.length || 0;
    const aiModelsActive = aiModelData?.models?.filter(m => m.status === 'healthy')?.length || 0;
    const totalAIModels = aiModelData?.models?.length || 0;
    const aiAccuracy = aiModelData?.models?.reduce((acc, m) => acc + (m.accuracy || 0), 0) / Math.max(totalAIModels, 1);
    
    switch(level) {
      case 'HIGH': 
        return `Elevated security activity detected by YOUR AI models. ${activeAgents} AI agents active, ${aiModelsActive}/${totalAIModels} models healthy (${(aiAccuracy * 100).toFixed(1)}% avg accuracy), ${recentEvents} recent security events.`;
      case 'MEDIUM': 
        return `Moderate security activity observed by YOUR threat detection models. ${activeAgents} AI agents monitoring, ${aiModelsActive}/${totalAIModels} models operational, ${recentEvents} recent events.`;
      case 'LOW': 
        return `Security operations within normal parameters. ${activeAgents} AI agents online, YOUR models operating at ${(aiAccuracy * 100).toFixed(1)}% accuracy.`;
      default: 
        return 'YOUR AI models are evaluating current security posture...';
    }
  };

  const getAreasToMonitor = () => {
    const areas = [];
    
    // Add YOUR AI model forecast-based threats
    if (forecast?.predicted_threats) {
      Object.entries(forecast.predicted_threats).forEach(([threat, score]) => {
        const normalizedScore = typeof score === 'number' ? (score > 1 ? score/100 : score) : 0;
        let category = 'AI Model Prediction';
        let status = 'Low Chance';
        
        // Categorize threats using YOUR AI model insights
        if (threat.toLowerCase().includes('powershell') || threat.toLowerCase().includes('command')) {
          category = 'Endpoint AI Detection';
        } else if (threat.toLowerCase().includes('login') || threat.toLowerCase().includes('auth')) {
          category = 'Identity AI Analysis';
        } else if (threat.toLowerCase().includes('network') || threat.toLowerCase().includes('traffic')) {
          category = 'Network AI Monitoring';
        } else if (threat.toLowerCase().includes('sql') || threat.toLowerCase().includes('injection')) {
          category = 'Web AI Security';
        } else if (threat.toLowerCase().includes('log4j') || threat.toLowerCase().includes('exploit')) {
          category = 'Vulnerability AI Scanner';
        } else if (threat.toLowerCase().includes('model') || threat.toLowerCase().includes('ai')) {
          category = 'AI Model Security';
        }
        
        // Determine status based on YOUR AI model confidence
        if (normalizedScore > 0.15) status = 'High Confidence';
        else if (normalizedScore > 0.08) status = 'Medium Confidence';
        else status = 'Low Confidence';
        
        areas.push({
          category,
          description: `${threat} (AI Model: ${forecast.method || 'your_ai'})`,
          status,
          score: normalizedScore,
          details: `${Math.round(normalizedScore * 100)}% AI confidence`
        });
      });
    }
    
    // Add YOUR trained threat prediction model insights
    if (threatPredictions?.threats) {
      threatPredictions.threats.slice(0, 2).forEach(threat => {
        areas.push({
          category: 'AI Threat Prediction',
          description: `${threat.source}: ${threat.description}`,
          status: threat.severity > 6 ? 'High Confidence' : threat.severity > 4 ? 'Medium Confidence' : 'Low Confidence',
          score: threat.severity / 10,
          details: `Severity: ${threat.severity}/10 (YOUR AI Model)`
        });
      });
    }
    
    // Add YOUR predictive AI correlation insights
    if (predictiveData?.threats) {
      predictiveData.threats.slice(0, 2).forEach(threat => {
        areas.push({
          category: `AI ${threat.source} Analysis`,
          description: threat.description,
          status: threat.severity > 7 ? 'High Confidence' : threat.severity > 5 ? 'Medium Confidence' : 'Low Confidence',
          score: threat.severity / 10,
          details: `YOUR ${threat.source} AI Model`
        });
      });
    }
    
    // Add YOUR AI intelligence summary insights
    if (aiIntelligence?.threats) {
      areas.push({
        category: 'AI Intelligence Summary',
        description: 'AI-generated threat intelligence analysis',
        status: 'Medium Confidence',
        score: 0.6,
        details: 'YOUR AI Intelligence Model'
      });
    }
    
    // Add default areas if no AI model threats detected
    if (areas.length === 0) {
      areas.push(
        { 
          category: 'AI Model Baseline', 
          description: 'YOUR AI models monitoring normal activity', 
          status: 'Low Confidence', 
          details: 'AI models operational' 
        },
        { 
          category: 'Network AI Monitoring', 
          description: 'YOUR network AI models active', 
          status: 'Low Confidence', 
          details: 'AI-powered monitoring' 
        }
      );
    }
    
    return areas.slice(0, 4); // Limit to 4 areas
  };

  const getRecommendedActions = (level) => {
    const baseActions = [
      { text: 'Continue AI model monitoring and validation', completed: true },
      { text: 'Maintain YOUR AI model training pipeline', completed: false },
      { text: 'Verify YOUR AI model backup systems are functioning', completed: false }
    ];
    
    // Get AI model-specific recommendations
    const aiActions = [];
    if (aiModelData?.models) {
      const degradedModels = aiModelData.models.filter(m => m.status === 'degraded');
      const offlineModels = aiModelData.models.filter(m => m.status === 'offline');
      
      if (degradedModels.length > 0) {
        aiActions.push({ 
          text: `Investigate ${degradedModels.length} degraded AI model(s)`, 
          completed: false 
        });
      }
      
      if (offlineModels.length > 0) {
        aiActions.push({ 
          text: `Restart ${offlineModels.length} offline AI model(s)`, 
          completed: false 
        });
      }
    }
    
    if (level === 'HIGH') {
      return [
        { text: 'Review and validate YOUR AI model threat predictions', completed: false },
        { text: 'Increase AI model prediction frequency for critical systems', completed: false },
        { text: 'Verify YOUR AI incident response models are ready', completed: false },
        ...aiActions,
        ...baseActions
      ];
    } else if (level === 'MEDIUM') {
      return [
        { text: 'Review YOUR AI model security events and patterns', completed: false },
        { text: 'Validate YOUR AI security models are functioning properly', completed: false },
        ...aiActions,
        ...baseActions
      ];
    }
    
    return [...aiActions, ...baseActions];
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
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold">24-Hour AI Security Outlook</h2>
          <span className="text-xs bg-blue-600 text-white px-2 py-1 rounded">YOUR AI MODELS</span>
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
        <p className="text-slate-400 text-xs mt-1">
          Based on {threatCount} AI model events • 
          {aiModelData?.models?.filter(m => m.status === 'healthy')?.length || 0}/{aiModelData?.models?.length || 0} AI models healthy • 
          Method: {forecast?.method || 'your_ai_models'}
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

      {/* Recommended Actions */}
      <div className="mb-4">
        <div className="flex items-center space-x-2 mb-3">
          <svg className="w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          <h3 className="font-medium">AI Model Recommendations</h3>
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
        <span>Based on {threatCount} AI model events from YOUR trained models</span>
      </div>
    </div>
  );
}
