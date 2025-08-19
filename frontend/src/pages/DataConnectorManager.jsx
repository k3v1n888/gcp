

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Alert, AlertDescription } from '../ui/alert';
import { 
  CpuChipIcon,
  BoltIcon,
  ShieldCheckIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  PlayIcon,
  PauseIcon,
  CogIcon,
  CircleStackIcon,
  SignalIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';

const DataConnectorManager = () => {
  const [connectorData, setConnectorData] = useState(null);
  const [intelligentRouting, setIntelligentRouting] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchConnectorData();
    fetchIntelligentRouting();
  }, []);

  const fetchConnectorData = async () => {
    try {
      const response = await fetch(`${process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8001'}/api/connectors/status`);
      const data = await response.json();
      setConnectorData(data);
    } catch (err) {
      console.error('Error fetching connector data:', err);
      setError(`Failed to fetch connector status: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const fetchIntelligentRouting = async () => {
    try {
      const response = await fetch(`${process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8001'}/api/connectors/intelligent-routing`);
      const data = await response.json();
      setIntelligentRouting(data);
    } catch (err) {
      console.error('Error fetching intelligent routing data:', err);
    }
  };

  const getStatusIcon = (status) => {
    switch (status.toLowerCase()) {
      case 'connected':
      case 'active':
        return <CheckCircleIcon className="h-5 w-5 text-green-600" />;
      case 'connecting':
        return <ClockIcon className="h-5 w-5 text-yellow-600" />;
      case 'error':
      case 'disconnected':
        return <XCircleIcon className="h-5 w-5 text-red-600" />;
      default:
        return <SignalIcon className="h-5 w-5 text-gray-600" />;
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.9) return 'text-green-600';
    if (confidence >= 0.8) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 bg-slate-900 text-white">
        <CpuChipIcon className="h-8 w-8 animate-spin text-blue-400" />
        <span className="ml-2 text-lg">Loading AI-Powered Connector System...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-slate-900 text-white">
        <Alert className="bg-red-900 border-red-700">
          <ExclamationTriangleIcon className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 bg-slate-900 text-white min-h-screen">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <CircleStackIcon className="h-8 w-8 text-blue-400" />
          <h1 className="text-2xl font-bold">AI-Powered Data Connector Management</h1>
        </div>
        <div className="flex space-x-2">
          <Button 
            onClick={fetchConnectorData} 
            variant="outline"
            className="bg-slate-800 border-slate-600 text-white hover:bg-slate-700"
          >
            <BoltIcon className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* AI Intelligence Overview */}
      {intelligentRouting && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">AI Routing Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-2">
                {intelligentRouting.intelligent_routing?.enabled ? (
                  <CheckCircleIcon className="h-6 w-6 text-green-500" />
                ) : (
                  <XCircleIcon className="h-6 w-6 text-red-500" />
                )}
                <div>
                  <div className="text-xl font-bold text-white">
                    {intelligentRouting.intelligent_routing?.enabled ? 'ACTIVE' : 'INACTIVE'}
                  </div>
                  <p className="text-xs text-slate-400">Model v{intelligentRouting.intelligent_routing?.model_version}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">Data Processed Today</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-400">
                {intelligentRouting.data_processing?.total_processed_today?.toLocaleString() || '0'}
              </div>
              <p className="text-xs text-slate-400">Records classified and routed</p>
            </CardContent>
          </Card>
          
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">Classification Accuracy</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-400">
                {((intelligentRouting.data_processing?.successful_classifications / intelligentRouting.data_processing?.total_processed_today) * 100).toFixed(1) || '0.0'}%
              </div>
              <p className="text-xs text-slate-400">AI classification success rate</p>
            </CardContent>
          </Card>
          
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">Manual Review Queue</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-400">
                {intelligentRouting.human_oversight?.pending_classifications || 0}
              </div>
              <p className="text-xs text-slate-400">Awaiting human review</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Connector Status Grid */}
      {connectorData && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {connectorData.connectors?.map((connector, index) => (
            <Card key={index} className="bg-slate-800 border-slate-700 hover:border-slate-600 transition-all">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg font-semibold text-white flex items-center">
                    {getStatusIcon(connector.status)}
                    <span className="ml-2">{connector.name}</span>
                  </CardTitle>
                  <Badge 
                    variant={connector.status === 'connected' ? 'default' : 'destructive'}
                    className={connector.status === 'connected' ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'}
                  >
                    {connector.status}
                  </Badge>
                </div>
                <p className="text-sm text-slate-400">{connector.type}</p>
              </CardHeader>
              
              <CardContent className="space-y-4">
                {/* AI Confidence Score */}
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium text-slate-300">AI Confidence</span>
                    <span className={`text-sm font-bold ${getConfidenceColor(connector.ai_confidence)}`}>
                      {(connector.ai_confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-slate-700 rounded-full h-2">
                    <div 
                      className="bg-blue-500 h-2 rounded-full" 
                      style={{ width: `${connector.ai_confidence * 100}%` }}
                    ></div>
                  </div>
                </div>

                {/* Processing Stats */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-slate-700 p-3 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <ChartBarIcon className="h-4 w-4 text-blue-400" />
                      <span className="text-xs text-slate-400">Processed Today</span>
                    </div>
                    <div className="text-lg font-bold text-white mt-1">
                      {connector.data_processed_today?.toLocaleString() || '0'}
                    </div>
                  </div>
                  <div className="bg-slate-700 p-3 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <BoltIcon className="h-4 w-4 text-green-400" />
                      <span className="text-xs text-slate-400">Health Status</span>
                    </div>
                    <div className="text-lg font-bold text-green-400 mt-1">
                      {connector.health}
                    </div>
                  </div>
                </div>

                {/* Last Sync */}
                <div className="text-xs text-slate-400">
                  <span className="flex items-center">
                    <ClockIcon className="h-3 w-3 mr-1" />
                    Last sync: {new Date(connector.last_sync).toLocaleString()}
                  </span>
                </div>

                {/* Control Buttons */}
                <div className="flex space-x-2 pt-2">
                  <Button 
                    size="sm" 
                    variant="outline"
                    className="flex-1 bg-slate-700 border-slate-600 text-white hover:bg-slate-600"
                  >
                    <CogIcon className="h-4 w-4 mr-1" />
                    Configure
                  </Button>
                  <Button 
                    size="sm" 
                    variant="outline"
                    className="flex-1 bg-slate-700 border-slate-600 text-white hover:bg-slate-600"
                  >
                    {connector.status === 'connected' ? (
                      <>
                        <PauseIcon className="h-4 w-4 mr-1" />
                        Pause
                      </>
                    ) : (
                      <>
                        <PlayIcon className="h-4 w-4 mr-1" />
                        Start
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Data Format Detection */}
      {intelligentRouting?.data_processing?.formats_detected && (
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <CpuChipIcon className="h-5 w-5 mr-2" />
              AI Data Format Detection (Last 24 Hours)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {Object.entries(intelligentRouting.data_processing.formats_detected).map(([format, count]) => (
                <div key={format} className="bg-slate-700 p-3 rounded-lg text-center">
                  <div className="text-xl font-bold text-blue-400">{count.toLocaleString()}</div>
                  <div className="text-xs text-slate-400 uppercase">{format}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Human Oversight Panel */}
      {intelligentRouting?.human_oversight && (
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <ShieldCheckIcon className="h-5 w-5 mr-2" />
              Human Oversight Dashboard
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-slate-700 p-4 rounded-lg">
                <div className="text-2xl font-bold text-orange-400">
                  {intelligentRouting.human_oversight.approval_queue}
                </div>
                <div className="text-sm text-slate-400">Approval Queue</div>
              </div>
              <div className="bg-slate-700 p-4 rounded-lg">
                <div className="text-2xl font-bold text-blue-400">
                  {intelligentRouting.human_oversight.pending_classifications}
                </div>
                <div className="text-sm text-slate-400">Pending Classifications</div>
              </div>
              <div className="bg-slate-700 p-4 rounded-lg">
                <div className="text-2xl font-bold text-green-400">
                  {intelligentRouting.human_oversight.analyst_interventions_today}
                </div>
                <div className="text-sm text-slate-400">Analyst Interventions</div>
              </div>
              <div className="bg-slate-700 p-4 rounded-lg">
                <div className="text-2xl font-bold text-yellow-400">
                  {(intelligentRouting.human_oversight.override_rate * 100).toFixed(1)}%
                </div>
                <div className="text-sm text-slate-400">Override Rate</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default DataConnectorManager;
