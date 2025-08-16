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
 * System Health Dashboard Component
 * Monitors Docker containers, API endpoints, connectors, and AI models
 */

import React, { useState, useEffect } from 'react';
import { 
  ServerIcon, 
  CircleStackIcon,
  CpuChipIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import { Card } from '../ui/card';
import { Badge } from '../ui/badge';
import { getApiBaseUrl } from '../utils/environment';

const HealthDashboard = () => {
  const [healthData, setHealthData] = useState({
    docker: { status: 'checking', containers: [] },
    apis: { status: 'checking', endpoints: [] },
    connectors: { status: 'checking', connectors: [] },
    aiModels: { status: 'checking', models: [] },
    system: { status: 'checking', metrics: {} }
  });
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchHealthData = async () => {
    try {
      const baseUrl = getApiBaseUrl();
      
      // Use port 8000 for health endpoints (ingest service) as it has Docker API access
      const healthBaseUrl = process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8000';
      
      // Fetch all health endpoints
      const [
        dockerHealth,
        apiHealth,
        connectorHealth,
        aiHealth,
        systemHealth
      ] = await Promise.all([
        fetch(`${healthBaseUrl}/api/admin/health/docker`).then(r => r.json()).catch(() => ({ status: 'error', containers: [] })),
        fetch(`${healthBaseUrl}/api/admin/health/apis`).then(r => r.json()).catch(() => ({ status: 'error', endpoints: [] })),
        fetch(`${baseUrl}/api/connectors/status`).then(r => r.json()).catch(() => ({ status: 'error', connectors: [] })),
        fetch(`${healthBaseUrl}/api/admin/health/ai-models`).then(r => r.json()).catch(() => ({ status: 'error', models: [] })),
        fetch(`${healthBaseUrl}/api/admin/health/system`).then(r => r.json()).catch(() => ({ status: 'error', metrics: {} }))
      ]);

      setHealthData({
        docker: dockerHealth,
        apis: apiHealth,
        connectors: connectorHealth,
        aiModels: aiHealth,
        system: systemHealth
      });
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Failed to fetch health data:', error);
    }
  };

  useEffect(() => {
    fetchHealthData();
    
    if (autoRefresh) {
      const interval = setInterval(fetchHealthData, 30000); // Refresh every 30 seconds
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy':
      case 'running':
      case 'online':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'warning':
      case 'degraded':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />;
      case 'error':
      case 'offline':
      case 'failed':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      default:
        return <ClockIcon className="h-5 w-5 text-gray-400 animate-spin" />;
    }
  };

  const getStatusBadge = (status) => {
    const colors = {
      'healthy': 'bg-green-100 text-green-800',
      'running': 'bg-green-100 text-green-800',
      'online': 'bg-green-100 text-green-800',
      'warning': 'bg-yellow-100 text-yellow-800',
      'degraded': 'bg-yellow-100 text-yellow-800',
      'error': 'bg-red-100 text-red-800',
      'offline': 'bg-red-100 text-red-800',
      'failed': 'bg-red-100 text-red-800',
      'checking': 'bg-gray-100 text-gray-800'
    };
    
    return (
      <Badge className={colors[status] || colors.checking}>
        {status}
      </Badge>
    );
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">System Health Dashboard</h1>
        <div className="flex items-center space-x-4">
          <div className="text-sm text-gray-500">
            Last updated: {lastUpdate.toLocaleTimeString()}
          </div>
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`px-3 py-2 rounded-md text-sm font-medium ${
              autoRefresh 
                ? 'bg-green-100 text-green-800' 
                : 'bg-gray-100 text-gray-800'
            }`}
          >
            Auto-refresh: {autoRefresh ? 'ON' : 'OFF'}
          </button>
          <button
            onClick={fetchHealthData}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Refresh Now
          </button>
        </div>
      </div>

      {/* Overall System Status */}
      <Card className="p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <ServerIcon className="h-8 w-8 text-blue-600" />
            <div>
              <h2 className="text-xl font-semibold">System Overview</h2>
              <p className="text-gray-500">Overall system health status</p>
            </div>
          </div>
          <div className="text-right">
            {getStatusBadge(healthData.system.status)}
          </div>
        </div>
        
        {healthData.system.metrics && (
          <div className="mt-4 grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="text-sm text-gray-500">Uptime</div>
              <div className="text-lg font-semibold">{healthData.system.metrics.uptime || 'N/A'}</div>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="text-sm text-gray-500">CPU Usage</div>
              <div className="text-lg font-semibold">{healthData.system.metrics.cpu || 'N/A'}</div>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="text-sm text-gray-500">Memory Usage</div>
              <div className="text-lg font-semibold">{healthData.system.metrics.memory || 'N/A'}</div>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="text-sm text-gray-500">Disk Usage</div>
              <div className="text-lg font-semibold">{healthData.system.metrics.disk || 'N/A'}</div>
            </div>
          </div>
        )}
      </Card>

      {/* Docker Containers */}
      <Card className="p-6">
        <div className="flex items-center space-x-3 mb-4">
          <CircleStackIcon className="h-6 w-6 text-blue-600" />
          <h2 className="text-xl font-semibold">Docker Containers</h2>
          {getStatusBadge(healthData.docker.status)}
        </div>
        <div className="space-y-3">
          {healthData.docker.containers.map((container, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                {getStatusIcon(container.status)}
                <div>
                  <div className="font-medium">{container.name}</div>
                  <div className="text-sm text-gray-500">{container.image}</div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm">{getStatusBadge(container.status)}</div>
                {container.ports && (
                  <div className="text-xs text-gray-500 mt-1">
                    Ports: {container.ports}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* API Endpoints */}
      <Card className="p-6">
        <div className="flex items-center space-x-3 mb-4">
          <ServerIcon className="h-6 w-6 text-green-600" />
          <h2 className="text-xl font-semibold">API Health</h2>
          {getStatusBadge(healthData.apis.status)}
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {healthData.apis.endpoints.map((endpoint, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                {getStatusIcon(endpoint.status)}
                <div>
                  <div className="font-medium">{endpoint.name}</div>
                  <div className="text-sm text-gray-500">{endpoint.url}</div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm">{getStatusBadge(endpoint.status)}</div>
                {endpoint.response_time && (
                  <div className="text-xs text-gray-500 mt-1">
                    {endpoint.response_time}ms
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Data Connectors */}
      <Card className="p-6">
        <div className="flex items-center space-x-3 mb-4">
          <CircleStackIcon className="h-6 w-6 text-purple-600" />
          <h2 className="text-xl font-semibold">Data Connectors</h2>
          {getStatusBadge(healthData.connectors.status)}
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {healthData.connectors.connectors?.map((connector, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                {getStatusIcon(connector.status)}
                <div>
                  <div className="font-medium">{connector.name}</div>
                  <div className="text-sm text-gray-500">{connector.type}</div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm">{getStatusBadge(connector.status)}</div>
                {connector.last_collection && (
                  <div className="text-xs text-gray-500 mt-1">
                    Last: {new Date(connector.last_collection).toLocaleTimeString()}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Sentient AI Models - Multi-Model Architecture */}
      <Card className="p-6">
        <div className="flex items-center space-x-3 mb-4">
          <CpuChipIcon className="h-6 w-6 text-orange-600" />
          <h2 className="text-xl font-semibold">Sentient AI SOC Multi-Model Architecture</h2>
          {getStatusBadge(healthData.aiModels.status)}
        </div>
        
        {healthData.aiModels.architecture && (
          <div className="mb-4 p-3 bg-blue-50 rounded-lg">
            <div className="text-sm font-medium text-blue-800">Architecture: {healthData.aiModels.architecture}</div>
            <div className="text-xs text-blue-600 mt-1">Pipeline: {healthData.aiModels.pipeline}</div>
            <div className="text-xs text-blue-600">
              Status: {healthData.aiModels.healthy_count || 0}/{healthData.aiModels.total_count || 0} models healthy
            </div>
          </div>
        )}
        
        <div className="space-y-4">
          {healthData.aiModels.models.map((model, index) => (
            <div key={index} className="border rounded-lg p-4 bg-white shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-3">
                  {getStatusIcon(model.status)}
                  <div>
                    <div className="font-medium text-lg">{model.name}</div>
                    <div className="text-sm text-gray-500">{model.type}</div>
                    {model.description && (
                      <div className="text-xs text-gray-400 mt-1">{model.description}</div>
                    )}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm">{getStatusBadge(model.status)}</div>
                  {model.port && (
                    <div className="text-xs text-gray-500 mt-1">Port: {model.port}</div>
                  )}
                </div>
              </div>
              
              {/* Model Details */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-3">
                {model.endpoint && (
                  <div className="bg-gray-50 p-2 rounded">
                    <div className="text-xs text-gray-500">Endpoint</div>
                    <div className="text-xs font-mono">{model.endpoint}</div>
                  </div>
                )}
                {model.container && (
                  <div className="bg-gray-50 p-2 rounded">
                    <div className="text-xs text-gray-500">Container</div>
                    <div className="text-xs font-mono">{model.container}</div>
                  </div>
                )}
                {model.version && (
                  <div className="bg-gray-50 p-2 rounded">
                    <div className="text-xs text-gray-500">Version</div>
                    <div className="text-xs">{model.version}</div>
                  </div>
                )}
                {model.uptime && (
                  <div className="bg-gray-50 p-2 rounded">
                    <div className="text-xs text-gray-500">Uptime</div>
                    <div className="text-xs">{model.uptime}</div>
                  </div>
                )}
              </div>
              
              {/* Special details for Model C (Your Trained AI) */}
              {model.name?.includes('Quantum AI Predictive Security Engine') && (
                <div className="mt-3 p-3 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-200">
                  <div className="text-sm font-medium text-purple-800 mb-2">🤖 Your Trained AI Model Status</div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                    {model.model_loaded !== undefined && (
                      <div className="flex items-center space-x-1">
                        {model.model_loaded ? 
                          <CheckCircleIcon className="h-4 w-4 text-green-500" /> : 
                          <XCircleIcon className="h-4 w-4 text-red-500" />
                        }
                        <span className="text-xs">Model Loaded</span>
                      </div>
                    )}
                    {model.preprocessor_loaded !== undefined && (
                      <div className="flex items-center space-x-1">
                        {model.preprocessor_loaded ? 
                          <CheckCircleIcon className="h-4 w-4 text-green-500" /> : 
                          <XCircleIcon className="h-4 w-4 text-red-500" />
                        }
                        <span className="text-xs">Preprocessor</span>
                      </div>
                    )}
                    {model.explainer_available !== undefined && (
                      <div className="flex items-center space-x-1">
                        {model.explainer_available ? 
                          <CheckCircleIcon className="h-4 w-4 text-green-500" /> : 
                          <XCircleIcon className="h-4 w-4 text-red-500" />
                        }
                        <span className="text-xs">SHAP Explainer</span>
                      </div>
                    )}
                    {model.features && (
                      <div className="text-xs">
                        <span className="text-gray-500">Features:</span> {model.features}
                      </div>
                    )}
                  </div>
                  {model.accuracy && (
                    <div className="mt-2 text-xs text-purple-600">
                      <span className="font-medium">Performance:</span> {model.accuracy}
                    </div>
                  )}
                </div>
              )}
              
              {/* Error display */}
              {model.error && (
                <div className="mt-3 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-700">
                  <span className="font-medium">Error:</span> {model.error}
                </div>
              )}
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};

export default HealthDashboard;
