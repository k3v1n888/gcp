import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Alert, AlertDescription } from '../ui/alert';
import { Loader2, Play, Pause, RefreshCw, Settings, Database, Activity } from '../ui/icons';
import { getApiBaseUrl } from '../utils/environment';

const DataConnectorManager = () => {
  const [connectors, setConnectors] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pipelineRunning, setPipelineRunning] = useState(false);
  const [stats, setStats] = useState(null);
  const [recentThreats, setRecentThreats] = useState([]);

  const API_BASE = getApiBaseUrl();

  const fetchConnectorStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/connectors/status`, {
        credentials: 'include'
      });
      const data = await response.json();
      
      if (data.success) {
        setConnectors(data.data.connectors || {});
      } else {
        setError('Failed to fetch connector status');
      }
    } catch (err) {
      console.error('Error fetching connector status:', err);
      setError(`Failed to fetch connector status: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/connectors/stats?hours_back=24`, {
        credentials: 'include'
      });
      const data = await response.json();
      
      if (data.success) {
        setStats(data.data);
      }
    } catch (err) {
      console.error('Error fetching stats:', err);
    }
  };

  const fetchRecentThreats = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/connectors/threats/recent?hours_back=1&limit=10`, {
        credentials: 'include'
      });
      const data = await response.json();
      
      if (data.success) {
        setRecentThreats(data.data.threats || []);
      }
    } catch (err) {
      console.error('Error fetching recent threats:', err);
    }
  };

  const testConnections = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/connectors/test-connections`, {
        method: 'POST',
        credentials: 'include'
      });
      const data = await response.json();
      
      if (data.success) {
        await fetchConnectorStatus(); // Refresh status
      } else {
        setError('Connection test failed');
      }
    } catch (err) {
      console.error('Error testing connections:', err);
      setError(`Connection test failed: ${err.message}`);
    }
  };

  const runPipeline = async () => {
    setPipelineRunning(true);
    try {
      const response = await fetch(`${API_BASE}/api/connectors/pipeline/run-sync?hours_back=1`, {
        credentials: 'include'
      });
      const data = await response.json();
      
      if (data.success) {
        // Refresh data after pipeline runs
        await Promise.all([
          fetchConnectorStatus(),
          fetchStats(),
          fetchRecentThreats()
        ]);
        
        // Show success message with results
        const result = data.data;
        alert(`Pipeline completed successfully!\n` +
              `Threats collected: ${result.threats_collected}\n` +
              `Incidents created: ${result.incidents_created}\n` +
              `Duration: ${result.duration.toFixed(2)}s`);
      } else {
        setError(`Pipeline failed: ${data.error || 'Unknown error'}`);
      }
    } catch (err) {
      console.error('Error running pipeline:', err);
      setError(`Pipeline execution failed: ${err.message}`);
    } finally {
      setPipelineRunning(false);
    }
  };

  const reloadConnectors = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/connectors/reload`, {
        method: 'POST',
        credentials: 'include'
      });
      const data = await response.json();
      
      if (data.success) {
        await fetchConnectorStatus();
      } else {
        setError('Failed to reload connectors');
      }
    } catch (err) {
      console.error('Error reloading connectors:', err);
      setError(`Failed to reload connectors: ${err.message}`);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'critical': return 'bg-red-500';
      case 'high': return 'bg-orange-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusColor = (connected, enabled) => {
    if (!enabled) return 'bg-gray-500';
    return connected ? 'bg-green-500' : 'bg-red-500';
  };

  useEffect(() => {
    fetchConnectorStatus();
    fetchStats();
    fetchRecentThreats();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(() => {
      fetchConnectorStatus();
      fetchStats();
      fetchRecentThreats();
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="w-8 h-8 animate-spin" />
        <span className="ml-2">Loading connectors...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold tracking-tight">Universal Data Connectors</h2>
        <div className="flex space-x-2">
          <Button onClick={testConnections} variant="outline">
            <RefreshCw className="w-4 h-4 mr-2" />
            Test Connections
          </Button>
          <Button onClick={reloadConnectors} variant="outline">
            <Settings className="w-4 h-4 mr-2" />
            Reload
          </Button>
          <Button 
            onClick={runPipeline} 
            disabled={pipelineRunning}
            className="bg-blue-600 hover:bg-blue-700"
          >
            {pipelineRunning ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Play className="w-4 h-4 mr-2" />
            )}
            Run Pipeline
          </Button>
        </div>
      </div>

      {error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertDescription className="text-red-800">{error}</AlertDescription>
        </Alert>
      )}

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center">
              <Database className="w-8 h-8 text-blue-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Connectors</p>
                <p className="text-2xl font-bold">{Object.keys(connectors).length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center">
              <Activity className="w-8 h-8 text-green-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Active</p>
                <p className="text-2xl font-bold">
                  {Object.values(connectors).filter(c => c.enabled).length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center">
              <RefreshCw className="w-8 h-8 text-orange-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Threats (24h)</p>
                <p className="text-2xl font-bold">{stats?.total_threats || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center">
              <Play className="w-8 h-8 text-purple-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Recent (1h)</p>
                <p className="text-2xl font-bold">{recentThreats.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Connector Status */}
      <Card>
        <CardHeader>
          <CardTitle>Connector Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {Object.entries(connectors).map(([name, connector]) => (
              <div key={name} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className={`w-3 h-3 rounded-full ${getStatusColor(connector.connected, connector.enabled)}`} />
                  <div>
                    <h4 className="font-semibold">{name}</h4>
                    <p className="text-sm text-gray-600">{connector.type}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <Badge variant={connector.enabled ? "default" : "secondary"}>
                    {connector.enabled ? "Enabled" : "Disabled"}
                  </Badge>
                  <Badge variant={connector.connected ? "success" : "destructive"}>
                    {connector.connected ? "Connected" : "Disconnected"}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Recent Threats */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Threats (Last Hour)</CardTitle>
        </CardHeader>
        <CardContent>
          {recentThreats.length === 0 ? (
            <p className="text-gray-600 text-center py-4">No recent threats detected</p>
          ) : (
            <div className="space-y-3">
              {recentThreats.map((threat, index) => (
                <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex-1">
                    <h4 className="font-semibold">{threat.threat}</h4>
                    <p className="text-sm text-gray-600">
                      {threat.source} • {threat.ip} • {new Date(threat.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge className={`${getSeverityColor(threat.severity)} text-white`}>
                      {threat.severity}
                    </Badge>
                    {threat.ai_severity && (
                      <Badge variant="outline">
                        AI: {threat.ai_severity}
                      </Badge>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Threat Statistics by Source */}
      {stats?.by_source && stats.by_source.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Threats by Source (24h)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {stats.by_source.map((source, index) => (
                <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <h4 className="font-semibold">{source.source}</h4>
                    <p className="text-sm text-gray-600">
                      Latest: {source.latest ? new Date(source.latest).toLocaleString() : 'Never'}
                    </p>
                  </div>
                  <Badge variant="outline" className="text-lg px-3 py-1">
                    {source.count}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default DataConnectorManager;
