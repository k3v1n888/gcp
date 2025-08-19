

import React, { useState, useEffect, useContext } from 'react';
import { UserContext } from '../context/UserContext';
import { useDevUser } from '../context/DevUserContext';
import { isDevelopment, getApiBaseUrl } from '../utils/environment';
import { 
  ShieldCheckIcon, 
  ExclamationTriangleIcon,
  CpuChipIcon,
  ClockIcon,
  ChartBarIcon,
  PlayIcon,
  SparklesIcon,
  EyeIcon
} from '@heroicons/react/24/solid';

/**
 * 🤖 AI-Powered Incident Management Component
 * Next-generation incident orchestration with industry-standard AI analysis
 */
const AIIncidentManager = () => {
  // Use appropriate context/hook based on environment
  let user = null;
  
  try {
      if (isDevelopment()) {
          const devContext = useDevUser();
          user = devContext.user;
          console.log('🔧 AIIncidentManager using DevUserContext, user:', user);
      }
  } catch (e) {
      console.log('🔧 DevUserContext not available in AIIncidentManager, falling back');
  }
  
  try {
      if (!isDevelopment()) {
          const prodContext = useContext(UserContext);
          user = prodContext?.user;
          console.log('🔒 AIIncidentManager using UserContext, user:', user);
      }
  } catch (e) {
      console.log('🔒 UserContext not available in AIIncidentManager');
  }

  const [incidents, setIncidents] = useState([]);
  const [orchestrationStatus, setOrchestrationStatus] = useState('idle');
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [dashboardMetrics, setDashboardMetrics] = useState(null);
  const [loading, setLoading] = useState(false);

  // Fetch AI-enhanced incidents
  useEffect(() => {
    fetchAIIncidents();
    fetchDashboardMetrics();
    
    // Auto-refresh every 2 minutes
    const interval = setInterval(() => {
      fetchAIIncidents();
      fetchDashboardMetrics();
    }, 120000);
    
    return () => clearInterval(interval);
  }, []);

  const fetchAIIncidents = async () => {
    try {
      const response = await fetch('/api/v1/incidents/ai-enhanced', {
        headers: {
          'Authorization': `Bearer ${user.token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const result = await response.json();
        setIncidents(result.data.incidents || []);
      }
    } catch (error) {
      console.error('Failed to fetch AI incidents:', error);
    }
  };

  const fetchDashboardMetrics = async () => {
    try {
      const response = await fetch('/api/v1/incidents/dashboard/ai-metrics?days=7', {
        headers: {
          'Authorization': `Bearer ${user.token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const result = await response.json();
        setDashboardMetrics(result.data);
      }
    } catch (error) {
      console.error('Failed to fetch dashboard metrics:', error);
    }
  };

  const triggerAIOrchestration = async () => {
    setOrchestrationStatus('running');
    setLoading(true);
    
    try {
      const baseUrl = process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8001';
      const response = await fetch(`${baseUrl}/api/v1/incidents/orchestrate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const result = await response.json();
        setOrchestrationStatus('completed');
        
        // Refresh incidents after orchestration
        setTimeout(() => {
          fetchAIIncidents();
          fetchDashboardMetrics();
        }, 2000);
        
        // Reset status after 3 seconds
        setTimeout(() => setOrchestrationStatus('idle'), 3000);
      } else {
        setOrchestrationStatus('error');
        setTimeout(() => setOrchestrationStatus('idle'), 3000);
      }
    } catch (error) {
      console.error('AI orchestration failed:', error);
      setOrchestrationStatus('error');
      setTimeout(() => setOrchestrationStatus('idle'), 3000);
    } finally {
      setLoading(false);
    }
  };

  const fetchIncidentAnalysis = async (incidentId) => {
    setLoading(true);
    
    try {
      const response = await fetch(`/api/v1/incidents/${incidentId}/ai-analysis`, {
        headers: {
          'Authorization': `Bearer ${user.token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const result = await response.json();
        setAiAnalysis(result.data);
      }
    } catch (error) {
      console.error('Failed to fetch incident analysis:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity) => {
    const colors = {
      critical: 'text-red-400 bg-red-500/10 border-red-500/20',
      high: 'text-orange-400 bg-orange-500/10 border-orange-500/20',
      medium: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
      low: 'text-green-400 bg-green-500/10 border-green-500/20'
    };
    return colors[severity] || colors.medium;
  };

  const getStatusColor = (status) => {
    const colors = {
      open: 'text-red-400 bg-red-500/10',
      investigating: 'text-yellow-400 bg-yellow-500/10',
      resolved: 'text-green-400 bg-green-500/10',
      closed: 'text-gray-400 bg-gray-500/10'
    };
    return colors[status] || colors.open;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-blue-900 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg">
                <CpuChipIcon className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                  AI Incident Orchestrator
                </h1>
                <p className="text-slate-400 mt-1">
                  Next-generation incident management powered by advanced AI
                </p>
              </div>
            </div>
            
            <button
              onClick={triggerAIOrchestration}
              disabled={loading || orchestrationStatus === 'running'}
              className={`px-6 py-3 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2 ${
                orchestrationStatus === 'running'
                  ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
                  : orchestrationStatus === 'completed'
                  ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                  : orchestrationStatus === 'error'
                  ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                  : 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700'
              }`}
            >
              {orchestrationStatus === 'running' ? (
                <>
                  <div className="w-4 h-4 border-2 border-yellow-400 border-t-transparent rounded-full animate-spin" />
                  <span>Orchestrating...</span>
                </>
              ) : orchestrationStatus === 'completed' ? (
                <>
                  <ShieldCheckIcon className="w-5 h-5" />
                  <span>Completed</span>
                </>
              ) : orchestrationStatus === 'error' ? (
                <>
                  <ExclamationTriangleIcon className="w-5 h-5" />
                  <span>Error</span>
                </>
              ) : (
                <>
                  <PlayIcon className="w-5 h-5" />
                  <span>Run AI Orchestration</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Dashboard Metrics */}
        {dashboardMetrics && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-xl p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-slate-400 text-sm">Total Incidents</p>
                  <p className="text-3xl font-bold text-white mt-1">{dashboardMetrics.total_incidents}</p>
                </div>
                <ChartBarIcon className="w-12 h-12 text-blue-400" />
              </div>
            </div>
            
            <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-xl p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-slate-400 text-sm">Avg Resolution</p>
                  <p className="text-3xl font-bold text-white mt-1">{dashboardMetrics.average_resolution_time}</p>
                </div>
                <ClockIcon className="w-12 h-12 text-green-400" />
              </div>
            </div>
            
            <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-xl p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-slate-400 text-sm">Threat Ratio</p>
                  <p className="text-3xl font-bold text-white mt-1">{dashboardMetrics.threat_to_incident_ratio}:1</p>
                </div>
                <SparklesIcon className="w-12 h-12 text-purple-400" />
              </div>
            </div>
            
            <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-xl p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-slate-400 text-sm">AI Actions</p>
                  <p className="text-3xl font-bold text-white mt-1">{dashboardMetrics.automated_actions?.successful || 0}</p>
                </div>
                <CpuChipIcon className="w-12 h-12 text-yellow-400" />
              </div>
            </div>
          </div>
        )}

        {/* Incidents List */}
        <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-xl overflow-hidden">
          <div className="p-6 border-b border-slate-700/50">
            <h2 className="text-2xl font-bold text-white flex items-center space-x-2">
              <SparklesIcon className="w-6 h-6 text-blue-400" />
              <span>AI-Enhanced Incidents</span>
              <span className="text-sm font-normal text-slate-400">({incidents.length} total)</span>
            </h2>
          </div>
          
          <div className="max-h-96 overflow-y-auto scrollbar-thin">
            {incidents.length === 0 ? (
              <div className="p-8 text-center">
                <ShieldCheckIcon className="w-16 h-16 text-slate-600 mx-auto mb-4" />
                <p className="text-slate-400 text-lg">No incidents found</p>
                <p className="text-slate-500 text-sm mt-1">AI orchestration will create incidents from threats</p>
              </div>
            ) : (
              <div className="divide-y divide-slate-700/50">
                {incidents.map((incident) => (
                  <div 
                    key={incident.id} 
                    className="p-6 hover:bg-slate-700/30 transition-colors cursor-pointer"
                    onClick={() => {
                      setSelectedIncident(incident);
                      fetchIncidentAnalysis(incident.id);
                    }}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <h3 className="text-lg font-semibold text-white">{incident.title}</h3>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getSeverityColor(incident.severity)}`}>
                            {incident.severity?.toUpperCase()}
                          </span>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(incident.status)}`}>
                            {incident.status?.toUpperCase()}
                          </span>
                        </div>
                        
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-slate-400">
                          <div>
                            <span className="font-medium text-slate-300">Threats:</span> {incident.ai_analytics.threat_count}
                          </div>
                          <div>
                            <span className="font-medium text-slate-300">IPs:</span> {incident.ai_analytics.unique_ips.length}
                          </div>
                          <div>
                            <span className="font-medium text-slate-300">Duration:</span> {incident.ai_analytics.time_span_hours}h
                          </div>
                          <div>
                            <span className="font-medium text-slate-300">Anomalies:</span> {incident.ai_analytics.has_anomalies ? 'Yes' : 'No'}
                          </div>
                        </div>
                        
                        <div className="mt-3">
                          <div className="flex flex-wrap gap-2">
                            {incident.indicators.ips.slice(0, 3).map(ip => (
                              <span key={ip} className="px-2 py-1 bg-red-500/20 text-red-300 text-xs rounded border border-red-500/30">
                                {ip}
                              </span>
                            ))}
                            {incident.indicators.ips.length > 3 && (
                              <span className="px-2 py-1 bg-slate-600 text-slate-300 text-xs rounded">
                                +{incident.indicators.ips.length - 3} more
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      
                      <div className="ml-4">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedIncident(incident);
                            fetchIncidentAnalysis(incident.id);
                          }}
                          className="p-2 text-slate-400 hover:text-blue-400 hover:bg-blue-500/10 rounded-lg transition-all"
                        >
                          <EyeIcon className="w-5 h-5" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* AI Analysis Modal */}
        {selectedIncident && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur flex items-center justify-center p-4 z-50">
            <div className="bg-slate-800 border border-slate-700 rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6 border-b border-slate-700">
                <div className="flex items-center justify-between">
                  <h3 className="text-2xl font-bold text-white flex items-center space-x-2">
                    <CpuChipIcon className="w-6 h-6 text-blue-400" />
                    <span>AI Incident Analysis</span>
                  </h3>
                  <button
                    onClick={() => {
                      setSelectedIncident(null);
                      setAiAnalysis(null);
                    }}
                    className="text-slate-400 hover:text-white p-2 hover:bg-slate-700 rounded-lg transition-colors"
                  >
                    ✕
                  </button>
                </div>
              </div>
              
              <div className="p-6">
                {loading ? (
                  <div className="flex items-center justify-center py-12">
                    <div className="w-8 h-8 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
                    <span className="ml-3 text-slate-400">Analyzing incident with AI...</span>
                  </div>
                ) : aiAnalysis ? (
                  <div className="space-y-6">
                    {/* AI Confidence & Risk Assessment */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="bg-slate-700/30 rounded-lg p-4">
                        <h4 className="text-lg font-semibold text-white mb-3">AI Confidence</h4>
                        <div className="flex items-center space-x-3">
                          <div className="flex-1 bg-slate-700 rounded-full h-2">
                            <div 
                              className="h-2 bg-gradient-to-r from-blue-500 to-green-500 rounded-full transition-all duration-500"
                              style={{ width: `${aiAnalysis.ai_confidence}%` }}
                            />
                          </div>
                          <span className="text-white font-medium">{aiAnalysis.ai_confidence}%</span>
                        </div>
                      </div>
                      
                      <div className="bg-slate-700/30 rounded-lg p-4">
                        <h4 className="text-lg font-semibold text-white mb-3">Risk Level</h4>
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${getSeverityColor(selectedIncident.severity)}`}>
                          {selectedIncident.severity?.toUpperCase()} RISK
                        </span>
                      </div>
                    </div>

                    {/* Attack Timeline */}
                    {aiAnalysis.timeline && (
                      <div className="bg-slate-700/30 rounded-lg p-4">
                        <h4 className="text-lg font-semibold text-white mb-3">Attack Timeline</h4>
                        <div className="space-y-2 max-h-48 overflow-y-auto">
                          {aiAnalysis.timeline.map((event, index) => (
                            <div key={index} className="flex items-center space-x-3 text-sm">
                              <span className="text-slate-400 w-4">{event.sequence}.</span>
                              <span className="text-slate-400 w-20">{new Date(event.timestamp).toLocaleTimeString()}</span>
                              <span className="flex-1 text-slate-300">{event.event}</span>
                              <span className={`px-2 py-1 rounded text-xs ${getSeverityColor(event.severity)}`}>
                                {event.severity}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* MITRE ATT&CK Mapping */}
                    {aiAnalysis.mitre_attack_mapping && (
                      <div className="bg-slate-700/30 rounded-lg p-4">
                        <h4 className="text-lg font-semibold text-white mb-3">MITRE ATT&CK Framework</h4>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          <div>
                            <p className="text-slate-400 text-sm">Tactics</p>
                            <div className="flex flex-wrap gap-1 mt-1">
                              {aiAnalysis.mitre_attack_mapping.tactics.map(tactic => (
                                <span key={tactic} className="px-2 py-1 bg-purple-500/20 text-purple-300 text-xs rounded border border-purple-500/30">
                                  {tactic}
                                </span>
                              ))}
                            </div>
                          </div>
                          <div>
                            <p className="text-slate-400 text-sm">Techniques</p>
                            <div className="flex flex-wrap gap-1 mt-1">
                              {aiAnalysis.mitre_attack_mapping.techniques.map(technique => (
                                <span key={technique} className="px-2 py-1 bg-blue-500/20 text-blue-300 text-xs rounded border border-blue-500/30">
                                  {technique}
                                </span>
                              ))}
                            </div>
                          </div>
                          <div>
                            <p className="text-slate-400 text-sm">Coverage</p>
                            <div className="flex items-center space-x-2 mt-1">
                              <div className="flex-1 bg-slate-700 rounded-full h-2">
                                <div 
                                  className="h-2 bg-gradient-to-r from-orange-500 to-red-500 rounded-full"
                                  style={{ width: `${aiAnalysis.mitre_attack_mapping.coverage_percentage}%` }}
                                />
                              </div>
                              <span className="text-white text-sm">{aiAnalysis.mitre_attack_mapping.coverage_percentage}%</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Recommendations */}
                    {aiAnalysis.recommendations && (
                      <div className="bg-slate-700/30 rounded-lg p-4">
                        <h4 className="text-lg font-semibold text-white mb-3">AI Recommendations</h4>
                        <p className="text-slate-300 text-sm">Advanced recommendations would be displayed here based on the AI analysis.</p>
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="text-slate-400 text-center py-8">No analysis available</p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AIIncidentManager;
