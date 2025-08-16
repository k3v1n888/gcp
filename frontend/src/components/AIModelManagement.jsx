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
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Progress } from './ui/progress';
import { 
  CpuChipIcon,
  CogIcon,
  ShieldCheckIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  BoltIcon,
  EyeIcon,
  AdjustmentsVerticalIcon,
  UserIcon,
  PlayIcon,
  PauseIcon
} from '@heroicons/react/24/outline';

const AIModelManagement = () => {
  const [modelData, setModelData] = useState(null);
  const [selectedModel, setSelectedModel] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showControlPanel, setShowControlPanel] = useState(false);

  useEffect(() => {
    fetchModelManagement();
  }, []);

  const fetchModelManagement = async () => {
    try {
      const response = await fetch(`${process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8001'}/api/ai/models/management`);
      if (response.ok) {
        const data = await response.json();
        setModelData(data);
      }
    } catch (error) {
      console.error('Failed to fetch AI model management data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const updateModelControl = async (modelId, settings) => {
    try {
      const response = await fetch(`${process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8001'}/api/ai/models/${modelId}/control`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings)
      });
      
      if (response.ok) {
        await fetchModelManagement(); // Refresh data
      }
    } catch (error) {
      console.error('Failed to update model control:', error);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active': return <CheckCircleIcon className="h-5 w-5 text-green-600" />;
      case 'training': return <ClockIcon className="h-5 w-5 text-yellow-600" />;
      case 'inactive': return <XCircleIcon className="h-5 w-5 text-red-600" />;
      default: return <CpuChipIcon className="h-5 w-5 text-gray-600" />;
    }
  };

  const getAccuracyColor = (accuracy) => {
    if (accuracy >= 0.9) return 'text-green-600';
    if (accuracy >= 0.8) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <CpuChipIcon className="h-8 w-8 animate-spin text-blue-600" />
        <span className="ml-2 text-lg">Loading AI Model Management...</span>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <CpuChipIcon className="h-8 w-8 text-blue-600" />
          <h1 className="text-2xl font-bold text-gray-900">AI Model Management & Control</h1>
        </div>
        <Button onClick={fetchModelManagement} variant="outline">
          <BoltIcon className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* System Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Models</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{modelData ? Object.keys(modelData.models).length : 0}</div>
            <p className="text-xs text-gray-600">Active AI models</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Human Oversight</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              {modelData?.system_settings?.global_human_approval ? 'ENABLED' : 'DISABLED'}
            </div>
            <p className="text-xs text-gray-600">Global approval required</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Auto Learning</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {modelData?.system_settings?.auto_learning_enabled ? 'ON' : 'OFF'}
            </div>
            <p className="text-xs text-gray-600">Continuous improvement</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Update Frequency</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{modelData?.system_settings?.model_update_frequency || 'N/A'}</div>
            <p className="text-xs text-gray-600">Model retraining</p>
          </CardContent>
        </Card>
      </div>

      {/* AI Models Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {modelData && Object.entries(modelData.models).map(([modelId, model]) => (
          <Card key={modelId} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg font-semibold flex items-center">
                  {getStatusIcon(model.status)}
                  <span className="ml-2">{model.name}</span>
                </CardTitle>
                <Badge variant={model.status === 'active' ? 'default' : model.status === 'training' ? 'secondary' : 'destructive'}>
                  {model.status}
                </Badge>
              </div>
              <p className="text-sm text-gray-600">{model.description || model.type}</p>
            </CardHeader>
            
            <CardContent className="space-y-4">
              {/* Model Performance */}
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Accuracy</span>
                  <span className={`text-sm font-bold ${getAccuracyColor(model.accuracy)}`}>
                    {(model.accuracy * 100).toFixed(1)}%
                  </span>
                </div>
                <Progress value={model.accuracy * 100} className="h-2" />
              </div>

              {/* Version & Training */}
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Version:</span>
                  <p className="font-medium">{model.version}</p>
                </div>
                <div>
                  <span className="text-gray-600">Last Trained:</span>
                  <p className="font-medium text-xs">
                    {model.last_trained ? new Date(model.last_trained).toLocaleDateString() : 'N/A'}
                  </p>
                </div>
              </div>

              {/* Human Control Settings */}
              <div className="bg-gray-50 p-3 rounded-lg space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium flex items-center">
                    <UserIcon className="h-4 w-4 mr-1" />
                    Human Control
                  </span>
                  <Badge variant={model.human_control?.approval_required ? 'destructive' : 'default'}>
                    {model.human_control?.approval_required ? 'REQUIRED' : 'AUTO'}
                  </Badge>
                </div>
                
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <span className="text-gray-600">Threshold:</span>
                    <p className="font-medium">{(model.human_control?.confidence_threshold * 100).toFixed(0)}%</p>
                  </div>
                  <div>
                    <span className="text-gray-600">Queue:</span>
                    <p className="font-medium">{model.human_control?.manual_review_queue || 0}</p>
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-600">Auto Response:</span>
                  <div className="flex items-center">
                    {model.human_control?.auto_response_enabled ? (
                      <PlayIcon className="h-3 w-3 text-green-600" />
                    ) : (
                      <PauseIcon className="h-3 w-3 text-red-600" />
                    )}
                    <span className="text-xs ml-1">
                      {model.human_control?.auto_response_enabled ? 'Enabled' : 'Disabled'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Model Capabilities */}
              {model.capabilities && (
                <div>
                  <span className="text-sm font-medium">Capabilities:</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {model.capabilities.slice(0, 3).map((capability, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {capability}
                      </Badge>
                    ))}
                    {model.capabilities.length > 3 && (
                      <Badge variant="outline" className="text-xs">
                        +{model.capabilities.length - 3} more
                      </Badge>
                    )}
                  </div>
                </div>
              )}

              {/* Control Buttons */}
              <div className="flex space-x-2 pt-2">
                <Button 
                  size="sm" 
                  variant="outline"
                  onClick={() => {
                    setSelectedModel({ id: modelId, ...model });
                    setShowControlPanel(true);
                  }}
                  className="flex-1"
                >
                  <AdjustmentsVerticalIcon className="h-4 w-4 mr-1" />
                  Control
                </Button>
                <Button 
                  size="sm" 
                  variant="outline"
                  onClick={() => console.log('View performance for', modelId)}
                  className="flex-1"
                >
                  <EyeIcon className="h-4 w-4 mr-1" />
                  Monitor
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Control Panel Modal */}
      {showControlPanel && selectedModel && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg max-w-lg w-full mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Control Panel: {selectedModel.name}</h3>
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => setShowControlPanel(false)}
              >
                ×
              </Button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Human Approval Required
                </label>
                <select 
                  className="w-full p-2 border rounded"
                  defaultValue={selectedModel.human_control?.approval_required}
                  onChange={(e) => {
                    updateModelControl(selectedModel.id, {
                      approval_required: e.target.value === 'true'
                    });
                  }}
                >
                  <option value="false">Auto-approve (No human required)</option>
                  <option value="true">Require human approval</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">
                  Confidence Threshold: {selectedModel.human_control?.confidence_threshold * 100}%
                </label>
                <input 
                  type="range" 
                  min="0" 
                  max="100" 
                  defaultValue={selectedModel.human_control?.confidence_threshold * 100}
                  className="w-full"
                  onChange={(e) => {
                    updateModelControl(selectedModel.id, {
                      confidence_threshold: e.target.value / 100
                    });
                  }}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">
                  Auto Response
                </label>
                <select 
                  className="w-full p-2 border rounded"
                  defaultValue={selectedModel.human_control?.auto_response_enabled}
                  onChange={(e) => {
                    updateModelControl(selectedModel.id, {
                      auto_response_enabled: e.target.value === 'true'
                    });
                  }}
                >
                  <option value="true">Enable automatic responses</option>
                  <option value="false">Disable automatic responses</option>
                </select>
              </div>
            </div>
            
            <div className="flex justify-end space-x-2 mt-6">
              <Button variant="outline" onClick={() => setShowControlPanel(false)}>
                Cancel
              </Button>
              <Button onClick={() => setShowControlPanel(false)}>
                Save Changes
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIModelManagement;
