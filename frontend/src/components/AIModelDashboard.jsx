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



import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Progress } from './ui/progress';
// Using heroicons since lucide-react is not installed
import { 
  CpuChipIcon,
  ChartBarIcon,
  ShieldCheckIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  BoltIcon,
  CursorArrowRaysIcon as TargetIcon,
  WifiIcon,
  ArrowTrendingUpIcon,
  EyeIcon,
  CpuChipIcon as CpuIcon,
  CircleStackIcon as DatabaseIcon,
  ArrowPathIcon as RefreshCwIcon
} from '@heroicons/react/24/outline';

const AIModelDashboard = () => {
  const [systemStatus, setSystemStatus] = useState(null);
  const [realtimeData, setRealtimeData] = useState({
    threats: [],
    decisions: [],
    processing: []
  });
  const [modelPerformance, setModelPerformance] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const intervalRef = useRef(null);

  useEffect(() => {
    fetchSystemStatus();
    fetchRealtimeData();
    
    // Setup real-time updates
    intervalRef.current = setInterval(() => {
      fetchSystemStatus();
      fetchRealtimeData();
    }, 5000); // Update every 5 seconds

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  const fetchSystemStatus = async () => {
    try {
      const response = await fetch(`${process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8001'}/api/ai/status`);
      if (response.ok) {
        const data = await response.json();
        setSystemStatus(data);
      }
    } catch (error) {
      console.error('Failed to fetch system status:', error);
    }
    setIsLoading(false);
  };

  const fetchRealtimeData = async () => {
    try {
      // Fetch recent AI decisions
      const decisionsResponse = await fetch(`${process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8001'}/api/ai/decisions/recent`);
      if (decisionsResponse.ok) {
        const decisions = await decisionsResponse.json();
        setRealtimeData(prev => ({
          ...prev,
          decisions
        }));
      }

      // Fetch current processing
      const processingResponse = await fetch(`${process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8001'}/api/ai/processing/current`);
      if (processingResponse.ok) {
        const processing = await processingResponse.json();
        setRealtimeData(prev => ({
          ...prev,
          processing
        }));
      }

      // Fetch recent threats
      const threatsResponse = await fetch(`${process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8001'}/api/threats?limit=10`);
      if (threatsResponse.ok) {
        const threatsData = await threatsResponse.json();
        setRealtimeData(prev => ({
          ...prev,
          threats: threatsData.threats || []
        }));
      }

    } catch (error) {
      console.error('Failed to fetch realtime data:', error);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy': return 'text-green-600';
      case 'degraded': return 'text-yellow-600';
      case 'offline': case 'critical': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy': return <CheckCircleIcon className="h-4 w-4 text-green-600" />;
      case 'degraded': return <ExclamationTriangleIcon className="h-4 w-4 text-yellow-600" />;
      case 'offline': case 'critical': return <XCircleIcon className="h-4 w-4 text-red-600" />;
      default: return <ClockIcon className="h-4 w-4 text-gray-600" />;
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCwIcon className="h-8 w-8 animate-spin text-blue-600" />
        <span className="ml-2 text-lg">Loading AI System Status...</span>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <CpuChipIcon className="h-8 w-8 text-blue-600" />
          <h1 className="text-2xl font-bold text-gray-900">AI Model Management Dashboard</h1>
        </div>
        <Button onClick={() => { fetchSystemStatus(); fetchRealtimeData(); }} variant="outline">
          <RefreshCwIcon className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* System Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">System Health</p>
                <p className={`text-2xl font-bold ${getStatusColor(systemStatus?.system_health)}`}>
                  {systemStatus?.system_health || 'Unknown'}
                </p>
              </div>
              {getStatusIcon(systemStatus?.system_health)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Recent Decisions</p>
                <p className="text-2xl font-bold text-blue-600">
                  {systemStatus?.recent_decisions || 0}
                </p>
              </div>
              <BoltIcon className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Models</p>
                <p className="text-2xl font-bold text-green-600">
                  {systemStatus?.models ? Object.keys(systemStatus.models).length : 0}
                </p>
              </div>
              <CpuIcon className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Avg Confidence</p>
                <p className="text-2xl font-bold text-purple-600">
                  {systemStatus?.performance_metrics?.average_confidence ? 
                    `${(systemStatus.performance_metrics.average_confidence * 100).toFixed(1)}%` : '0%'}
                </p>
              </div>
              <TargetIcon className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* AI Models Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <WifiIcon className="h-5 w-5" />
            <span>AI Models Status</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {systemStatus?.models && Object.entries(systemStatus.models).map(([name, model]) => (
              <div key={name} className="border rounded-lg p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="font-medium text-gray-900 capitalize">{name.replace('_', ' ')}</h3>
                  {getStatusIcon(model.status)}
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Status:</span>
                    <Badge variant={model.status === 'healthy' ? 'default' : model.status === 'degraded' ? 'secondary' : 'destructive'}>
                      {model.status}
                    </Badge>
                  </div>
                  
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Response Time:</span>
                    <span className="font-medium">{model.response_time || 'N/A'}</span>
                  </div>
                  
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Last Check:</span>
                    <span className="text-xs text-gray-500">
                      {model.last_check ? formatTimestamp(model.last_check) : 'N/A'}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Real-time Processing */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent AI Decisions */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <CpuChipIcon className="h-5 w-5" />
              <span>Recent AI Decisions</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 max-h-64 overflow-y-auto">
              {realtimeData.decisions.length > 0 ? realtimeData.decisions.map((decision, index) => (
                <div key={index} className="border-l-4 border-blue-500 pl-4 py-2">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-sm">Decision #{decision.decision_id}</span>
                    <Badge variant="outline">{decision.decision_type}</Badge>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">{decision.rationale}</p>
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>Confidence: {(decision.confidence * 100).toFixed(1)}%</span>
                    <span>{formatTimestamp(decision.timestamp)}</span>
                  </div>
                </div>
              )) : (
                <p className="text-gray-500 text-center py-8">No recent decisions</p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Current Processing */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <ChartBarIcon className="h-5 w-5" />
              <span>Current Processing</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 max-h-64 overflow-y-auto">
              {realtimeData.processing.length > 0 ? realtimeData.processing.map((process, index) => (
                <div key={index} className="border rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-sm">{process.stage}</span>
                    <Badge variant="outline">{process.status}</Badge>
                  </div>
                  <Progress value={process.progress || 0} className="mb-2" />
                  <div className="flex justify-between text-xs text-gray-500">
                    <span>ID: {process.id}</span>
                    <span>ETA: {process.eta || 'Unknown'}</span>
                  </div>
                </div>
              )) : (
                <div className="text-center py-8">
                  <EyeIcon className="h-12 w-12 text-gray-300 mx-auto mb-2" />
                  <p className="text-gray-500">No active processing</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Threat Intelligence Stream */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <ShieldCheckIcon className="h-5 w-5" />
            <span>Real-time Threat Intelligence</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {realtimeData.threats.length > 0 ? realtimeData.threats.map((threat, index) => (
              <div key={threat.id || index} className="flex items-center justify-between p-2 hover:bg-gray-50 rounded">
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <Badge variant={
                      threat.severity === 'critical' ? 'destructive' :
                      threat.severity === 'high' ? 'secondary' : 'outline'
                    }>
                      {threat.severity}
                    </Badge>
                    <span className="font-medium text-sm truncate">{threat.threat}</span>
                  </div>
                  <div className="flex items-center space-x-4 text-xs text-gray-500 mt-1">
                    <span>IP: {threat.ip}</span>
                    <span>Source: {threat.source}</span>
                    <span>{formatTimestamp(threat.timestamp)}</span>
                  </div>
                </div>
                <div className="flex items-center space-x-1">
                  {threat.ai_processed && <CpuChipIcon className="h-4 w-4 text-blue-500" />}
                  {threat.correlation_score > 0.5 && <WifiIcon className="h-4 w-4 text-orange-500" />}
                  {threat.severity === 'high' || threat.severity === 'critical' ? 
                    <ExclamationTriangleIcon className="h-4 w-4 text-red-500" /> : 
                    <CheckCircleIcon className="h-4 w-4 text-green-500" />
                  }
                </div>
              </div>
            )) : (
              <p className="text-gray-500 text-center py-8">No recent threats</p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* System Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Processing Throughput</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Data Intelligence</span>
                <span className="font-medium">125/min</span>
              </div>
              <Progress value={75} className="h-2" />
              
              <div className="flex justify-between text-sm">
                <span>Threat Scoring</span>
                <span className="font-medium">98/min</span>
              </div>
              <Progress value={60} className="h-2" />
              
              <div className="flex justify-between text-sm">
                <span>Policy Decisions</span>
                <span className="font-medium">45/min</span>
              </div>
              <Progress value={30} className="h-2" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Model Accuracy</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Threat Detection</span>
                <span className="font-medium">94.2%</span>
              </div>
              <Progress value={94} className="h-2" />
              
              <div className="flex justify-between text-sm">
                <span>False Positive Rate</span>
                <span className="font-medium">3.1%</span>
              </div>
              <Progress value={3} className="h-2" />
              
              <div className="flex justify-between text-sm">
                <span>Classification</span>
                <span className="font-medium">91.8%</span>
              </div>
              <Progress value={92} className="h-2" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">System Resources</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>CPU Usage</span>
                <span className="font-medium">68%</span>
              </div>
              <Progress value={68} className="h-2" />
              
              <div className="flex justify-between text-sm">
                <span>Memory</span>
                <span className="font-medium">45%</span>
              </div>
              <Progress value={45} className="h-2" />
              
              <div className="flex justify-between text-sm">
                <span>GPU Utilization</span>
                <span className="font-medium">82%</span>
              </div>
              <Progress value={82} className="h-2" />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AIModelDashboard;
