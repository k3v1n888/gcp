import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  PlayIcon, 
  StopIcon, 
  CheckCircleIcon, 
  XCircleIcon,
  ClockIcon,
  CpuChipIcon,
  DatabaseIcon,
  BeakerIcon
} from '@heroicons/react/24/outline';

const AIModelTestingDashboard = () => {
  const [testResults, setTestResults] = useState(null);
  const [testing, setTesting] = useState(false);
  const [selectedTest, setSelectedTest] = useState('all');
  const [testHistory, setTestHistory] = useState([]);
  const [dataGeneration, setDataGeneration] = useState({
    threatLogs: 0,
    incidents: 0,
    status: 'idle'
  });

  // AI Model test configurations
  const aiModelTests = {
    'threat_scoring': {
      name: 'Threat Scoring Model',
      endpoint: '/predict/threat_score',
      description: 'Tests AI model for threat severity scoring',
      sampleData: {
        source_ip: '192.168.1.100',
        threat_type: 'malware_detection',
        confidence_score: 0.85,
        cvss_score: 7.5
      }
    },
    'anomaly_detection': {
      name: 'Anomaly Detection Model',
      endpoint: '/predict/anomaly',
      description: 'Tests AI model for anomaly detection',
      sampleData: {
        protocol: 'TCP',
        port: 443,
        traffic_volume: 1000,
        connection_count: 50
      }
    },
    'severity_prediction': {
      name: 'Severity Prediction Model', 
      endpoint: '/predict/severity',
      description: 'Tests AI model for threat severity prediction',
      sampleData: {
        threat_type: 'phishing_attempt',
        ioc_count: 5,
        criticality_score: 0.8
      }
    },
    'risk_assessment': {
      name: 'Risk Assessment Model',
      endpoint: '/predict/risk',
      description: 'Tests AI model for comprehensive risk assessment',
      sampleData: {
        asset_value: 'high',
        vulnerability_score: 8.5,
        threat_landscape: 'active'
      }
    },
    'shap_explanation': {
      name: 'SHAP Explainability',
      endpoint: '/explain/shap',
      description: 'Tests AI model explainability features',
      sampleData: {
        features: ['ip', 'port', 'protocol'],
        prediction_context: 'threat_analysis'
      }
    }
  };

  const generateTestData = async () => {
    setDataGeneration(prev => ({ ...prev, status: 'generating' }));
    
    try {
      const response = await fetch('/api/admin/generate-test-data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify({
          threat_logs_count: 100,
          incidents_count: 20,
          generate_iocs: true
        })
      });

      if (response.ok) {
        const result = await response.json();
        setDataGeneration({
          threatLogs: result.threat_logs_inserted,
          incidents: result.incidents_inserted,
          status: 'complete'
        });
      } else {
        throw new Error('Failed to generate test data');
      }
    } catch (error) {
      console.error('Error generating test data:', error);
      setDataGeneration(prev => ({ ...prev, status: 'error' }));
    }
  };

  const runAIModelTests = async (testType = 'all') => {
    setTesting(true);
    const startTime = Date.now();

    try {
      const testsToRun = testType === 'all' ? Object.keys(aiModelTests) : [testType];
      const results = {};

      for (const test of testsToRun) {
        const testConfig = aiModelTests[test];
        console.log(`Running test: ${testConfig.name}`);

        try {
          const response = await fetch(`/api/ai-service${testConfig.endpoint}`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(testConfig.sampleData)
          });

          const responseData = await response.json();
          
          results[test] = {
            name: testConfig.name,
            status: response.ok ? 'success' : 'failed',
            statusCode: response.status,
            responseTime: Date.now() - startTime,
            response: responseData,
            endpoint: testConfig.endpoint
          };

        } catch (error) {
          results[test] = {
            name: testConfig.name,
            status: 'error',
            error: error.message,
            endpoint: testConfig.endpoint
          };
        }
      }

      const testResult = {
        timestamp: new Date().toISOString(),
        testType,
        results,
        summary: {
          total: Object.keys(results).length,
          passed: Object.values(results).filter(r => r.status === 'success').length,
          failed: Object.values(results).filter(r => r.status === 'failed').length,
          errors: Object.values(results).filter(r => r.status === 'error').length
        }
      };

      setTestResults(testResult);
      setTestHistory(prev => [testResult, ...prev.slice(0, 9)]); // Keep last 10 results

    } catch (error) {
      console.error('Error running AI model tests:', error);
      setTestResults({
        error: error.message,
        timestamp: new Date().toISOString()
      });
    } finally {
      setTesting(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'failed':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      case 'error':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      default:
        return <ClockIcon className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusBadge = (status) => {
    const variants = {
      'success': 'bg-green-100 text-green-800',
      'failed': 'bg-red-100 text-red-800', 
      'error': 'bg-red-100 text-red-800',
      'running': 'bg-blue-100 text-blue-800'
    };

    return (
      <Badge className={variants[status] || 'bg-gray-100 text-gray-800'}>
        {status.toUpperCase()}
      </Badge>
    );
  };

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">AI Model Testing Dashboard</h1>
          <p className="text-gray-600 mt-2">Comprehensive testing suite for all AI models</p>
        </div>
        <div className="flex space-x-3">
          <Button
            onClick={generateTestData}
            disabled={dataGeneration.status === 'generating'}
            variant="outline"
            className="flex items-center space-x-2"
          >
            <DatabaseIcon className="h-4 w-4" />
            <span>Generate Test Data</span>
          </Button>
          <Button
            onClick={() => runAIModelTests(selectedTest)}
            disabled={testing}
            className="flex items-center space-x-2"
          >
            {testing ? (
              <StopIcon className="h-4 w-4 animate-spin" />
            ) : (
              <PlayIcon className="h-4 w-4" />
            )}
            <span>{testing ? 'Testing...' : 'Run Tests'}</span>
          </Button>
        </div>
      </div>

      {/* Test Data Generation Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <DatabaseIcon className="h-5 w-5" />
            <span>Test Data Generation</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{dataGeneration.threatLogs}</div>
              <div className="text-sm text-gray-500">Threat Logs</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{dataGeneration.incidents}</div>
              <div className="text-sm text-gray-500">Security Incidents</div>
            </div>
            <div className="text-center">
              {getStatusBadge(dataGeneration.status)}
              <div className="text-sm text-gray-500 mt-1">Generation Status</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Test Selection */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <BeakerIcon className="h-5 w-5" />
            <span>Test Configuration</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Test Type
              </label>
              <select
                value={selectedTest}
                onChange={(e) => setSelectedTest(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All AI Models</option>
                {Object.entries(aiModelTests).map(([key, test]) => (
                  <option key={key} value={key}>{test.name}</option>
                ))}
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Test Results Summary */}
      {testResults && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <CpuChipIcon className="h-5 w-5" />
              <span>Test Results Summary</span>
              <span className="text-sm text-gray-500">
                ({new Date(testResults.timestamp).toLocaleString()})
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {testResults.error ? (
              <Alert variant="destructive">
                <AlertDescription>{testResults.error}</AlertDescription>
              </Alert>
            ) : (
              <div className="space-y-4">
                <div className="grid grid-cols-4 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-900">{testResults.summary?.total}</div>
                    <div className="text-sm text-gray-500">Total Tests</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">{testResults.summary?.passed}</div>
                    <div className="text-sm text-gray-500">Passed</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-red-600">{testResults.summary?.failed}</div>
                    <div className="text-sm text-gray-500">Failed</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-orange-600">{testResults.summary?.errors}</div>
                    <div className="text-sm text-gray-500">Errors</div>
                  </div>
                </div>

                {/* Individual Test Results */}
                <div className="space-y-3">
                  <h4 className="font-medium text-gray-900">Individual Test Results</h4>
                  {Object.entries(testResults.results || {}).map(([testKey, result]) => (
                    <div key={testKey} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-3">
                        {getStatusIcon(result.status)}
                        <div>
                          <div className="font-medium">{result.name}</div>
                          <div className="text-sm text-gray-500">{result.endpoint}</div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        {result.responseTime && (
                          <span className="text-sm text-gray-500">
                            {result.responseTime}ms
                          </span>
                        )}
                        {getStatusBadge(result.status)}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Test History */}
      {testHistory.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Test History</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {testHistory.map((historyItem, index) => (
                <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <span className="text-sm text-gray-600">
                    {new Date(historyItem.timestamp).toLocaleString()}
                  </span>
                  <div className="flex space-x-2">
                    <span className="text-sm text-green-600">✓ {historyItem.summary?.passed}</span>
                    <span className="text-sm text-red-600">✗ {historyItem.summary?.failed + historyItem.summary?.errors}</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default AIModelTestingDashboard;
