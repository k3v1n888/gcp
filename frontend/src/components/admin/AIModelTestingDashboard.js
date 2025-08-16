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

/**
 * Sentient AI SOC Multi-Model Management Dashboard
 * Comprehensive interface for managing and monitoring all AI models
 */

import React, { useState, useEffect } from 'react';
import { 
  CpuChipIcon, 
  PlayCircleIcon,
  StopCircleIcon,
  ChartBarIcon,
  EyeIcon,
  Cog6ToothIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  BoltIcon
} from '@heroicons/react/24/outline';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Alert, AlertDescription } from '../ui/alert';
import { getApiBaseUrl } from '../../utils/environment';

const SentientAIModelsDashboard = () => {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedModel, setSelectedModel] = useState(null);
      const [modelHealth, setModelHealth] = useState(null);
    const [testingModel, setTestingModel] = useState(null);
    const [testResults, setTestResults] = useState({});
    const [orchestratorStatus, setOrchestratorStatus] = useState(null);
    const [orchestratorLoading, setOrchestratorLoading] = useState(false);
    const [pipelineOverview, setPipelineOverview] = useState(null);
    const [decisionHistory, setDecisionHistory] = useState([]);
    const [error, setError] = useState(null);
  const [systemHealth, setSystemHealth] = useState({});

  // Map display model names to orchestrator API names
  const getOrchestratorModelName = (displayName) => {
    const modelMap = {
      'Model A: Data Intake & Normalization AI': 'ingest',
      'Data Intake & Normalization AI': 'ingest',
      'Model B: Post-Processing & Enrichment AI': 'postprocess',
      'Post-Processing & Enrichment AI': 'postprocess',
      'Model C: Quantum AI Predictive Security Engine': 'threat-model',
      'Quantum AI Predictive Security Engine': 'threat-model',
      'Threat Service (Model C Wrapper)': 'threat-model',
      'AI Orchestrator (Action Execution)': 'orchestrator',
      'Console (Web Approval Interface)': 'console'
    };
    
    // Find exact match first
    if (modelMap[displayName]) {
      return modelMap[displayName];
    }
    
    // Fallback: find partial match
    for (const [key, value] of Object.entries(modelMap)) {
      if (displayName.includes(key) || key.includes(displayName)) {
        return value;
      }
    }
    
    // Default fallback - try to extract key terms
    if (displayName.includes('Data Intake') || displayName.includes('Normalization')) {
      return 'ingest';
    }
    if (displayName.includes('Post-Process') || displayName.includes('Enrichment')) {
      return 'postprocess';
    }
    if (displayName.includes('Quantum') || displayName.includes('Threat') || displayName.includes('Predictive')) {
      return 'threat-model';
    }
    if (displayName.includes('Orchestrator') || displayName.includes('Action')) {
      return 'orchestrator';
    }
    if (displayName.includes('Console') || displayName.includes('Approval')) {
      return 'console';
    }
    
    return displayName.toLowerCase().replace(/\s+/g, '-');
  };

  const fetchModelsData = async () => {
    try {
      setLoading(true);
      // Use port 8000 for health endpoints (ingest service) 
      const healthBaseUrl = process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8000';
      
      // Fetch AI models health
      const modelsResponse = await fetch(`${healthBaseUrl}/api/admin/health/ai-models`);
      const modelsData = await modelsResponse.json();
      
      setModels(modelsData.models || []);
      setSystemHealth({
        status: modelsData.status,
        healthy_count: modelsData.healthy_count,
        total_count: modelsData.total_count,
        architecture: modelsData.architecture,
        pipeline: modelsData.pipeline
      });
      
    } catch (error) {
      console.error('Failed to fetch models data:', error);
    } finally {
      setLoading(false);
    }
  };

  const testModel = async (model) => {
    try {
      setTestResults(prev => ({...prev, [model.name]: { status: 'testing' }}));
      
      // Use the orchestrator API directly for model testing
      const orchestratorBaseUrl = process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8003';
      const orchestratorModelName = getOrchestratorModelName(model.name);
      const response = await fetch(`${orchestratorBaseUrl}/api/models/test/${orchestratorModelName}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      const result = await response.json();
      
      setTestResults(prev => ({
        ...prev,
        [model.name]: {
          status: response.ok ? 'success' : 'error',
          result: result,
          timestamp: new Date().toISOString()
        }
      }));
      
    } catch (error) {
      setTestResults(prev => ({
        ...prev,
        [model.name]: {
          status: 'error',
          error: error.message,
          timestamp: new Date().toISOString()
        }
      }));
    }
  };

  const fetchOrchestratorStatus = async () => {
    try {
      setOrchestratorLoading(true);
      // Use orchestrator port 8003 for orchestrator status
      const orchestratorBaseUrl = process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8003';
      const response = await fetch(`${orchestratorBaseUrl}/api/orchestrator/status`);
      if (response.ok) {
        const data = await response.json();
        setOrchestratorStatus(data);
      }
    } catch (err) {
      console.error('Failed to fetch orchestrator status:', err);
    } finally {
      setOrchestratorLoading(false);
    }
  };

  const fetchPipelineOverview = async () => {
    try {
      // Use orchestrator port 8003 for pipeline overview
      const orchestratorBaseUrl = process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8003';
      const response = await fetch(`${orchestratorBaseUrl}/api/orchestrator/pipeline/overview`);
      if (response.ok) {
        const data = await response.json();
        setPipelineOverview(data);
      }
    } catch (err) {
      console.error('Failed to fetch pipeline overview:', err);
    }
  };

  const fetchDecisionHistory = async () => {
    try {
      // Use orchestrator port 8003 for decision history
      const orchestratorBaseUrl = process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8003';
      const response = await fetch(`${orchestratorBaseUrl}/api/orchestrator/decisions/history?limit=5`);
      if (response.ok) {
        const data = await response.json();
        setDecisionHistory(data.decisions || []);
      }
    } catch (err) {
      console.error('Failed to fetch decision history:', err);
    }
  };

  const controlOrchestrator = async (action) => {
    try {
      setOrchestratorLoading(true);
      // Use orchestrator port 8003 for control
      const orchestratorBaseUrl = process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8003';
      const response = await fetch(`${orchestratorBaseUrl}/api/orchestrator/control/${action}`, {
        method: 'POST'
      });
      if (response.ok) {
        await fetchOrchestratorStatus();
      }
    } catch (err) {
      console.error(`Failed to ${action} orchestrator:`, err);
    } finally {
      setOrchestratorLoading(false);
    }
  };

  useEffect(() => {
    fetchModelsData();
    fetchOrchestratorStatus();
    fetchPipelineOverview();
    fetchDecisionHistory();
    const interval = setInterval(() => {
      fetchModelsData();
      fetchOrchestratorStatus();
      fetchDecisionHistory();
    }, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'degraded':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />;
      case 'offline':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      default:
        return <ArrowPathIcon className="h-5 w-5 text-gray-400 animate-spin" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy': return 'bg-green-100 text-green-800 border-green-200';
      case 'degraded': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'offline': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="space-y-3">
            {[1,2,3].map(i => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Sentient AI SOC Models</h1>
          <p className="text-gray-600">Multi-Model Architecture Management & Testing</p>
        </div>
        <div className="flex space-x-3">
          <Button onClick={fetchModelsData} variant="outline" size="sm">
            <ArrowPathIcon className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* System Overview */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <BoltIcon className="h-8 w-8 text-blue-600" />
            <div>
              <h2 className="text-xl font-semibold">Architecture Overview</h2>
              <p className="text-gray-500">{systemHealth.architecture}</p>
            </div>
          </div>
          <Badge className={getStatusColor(systemHealth.status)}>
            {systemHealth.status}
          </Badge>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">
              {systemHealth.healthy_count || 0}
            </div>
            <div className="text-sm text-blue-800">Healthy Models</div>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-gray-600">
              {systemHealth.total_count || 0}
            </div>
            <div className="text-sm text-gray-800">Total Models</div>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-green-600">
              {systemHealth.total_count ? Math.round((systemHealth.healthy_count/systemHealth.total_count)*100) : 0}%
            </div>
            <div className="text-sm text-green-800">System Health</div>
          </div>
        </div>
        
        {systemHealth.pipeline && (
          <div className="bg-gray-50 p-3 rounded-lg">
            <div className="text-sm font-medium text-gray-700">Data Flow Pipeline:</div>
            <div className="text-sm text-gray-600 mt-1">{systemHealth.pipeline}</div>
          </div>
        )}
      </Card>

      {/* Models Grid */}
      <div className="space-y-4">
        {models.map((model, index) => (
          <Card key={index} className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                {getStatusIcon(model.status)}
                <div>
                  <h3 className="text-lg font-semibold">{model.name}</h3>
                  <p className="text-sm text-gray-500">{model.type}</p>
                  {model.description && (
                    <p className="text-xs text-gray-400 mt-1">{model.description}</p>
                  )}
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Badge className={getStatusColor(model.status)}>
                  {model.status}
                </Badge>
                <Button 
                  onClick={() => testModel(model)}
                  variant="outline" 
                  size="sm"
                  disabled={!model.endpoint || model.status === 'offline'}
                >
                  <PlayCircleIcon className="h-4 w-4 mr-1" />
                  Test
                </Button>
              </div>
            </div>

            {/* Model Details */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
              {model.endpoint && (
                <div className="bg-gray-50 p-3 rounded">
                  <div className="text-xs text-gray-500">Endpoint</div>
                  <div className="text-sm font-mono">{model.endpoint}</div>
                </div>
              )}
              {model.port && (
                <div className="bg-gray-50 p-3 rounded">
                  <div className="text-xs text-gray-500">Port</div>
                  <div className="text-sm font-mono">{model.port}</div>
                </div>
              )}
              {model.container && (
                <div className="bg-gray-50 p-3 rounded">
                  <div className="text-xs text-gray-500">Container</div>
                  <div className="text-sm font-mono">{model.container}</div>
                </div>
              )}
              {model.version && (
                <div className="bg-gray-50 p-3 rounded">
                  <div className="text-xs text-gray-500">Version</div>
                  <div className="text-sm">{model.version}</div>
                </div>
              )}
            </div>

            {/* Special Model C (Your AI) Details */}
            {model.name?.includes('Quantum AI Predictive Security Engine') && (
              <div className="mb-4 p-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-200">
                <div className="text-sm font-medium text-purple-800 mb-3">🤖 Your Trained AI Model Details</div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {[
                    { label: 'RandomForest Model', value: model.model_loaded, type: 'boolean' },
                    { label: 'Preprocessor', value: model.preprocessor_loaded, type: 'boolean' },
                    { label: 'SHAP Explainer', value: model.explainer_available, type: 'boolean' },
                    { label: 'Features', value: model.features, type: 'text' }
                  ].map((item, i) => (
                    <div key={i} className="bg-white p-2 rounded border">
                      <div className="text-xs text-gray-500">{item.label}</div>
                      {item.type === 'boolean' ? (
                        <div className="flex items-center space-x-1 mt-1">
                          {item.value ? 
                            <CheckCircleIcon className="h-4 w-4 text-green-500" /> : 
                            <XCircleIcon className="h-4 w-4 text-red-500" />
                          }
                          <span className="text-xs">{item.value ? 'Loaded' : 'Missing'}</span>
                        </div>
                      ) : (
                        <div className="text-sm mt-1">{item.value || 'N/A'}</div>
                      )}
                    </div>
                  ))}
                </div>
                {model.accuracy && (
                  <div className="mt-3 text-sm">
                    <span className="font-medium text-purple-700">Performance:</span> 
                    <span className="text-purple-600 ml-1">{model.accuracy}</span>
                  </div>
                )}
              </div>
            )}

            {/* Test Results */}
            {testResults[model.name] && (
              <div className="mt-4">
                <div className="text-sm font-medium text-gray-700 mb-2">Latest Test Result:</div>
                {testResults[model.name].status === 'testing' ? (
                  <div className="flex items-center space-x-2 text-blue-600">
                    <ArrowPathIcon className="h-4 w-4 animate-spin" />
                    <span className="text-sm">Testing model...</span>
                  </div>
                ) : testResults[model.name].status === 'success' ? (
                  <Alert className="border-green-200 bg-green-50">
                    <CheckCircleIcon className="h-4 w-4 text-green-600" />
                    <AlertDescription>
                      <div className="text-sm">
                        <div className="font-medium text-green-800">Test Successful</div>
                        {testResults[model.name].result && (
                          <div className="mt-2 font-mono text-xs bg-white p-2 rounded">
                            Prediction: {testResults[model.name].result.prediction} | 
                            Confidence: {testResults[model.name].result.confidence} | 
                            Severity: {testResults[model.name].result.severity}
                          </div>
                        )}
                      </div>
                    </AlertDescription>
                  </Alert>
                ) : (
                  <Alert className="border-red-200 bg-red-50">
                    <XCircleIcon className="h-4 w-4 text-red-600" />
                    <AlertDescription>
                      <div className="text-sm">
                        <div className="font-medium text-red-800">Test Failed</div>
                        <div className="text-red-600 mt-1">{testResults[model.name].error}</div>
                      </div>
                    </AlertDescription>
                  </Alert>
                )}
              </div>
            )}

            {/* Error Display */}
            {model.error && (
              <Alert className="border-red-200 bg-red-50 mt-4">
                <XCircleIcon className="h-4 w-4 text-red-600" />
                <AlertDescription>
                  <div className="text-sm">
                    <div className="font-medium text-red-800">Model Error</div>
                    <div className="text-red-600 mt-1">{model.error}</div>
                  </div>
                </AlertDescription>
              </Alert>
            )}
          </Card>
        ))}
      </div>

      {/* AI Orchestrator Control */}
      {orchestratorStatus && (
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <CpuChipIcon className="h-8 w-8 text-purple-600" />
              <div>
                <h2 className="text-xl font-semibold">AI Orchestrator</h2>
                <p className="text-gray-500">Central decision engine and model coordination</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Badge className={orchestratorStatus.orchestrator_status === 'running' ? 
                'bg-green-100 text-green-800 border-green-200' : 
                'bg-red-100 text-red-800 border-red-200'}>
                {orchestratorStatus.orchestrator_status}
              </Badge>
              {orchestratorStatus.orchestrator_status === 'running' ? (
                <Button 
                  onClick={() => controlOrchestrator('stop')}
                  variant="outline" 
                  size="sm"
                  disabled={orchestratorLoading}
                  className="text-red-600 border-red-200 hover:bg-red-50"
                >
                  Stop
                </Button>
              ) : (
                <Button 
                  onClick={() => controlOrchestrator('start')}
                  variant="outline" 
                  size="sm"
                  disabled={orchestratorLoading}
                  className="text-green-600 border-green-200 hover:bg-green-50"
                >
                  Start
                </Button>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">
                {orchestratorStatus.recent_decisions || 0}
              </div>
              <div className="text-sm text-purple-800">Recent Decisions</div>
            </div>
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                {orchestratorStatus.performance_metrics?.model_health ? 
                  Object.values(orchestratorStatus.performance_metrics.model_health).filter(h => h === 'healthy').length : 0}
              </div>
              <div className="text-sm text-blue-800">Healthy Models</div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {orchestratorStatus.system_health}
              </div>
              <div className="text-sm text-green-800">System Health</div>
            </div>
            <div className="bg-yellow-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-yellow-600">
                {orchestratorStatus.performance_metrics?.uptime_hours ? 
                  Math.round(orchestratorStatus.performance_metrics.uptime_hours) : 0}h
              </div>
              <div className="text-sm text-yellow-800">System Uptime</div>
            </div>
          </div>

          {/* Recent Decisions */}
          {decisionHistory.length > 0 && (
            <div className="mt-4">
              <h3 className="text-sm font-medium text-gray-700 mb-2">Recent AI Decisions</h3>
              <div className="space-y-2">
                {decisionHistory.slice(0, 3).map((decision, idx) => (
                  <div key={idx} className="bg-gray-50 p-3 rounded text-sm">
                    <div className="flex justify-between items-center">
                      <span className="font-medium">{decision.decision_type}</span>
                      <span className="text-xs text-gray-500">
                        {new Date(decision.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <div className="text-gray-600 mt-1">{decision.rationale}</div>
                    <div className="mt-1">
                      <Badge className="text-xs">
                        Confidence: {Math.round(decision.confidence * 100)}%
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </Card>
      )}

      {/* Pipeline Overview */}
      {pipelineOverview && (
        <Card className="p-6">
          <div className="flex items-center space-x-3 mb-4">
            <BoltIcon className="h-8 w-8 text-indigo-600" />
            <div>
              <h2 className="text-xl font-semibold">AI Pipeline Overview</h2>
              <p className="text-gray-500">Complete data flow and processing architecture</p>
            </div>
          </div>

          <div className="space-y-3">
            {pipelineOverview.stages?.map((stage, idx) => (
              <div key={idx} className="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg">
                <div className="flex-shrink-0 w-8 h-8 bg-indigo-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                  {stage.stage}
                </div>
                <div className="flex-grow">
                  <div className="font-medium">{stage.name}</div>
                  <div className="text-sm text-gray-600">{stage.model}</div>
                  <div className="text-xs text-gray-500">{stage.description}</div>
                </div>
                <div className="text-right">
                  <Badge className={stage.status === 'healthy' || stage.status === 'running' ? 
                    'bg-green-100 text-green-800' : 
                    stage.status === 'degraded' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'}>
                    {stage.status}
                  </Badge>
                  <div className="text-xs text-gray-500 mt-1">{stage.endpoint}</div>
                </div>
              </div>
            ))}
          </div>

          {pipelineOverview.data_flow && (
            <div className="mt-4 p-3 bg-blue-50 rounded-lg">
              <div className="text-sm font-medium text-blue-800 mb-2">Data Flow:</div>
              {pipelineOverview.data_flow.map((flow, idx) => (
                <div key={idx} className="text-sm text-blue-700">{flow}</div>
              ))}
            </div>
          )}

          {pipelineOverview.human_control_points && (
            <div className="mt-4 p-3 bg-amber-50 rounded-lg">
              <div className="text-sm font-medium text-amber-800 mb-2">Human Control Points:</div>
              <div className="grid grid-cols-2 gap-2">
                {pipelineOverview.human_control_points.map((point, idx) => (
                  <div key={idx} className="text-sm text-amber-700">• {point}</div>
                ))}
              </div>
            </div>
          )}
        </Card>
      )}

      {models.length === 0 && !loading && (
        <Card className="p-12 text-center">
          <CpuChipIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <div className="text-lg text-gray-500">No AI models found</div>
          <div className="text-sm text-gray-400">Check if the Sentient AI services are running</div>
        </Card>
      )}
    </div>
  );
};

export default SentientAIModelsDashboard;
