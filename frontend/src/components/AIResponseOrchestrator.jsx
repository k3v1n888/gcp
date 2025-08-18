

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Alert, AlertDescription } from '../ui/alert';
import {
  CpuChipIcon,
  PlayIcon,
  PauseIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  ShieldCheckIcon,
  BoltIcon,
  ClockIcon,
  UserIcon,
  DocumentTextIcon,
  CogIcon
} from '@heroicons/react/24/outline';

const AIResponseOrchestrator = ({ threatId, incidentId, onResponseExecuted }) => {
  const [orchestratorData, setOrchestratorData] = useState(null);
  const [suggestedResponses, setSuggestedResponses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [executingResponse, setExecutingResponse] = useState(null);

  useEffect(() => {
    if (threatId || incidentId) {
      fetchOrchestratorData();
      fetchSuggestedResponses();
    }
  }, [threatId, incidentId]);

  const fetchOrchestratorData = async () => {
    setLoading(true);
    try {
      const endpoint = threatId ? 
        `/api/threats/${threatId}/ai-responses` : 
        `/api/incidents/${incidentId}/ai-responses`;
      
      const response = await fetch(`${process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8001'}${endpoint}`);
      const data = await response.json();
      setOrchestratorData(data);
    } catch (err) {
      console.error('Error fetching orchestrator data:', err);
      setError(`Failed to fetch AI orchestrator data: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const fetchSuggestedResponses = async () => {
    try {
      const endpoint = threatId ? 
        `/api/threats/${threatId}/suggested-responses` : 
        `/api/incidents/${incidentId}/suggested-responses`;
      
      const response = await fetch(`${process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8001'}${endpoint}`);
      const data = await response.json();
      setSuggestedResponses(data.suggestions || []);
    } catch (err) {
      console.error('Error fetching suggested responses:', err);
    }
  };

  const executeResponse = async (responseId, requiresApproval = false) => {
    setExecutingResponse(responseId);
    try {
      const endpoint = threatId ? 
        `/api/threats/${threatId}/execute-response` : 
        `/api/incidents/${incidentId}/execute-response`;
      
      const response = await fetch(`${process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8001'}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          response_id: responseId,
          requires_approval: requiresApproval,
          executed_by: 'analyst', // This would come from auth context
          execution_mode: requiresApproval ? 'human_approved' : 'automated'
        }),
      });
      
      const result = await response.json();
      
      if (result.success) {
        // Refresh data after execution
        fetchOrchestratorData();
        if (onResponseExecuted) {
          onResponseExecuted(result);
        }
      } else {
        setError(`Failed to execute response: ${result.message}`);
      }
    } catch (err) {
      console.error('Error executing response:', err);
      setError(`Failed to execute response: ${err.message}`);
    } finally {
      setExecutingResponse(null);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'critical': return 'text-red-400';
      case 'high': return 'text-orange-400';
      case 'medium': return 'text-yellow-400';
      case 'low': return 'text-green-400';
      default: return 'text-gray-400';
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.9) return 'text-green-400';
    if (confidence >= 0.7) return 'text-yellow-400';
    return 'text-red-400';
  };

  if (loading && !orchestratorData) {
    return (
      <div className="flex items-center justify-center p-6 bg-slate-800 rounded-lg">
        <CpuChipIcon className="h-6 w-6 animate-spin text-blue-400 mr-2" />
        <span className="text-white">Loading AI Response Orchestrator...</span>
      </div>
    );
  }

  if (error) {
    return (
      <Alert className="bg-red-900 border-red-700 mb-4">
        <ExclamationTriangleIcon className="h-4 w-4" />
        <AlertDescription className="text-red-300">{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      {/* AI Orchestrator Status */}
      {orchestratorData && (
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <CpuChipIcon className="h-5 w-5 mr-2 text-blue-400" />
              AI Response Orchestrator
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-slate-700 p-3 rounded-lg">
                <div className="flex items-center space-x-2">
                  <ShieldCheckIcon className="h-4 w-4 text-blue-400" />
                  <span className="text-xs text-slate-400">Model Status</span>
                </div>
                <div className="text-lg font-bold text-green-400 mt-1">
                  {orchestratorData.model_status || 'ACTIVE'}
                </div>
              </div>
              <div className="bg-slate-700 p-3 rounded-lg">
                <div className="flex items-center space-x-2">
                  <BoltIcon className="h-4 w-4 text-yellow-400" />
                  <span className="text-xs text-slate-400">Confidence</span>
                </div>
                <div className={`text-lg font-bold mt-1 ${getConfidenceColor(orchestratorData.confidence)}`}>
                  {(orchestratorData.confidence * 100).toFixed(1)}%
                </div>
              </div>
              <div className="bg-slate-700 p-3 rounded-lg">
                <div className="flex items-center space-x-2">
                  <ClockIcon className="h-4 w-4 text-purple-400" />
                  <span className="text-xs text-slate-400">Response Time</span>
                </div>
                <div className="text-lg font-bold text-white mt-1">
                  {orchestratorData.avg_response_time || '1.2s'}
                </div>
              </div>
              <div className="bg-slate-700 p-3 rounded-lg">
                <div className="flex items-center space-x-2">
                  <UserIcon className="h-4 w-4 text-green-400" />
                  <span className="text-xs text-slate-400">Human Oversight</span>
                </div>
                <div className="text-lg font-bold text-green-400 mt-1">
                  {orchestratorData.human_oversight_enabled ? 'ENABLED' : 'DISABLED'}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Suggested Responses */}
      {suggestedResponses.length > 0 && (
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center justify-between">
              <div className="flex items-center">
                <DocumentTextIcon className="h-5 w-5 mr-2 text-green-400" />
                AI-Suggested Response Actions
              </div>
              <Badge className="bg-blue-900 text-blue-300">
                {suggestedResponses.length} Available
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {suggestedResponses.map((response, index) => (
                <div key={index} className="bg-slate-700 rounded-lg p-4 border border-slate-600">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h4 className="text-white font-semibold mb-1">{response.title}</h4>
                      <p className="text-slate-300 text-sm mb-2">{response.description}</p>
                      
                      <div className="flex items-center space-x-4 text-xs text-slate-400">
                        <span className={`flex items-center ${getSeverityColor(response.severity)}`}>
                          <ExclamationTriangleIcon className="h-3 w-3 mr-1" />
                          {response.severity} Priority
                        </span>
                        <span className={`flex items-center ${getConfidenceColor(response.confidence)}`}>
                          <CpuChipIcon className="h-3 w-3 mr-1" />
                          {(response.confidence * 100).toFixed(1)}% Confidence
                        </span>
                        <span className="flex items-center">
                          <ClockIcon className="h-3 w-3 mr-1" />
                          Est. {response.estimated_duration || '5-10'} min
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Response Actions */}
                  <div className="bg-slate-600 rounded p-3 mb-3">
                    <h5 className="text-white text-sm font-medium mb-2">Proposed Actions:</h5>
                    <ul className="text-slate-300 text-sm space-y-1">
                      {response.actions?.map((action, actionIndex) => (
                        <li key={actionIndex} className="flex items-start">
                          <span className="text-blue-400 mr-2">•</span>
                          {action}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Execution Controls */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {response.requires_approval && (
                        <Badge variant="outline" className="text-orange-300 border-orange-600">
                          <UserIcon className="h-3 w-3 mr-1" />
                          Human Approval Required
                        </Badge>
                      )}
                      {response.automated_execution && (
                        <Badge variant="outline" className="text-green-300 border-green-600">
                          <BoltIcon className="h-3 w-3 mr-1" />
                          Can Auto-Execute
                        </Badge>
                      )}
                    </div>
                    
                    <div className="flex space-x-2">
                      <Button
                        size="sm"
                        variant="outline"
                        className="bg-slate-600 border-slate-500 text-white hover:bg-slate-500"
                      >
                        <CogIcon className="h-4 w-4 mr-1" />
                        Configure
                      </Button>
                      
                      {response.requires_approval ? (
                        <Button
                          size="sm"
                          onClick={() => executeResponse(response.id, true)}
                          disabled={executingResponse === response.id}
                          className="bg-orange-600 hover:bg-orange-700 text-white"
                        >
                          {executingResponse === response.id ? (
                            <CpuChipIcon className="h-4 w-4 mr-1 animate-spin" />
                          ) : (
                            <UserIcon className="h-4 w-4 mr-1" />
                          )}
                          Approve & Execute
                        </Button>
                      ) : (
                        <Button
                          size="sm"
                          onClick={() => executeResponse(response.id, false)}
                          disabled={executingResponse === response.id}
                          className="bg-green-600 hover:bg-green-700 text-white"
                        >
                          {executingResponse === response.id ? (
                            <CpuChipIcon className="h-4 w-4 mr-1 animate-spin" />
                          ) : (
                            <PlayIcon className="h-4 w-4 mr-1" />
                          )}
                          Execute Now
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Quick Actions */}
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center">
            <BoltIcon className="h-5 w-5 mr-2 text-yellow-400" />
            Quick Response Actions
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <Button
              variant="outline"
              className="bg-red-900 border-red-700 text-red-300 hover:bg-red-800"
            >
              <XCircleIcon className="h-4 w-4 mr-1" />
              Block Source
            </Button>
            <Button
              variant="outline"
              className="bg-yellow-900 border-yellow-700 text-yellow-300 hover:bg-yellow-800"
            >
              <ExclamationTriangleIcon className="h-4 w-4 mr-1" />
              Quarantine
            </Button>
            <Button
              variant="outline"
              className="bg-blue-900 border-blue-700 text-blue-300 hover:bg-blue-800"
            >
              <ShieldCheckIcon className="h-4 w-4 mr-1" />
              Monitor
            </Button>
            <Button
              variant="outline"
              className="bg-green-900 border-green-700 text-green-300 hover:bg-green-800"
            >
              <CheckCircleIcon className="h-4 w-4 mr-1" />
              Mark Safe
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AIResponseOrchestrator;
