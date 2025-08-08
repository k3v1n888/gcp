import React, { useState, useEffect, useContext } from 'react';
import { UserContext } from '../context/UserContext';
import { 
  ShieldExclamationIcon,
  ExclamationTriangleIcon,
  EyeIcon,
  ClockIcon,
  ChartBarIcon,
  GlobeAltIcon,
  CpuChipIcon,
  BugAntIcon,
  ArrowPathIcon,
  FireIcon
} from '@heroicons/react/24/solid';

/**
 * ⚠️ AI-Powered Threats Dashboard Component
 * Real-time threat monitoring with advanced AI analysis and correlation
 */
const ThreatsManager = () => {
  const { user } = useContext(UserContext);
  const [threats, setThreats] = useState([]);
  const [selectedThreat, setSelectedThreat] = useState(null);
  const [threatDetail, setThreatDetail] = useState(null);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterSeverity, setFilterSeverity] = useState('all');
  const [filterSource, setFilterSource] = useState('all');

  // Real-time threat updates
  useEffect(() => {
    fetchThreats();
    
    // Auto-refresh every 30 seconds for real-time updates
    const interval = setInterval(() => {
      refreshThreats();
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const fetchThreats = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/threats', {
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        setThreats(data);
      } else {
        console.error('Failed to fetch threats');
      }
    } catch (error) {
      console.error('Error fetching threats:', error);
    } finally {
      setLoading(false);
    }
  };

  const refreshThreats = async () => {
    setRefreshing(true);
    try {
      const response = await fetch('/api/threats', {
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        setThreats(data);
      }
    } catch (error) {
      console.error('Error refreshing threats:', error);
    } finally {
      setRefreshing(false);
    }
  };

  const fetchThreatDetail = async (threatId) => {
    setLoading(true);
    
    try {
      const response = await fetch(`/api/threats/${threatId}`, {
        credentials: 'include'
      });
      
      if (response.ok) {
        const result = await response.json();
        setThreatDetail(result);
      }
    } catch (error) {
      console.error('Failed to fetch threat detail:', error);
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
    return colors[severity?.toLowerCase()] || colors.medium;
  };

  const getSeverityIcon = (severity) => {
    switch(severity?.toLowerCase()) {
      case 'critical': return <FireIcon className="w-5 h-5" />;
      case 'high': return <ExclamationTriangleIcon className="w-5 h-5" />;
      case 'medium': return <ShieldExclamationIcon className="w-5 h-5" />;
      case 'low': return <EyeIcon className="w-5 h-5" />;
      default: return <ShieldExclamationIcon className="w-5 h-5" />;
    }
  };

  const getSourceIcon = (source) => {
    const sourceIcons = {
      'wazuh': <CpuChipIcon className="w-5 h-5" />,
      'maltiverse': <GlobeAltIcon className="w-5 h-5" />,
      'misp': <BugAntIcon className="w-5 h-5" />,
      'threatmapper': <ShieldExclamationIcon className="w-5 h-5" />
    };
    return sourceIcons[source?.toLowerCase()] || <CpuChipIcon className="w-5 h-5" />;
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'Unknown';
    return new Date(timestamp).toLocaleString();
  };

  const getFilteredThreats = () => {
    let filtered = threats;

    if (searchTerm) {
      filtered = filtered.filter(threat => 
        threat.threat?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        threat.ip?.includes(searchTerm) ||
        threat.source?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (filterSeverity !== 'all') {
      filtered = filtered.filter(threat => threat.severity?.toLowerCase() === filterSeverity);
    }

    if (filterSource !== 'all') {
      filtered = filtered.filter(threat => threat.source?.toLowerCase() === filterSource);
    }

    return filtered;
  };

  const getThreatStats = () => {
    const total = threats.length;
    const critical = threats.filter(t => t.severity?.toLowerCase() === 'critical').length;
    const high = threats.filter(t => t.severity?.toLowerCase() === 'high').length;
    const anomalies = threats.filter(t => t.is_anomaly).length;
    const uniqueIps = new Set(threats.filter(t => t.ip).map(t => t.ip)).size;

    return { total, critical, high, anomalies, uniqueIps };
  };

  const stats = getThreatStats();
  const filteredThreats = getFilteredThreats();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-blue-900 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-gradient-to-br from-red-500 to-orange-600 rounded-lg">
                <ShieldExclamationIcon className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-red-400 to-orange-400 bg-clip-text text-transparent">
                  Threats Dashboard
                </h1>
                <p className="text-slate-400 mt-1">
                  Real-time threat monitoring with advanced AI correlation
                </p>
              </div>
            </div>
            
            <button
              onClick={refreshThreats}
              disabled={refreshing}
              className={`px-6 py-3 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2 ${
                refreshing
                  ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                  : 'bg-gradient-to-r from-red-600 to-orange-600 text-white hover:from-red-700 hover:to-orange-700'
              }`}
            >
              {refreshing ? (
                <>
                  <div className="w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
                  <span>Refreshing...</span>
                </>
              ) : (
                <>
                  <ArrowPathIcon className="w-5 h-5" />
                  <span>Refresh Threats</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Dashboard Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
          <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Total Threats</p>
                <p className="text-3xl font-bold text-white mt-1">{stats.total}</p>
              </div>
              <ChartBarIcon className="w-12 h-12 text-blue-400" />
            </div>
          </div>
          
          <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Critical Threats</p>
                <p className="text-3xl font-bold text-red-400 mt-1">{stats.critical}</p>
              </div>
              <FireIcon className="w-12 h-12 text-red-400" />
            </div>
          </div>
          
          <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">High Severity</p>
                <p className="text-3xl font-bold text-orange-400 mt-1">{stats.high}</p>
              </div>
              <ExclamationTriangleIcon className="w-12 h-12 text-orange-400" />
            </div>
          </div>
          
          <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">AI Anomalies</p>
                <p className="text-3xl font-bold text-purple-400 mt-1">{stats.anomalies}</p>
              </div>
              <BugAntIcon className="w-12 h-12 text-purple-400" />
            </div>
          </div>
          
          <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Unique IPs</p>
                <p className="text-3xl font-bold text-cyan-400 mt-1">{stats.uniqueIps}</p>
              </div>
              <GlobeAltIcon className="w-12 h-12 text-cyan-400" />
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-xl p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Search Threats</label>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search by threat, IP, or source..."
                className="w-full px-4 py-2 bg-slate-700/50 border border-slate-600/50 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-red-500/50 focus:border-red-500/50"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Filter by Severity</label>
              <select
                value={filterSeverity}
                onChange={(e) => setFilterSeverity(e.target.value)}
                className="w-full px-4 py-2 bg-slate-700/50 border border-slate-600/50 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-red-500/50 focus:border-red-500/50"
              >
                <option value="all">All Severities</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Filter by Source</label>
              <select
                value={filterSource}
                onChange={(e) => setFilterSource(e.target.value)}
                className="w-full px-4 py-2 bg-slate-700/50 border border-slate-600/50 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-red-500/50 focus:border-red-500/50"
              >
                <option value="all">All Sources</option>
                <option value="wazuh">Wazuh</option>
                <option value="maltiverse">Maltiverse</option>
                <option value="misp">MISP</option>
                <option value="threatmapper">ThreatMapper</option>
              </select>
            </div>
          </div>
        </div>

        {/* Threats List */}
        <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-xl overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-700/50">
            <h2 className="text-xl font-bold text-white">
              Recent Threats ({filteredThreats.length})
            </h2>
            <p className="text-slate-400 text-sm mt-1">
              Click on any threat for detailed analysis and AI recommendations
            </p>
          </div>
          
          {loading && !threats.length ? (
            <div className="p-12 text-center">
              <div className="w-8 h-8 border-2 border-blue-400 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
              <p className="text-slate-400">Loading threats...</p>
            </div>
          ) : filteredThreats.length === 0 ? (
            <div className="p-12 text-center">
              <ShieldExclamationIcon className="w-16 h-16 text-slate-600 mx-auto mb-4" />
              <p className="text-slate-400">No threats found matching your criteria</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-700/50 bg-slate-900/50">
                    <th className="text-left py-4 px-6 text-slate-300 font-medium">Threat</th>
                    <th className="text-left py-4 px-6 text-slate-300 font-medium">Severity</th>
                    <th className="text-left py-4 px-6 text-slate-300 font-medium">Source</th>
                    <th className="text-left py-4 px-6 text-slate-300 font-medium">IP Address</th>
                    <th className="text-left py-4 px-6 text-slate-300 font-medium">Timestamp</th>
                    <th className="text-left py-4 px-6 text-slate-300 font-medium">Status</th>
                    <th className="text-left py-4 px-6 text-slate-300 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredThreats.map((threat) => (
                    <tr 
                      key={threat.id} 
                      className="border-b border-slate-700/30 hover:bg-slate-700/20 transition-colors duration-200"
                    >
                      <td className="py-4 px-6">
                        <div className="flex items-start space-x-3">
                          <div className={`p-2 rounded-lg border ${getSeverityColor(threat.severity)}`}>
                            {getSeverityIcon(threat.severity)}
                          </div>
                          <div>
                            <p className="font-medium text-white truncate max-w-xs" title={threat.threat}>
                              {threat.threat || 'Unknown Threat'}
                            </p>
                            {threat.is_anomaly && (
                              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-500/20 text-purple-400 border border-purple-500/30 mt-1">
                                AI Anomaly
                              </span>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="py-4 px-6">
                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${getSeverityColor(threat.severity)}`}>
                          {threat.severity || 'Medium'}
                        </span>
                      </td>
                      <td className="py-4 px-6">
                        <div className="flex items-center space-x-2">
                          {getSourceIcon(threat.source)}
                          <span className="text-slate-300">
                            {threat.source || 'Unknown'}
                          </span>
                        </div>
                      </td>
                      <td className="py-4 px-6">
                        <span className="font-mono text-slate-300">
                          {threat.ip || 'N/A'}
                        </span>
                      </td>
                      <td className="py-4 px-6">
                        <div className="flex items-center space-x-2">
                          <ClockIcon className="w-4 h-4 text-slate-400" />
                          <span className="text-slate-400 text-sm">
                            {formatTimestamp(threat.timestamp)}
                          </span>
                        </div>
                      </td>
                      <td className="py-4 px-6">
                        {threat.cvss_score && (
                          <div className="flex items-center space-x-2">
                            <span className="text-slate-400 text-sm">CVSS:</span>
                            <span className={`font-medium ${threat.cvss_score >= 7 ? 'text-red-400' : threat.cvss_score >= 4 ? 'text-orange-400' : 'text-green-400'}`}>
                              {threat.cvss_score.toFixed(1)}
                            </span>
                          </div>
                        )}
                      </td>
                      <td className="py-4 px-6">
                        <button
                          onClick={() => {
                            setSelectedThreat(threat);
                            fetchThreatDetail(threat.id);
                          }}
                          className="inline-flex items-center px-3 py-2 text-sm font-medium text-blue-400 bg-blue-500/10 border border-blue-500/20 rounded-lg hover:bg-blue-500/20 transition-colors duration-200"
                        >
                          <EyeIcon className="w-4 h-4 mr-2" />
                          Analyze
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Threat Detail Modal */}
        {selectedThreat && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-slate-800 border border-slate-700/50 rounded-xl max-w-4xl w-full max-h-[90vh] overflow-auto">
              <div className="p-6 border-b border-slate-700/50">
                <div className="flex items-center justify-between">
                  <h3 className="text-xl font-bold text-white">Threat Analysis</h3>
                  <button
                    onClick={() => {
                      setSelectedThreat(null);
                      setThreatDetail(null);
                    }}
                    className="text-slate-400 hover:text-white transition-colors duration-200"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
              
              <div className="p-6 space-y-6">
                {loading ? (
                  <div className="flex items-center justify-center py-12">
                    <div className="w-8 h-8 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
                    <span className="ml-3 text-slate-400">Loading threat details...</span>
                  </div>
                ) : (
                  <div className="space-y-6">
                {/* Threat Overview */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h4 className="font-semibold text-white">Threat Details</h4>
                    <div className="space-y-2">
                      <div>
                        <span className="text-slate-400 text-sm">Threat:</span>
                        <p className="text-white">{selectedThreat.threat}</p>
                      </div>
                      <div>
                        <span className="text-slate-400 text-sm">IP Address:</span>
                        <p className="text-white font-mono">{selectedThreat.ip || 'N/A'}</p>
                      </div>
                      <div>
                        <span className="text-slate-400 text-sm">Source:</span>
                        <p className="text-white">{selectedThreat.source}</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <h4 className="font-semibold text-white">Risk Assessment</h4>
                    <div className="space-y-2">
                      <div>
                        <span className="text-slate-400 text-sm">Severity:</span>
                        <span className={`ml-2 inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${getSeverityColor(selectedThreat.severity)}`}>
                          {selectedThreat.severity}
                        </span>
                      </div>
                      {selectedThreat.cvss_score && (
                        <div>
                          <span className="text-slate-400 text-sm">CVSS Score:</span>
                          <span className="ml-2 text-white font-medium">{selectedThreat.cvss_score.toFixed(1)}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* AI Recommendations */}
                {threatDetail.recommendations && (
                  <div className="bg-slate-900/50 border border-slate-700/50 rounded-lg p-4">
                    <h4 className="font-semibold text-white mb-3">AI Recommendations</h4>
                    <div className="space-y-3">
                      {threatDetail.recommendations.map((rec, index) => (
                        <div key={index} className="bg-slate-800/50 rounded-lg p-3">
                          <p className="text-slate-300">{rec.explanation}</p>
                          <div className="mt-2">
                            <span className="text-slate-400 text-sm">Impact: </span>
                            <span className="text-white text-sm">{rec.impact}</span>
                          </div>
                          <div className="mt-1">
                            <span className="text-slate-400 text-sm">Mitigation: </span>
                            <span className="text-white text-sm">{rec.mitigation}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ThreatsManager;
