import React, { useState, useEffect, useContext } from 'react';
import { UserContext } from '../context/UserContext';
import Chatbot from './Chatbot';
import AnalystFeedback from './AnalystFeedback';
import ModelExplanation from './ModelExplanation';
import SoarActionLog from './SoarActionLog';
import { 
  MagnifyingGlassIcon, 
  ExclamationTriangleIcon, 
  FireIcon, 
  ShieldCheckIcon, 
  EyeIcon,
  ChatBubbleLeftRightIcon,
  XMarkIcon,
  ShieldExclamationIcon,
  ArrowPathIcon,
  ChartBarIcon,
  BugAntIcon,
  GlobeAltIcon,
  ClockIcon,
  CpuChipIcon
} from '@heroicons/react/24/outline';

/**
 * ⚠️ AI-Powered Threats Dashboard Component
 * Real-time threat monitoring with advanced AI analysis and correlation
 */
const ThreatsManager = () => {
  const { user } = useContext(UserContext);

  // Add the same components from ThreatDetail.jsx
  const SeverityBadge = ({ severity }) => {
    const severityStyles = {
      critical: 'bg-red-600 text-white',
      high: 'bg-orange-500 text-white',
      medium: 'bg-yellow-400 text-black',
      low: 'bg-sky-500 text-white',
      unknown: 'bg-slate-500 text-white',
    };
    const severityKey = typeof severity === 'string' ? severity.toLowerCase() : 'unknown';
    return (
      <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${severityStyles[severityKey] || severityStyles.unknown}`}>
        {severity.toUpperCase()}
      </span>
    );
  };

  const ReputationScore = ({ score }) => {
    const numericScore = typeof score === 'number' ? score : 0;
    const getScoreColor = () => {
      if (numericScore > 75) return 'bg-red-600';
      if (numericScore > 40) return 'bg-orange-500';
      return 'bg-green-600';
    };
    return (
      <div className="flex items-center">
        <div className="w-full bg-slate-700 rounded-full h-2.5">
          <div className={`${getScoreColor()} h-2.5 rounded-full`} style={{ width: `${numericScore}%` }} title={`MISP Score: ${numericScore}`}></div>
        </div>
        <span className="text-xs font-semibold ml-3 text-slate-300">{numericScore}</span>
      </div>
    );
  };

  const DetailCard = ({ title, children }) => (
    <div className="widget-card p-6 mb-6">
      <h2 className="text-xl font-semibold mb-4 text-sky-400">{title}</h2>
      <div className="text-slate-300 leading-relaxed prose prose-invert max-w-none">{children}</div>
    </div>
  );

  const TimelineItem = ({ log, isLast }) => {
    const borderColor = isLast ? 'border-transparent' : 'border-slate-600';
    return (
      <div className="relative flex items-start pl-8">
        <div className="absolute left-0 flex flex-col items-center h-full">
          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-sky-500 flex items-center justify-center ring-4 ring-slate-800 z-10">
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
          <div className={`w-px flex-grow ${borderColor}`}></div>
        </div>
        <div className="pb-8 ml-4">
          <p className="text-sm text-slate-400">{new Date(log.timestamp).toLocaleString()}</p>
          <h3 className="font-semibold text-slate-200">{log.threat}</h3>
          <p className="text-sm text-slate-500">Source: {log.source} | IP: {log.ip}</p>
        </div>
      </div>
    );
  };
  const [threats, setThreats] = useState([]);
  const [selectedThreat, setSelectedThreat] = useState(null);
  const [threatDetail, setThreatDetail] = useState(null);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterSeverity, setFilterSeverity] = useState('all');
  const [filterSource, setFilterSource] = useState('all');
  const [showAnalystFeedback, setShowAnalystFeedback] = useState(false);
  const [showAIChat, setShowAIChat] = useState(false);

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
    setThreatDetail(null); // Clear previous data
    
    try {
      const response = await fetch(`/api/threats/${threatId}`, {
        credentials: 'include'
      });
      
      if (response.ok) {
        const result = await response.json();
        setThreatDetail(result);
      } else {
        console.error(`Failed to fetch threat detail: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      console.error('Failed to fetch threat detail:', error);
    } finally {
      setLoading(false);
    }
  };

  // AI Explain function - re-triggers AI analysis
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
            <div className="bg-slate-900 rounded-lg max-w-6xl w-full max-h-[90vh] overflow-y-auto">
              <div className="sticky top-0 bg-slate-900 border-b border-slate-700 p-6 z-10">
                <div className="flex justify-between items-start">
                  <div>
                    <div className="flex items-center gap-4 mb-2">
                      <h1 className="text-3xl font-bold text-slate-100">{selectedThreat.threat}</h1>
                      {selectedThreat.is_anomaly && (
                        <span className="bg-fuchsia-500/20 text-fuchsia-300 border border-fuchsia-400 text-sm font-semibold px-3 py-1 rounded-full">
                          ANOMALY
                        </span>
                      )}
                      {selectedThreat.source === 'UEBA Engine' && (
                        <span className="bg-amber-500/20 text-amber-300 border border-amber-400 text-sm font-semibold px-3 py-1 rounded-full">
                          INSIDER THREAT
                        </span>
                      )}
                    </div>
                    <p className="text-slate-400 mb-4">
                      Detected from {selectedThreat.source} at {new Date(selectedThreat.timestamp).toLocaleString()}
                    </p>
                  </div>
                  <button
                    onClick={() => {
                      setSelectedThreat(null);
                      setThreatDetail(null);
                    }}
                    className="text-slate-400 hover:text-white transition-colors p-2"
                  >
                    <XMarkIcon className="w-6 h-6" />
                  </button>
                </div>
                
                {/* Action Buttons */}
                <div className="flex flex-wrap gap-3 mt-4">
                  <button
                    onClick={() => setShowAnalystFeedback(!showAnalystFeedback)}
                    className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors duration-200"
                  >
                    <EyeIcon className="w-4 h-4 mr-2" />
                    {showAnalystFeedback ? 'Hide' : 'Show'} Analyst Feedback
                  </button>
                  
                  <button
                    onClick={() => setShowAIChat(!showAIChat)}
                    className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 transition-colors duration-200"
                  >
                    <ChatBubbleLeftRightIcon className="w-4 h-4 mr-2" />
                    {showAIChat ? 'Hide' : 'Show'} AI Chat
                  </button>
                </div>
              </div>

              {loading ? (
                <div className="flex items-center justify-center p-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400"></div>
                  <span className="ml-3 text-slate-300">Loading Analysis...</span>
                </div>
              ) : !threatDetail ? (
                <div className="p-6 text-center text-slate-400">
                  <div className="text-red-500">Error: Threat data could not be loaded.</div>
                  <button
                    onClick={() => fetchThreatDetail(selectedThreat.id)}
                    className="mt-4 inline-flex items-center px-4 py-2 text-sm font-medium text-blue-400 bg-blue-500/10 border border-blue-500/20 rounded-lg hover:bg-blue-500/20 transition-colors duration-200"
                  >
                    Retry Analysis
                  </button>
                </div>
              ) : (
                <div className="p-6">
                  {/* Event Telemetry - matching ThreatDetail.jsx */}
                  <DetailCard title="Event Telemetry">
                    <dl className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-4">
                      <div className="py-2">
                        <dt className="font-semibold text-slate-400">Attacker IP</dt>
                        <dd className="font-mono text-slate-200">{threatDetail.ip}</dd>
                      </div>
                      <div className="py-2">
                        <dt className="font-semibold text-slate-400">IP Reputation Score (from MISP)</dt>
                        <dd className="mt-1 w-40">
                          <ReputationScore score={threatDetail.ip_reputation_score} />
                        </dd>
                      </div>
                      <div className="py-2">
                        <dt className="font-semibold text-slate-400">AI-Assigned Severity</dt>
                        <dd className="mt-1">
                          <SeverityBadge severity={threatDetail.severity} />
                        </dd>
                      </div>
                      <div className="py-2">
                        <dt className="font-semibold text-slate-400">Associated CVE</dt>
                        <dd className="font-mono text-slate-200">
                          {threatDetail.cve_id ? (
                            <a 
                              href={`https://cve.mitre.org/cgi-bin/cvename.cgi?name=${threatDetail.cve_id}`} 
                              target="_blank" 
                              rel="noopener noreferrer" 
                              className="text-blue-400 hover:underline"
                            >
                              {threatDetail.cve_id}
                            </a>
                          ) : (
                            'N/A'
                          )}
                        </dd>
                      </div>
                    </dl>
                  </DetailCard>

                  {/* Attack Timeline - matching ThreatDetail.jsx */}
                  {threatDetail.timeline_threats && threatDetail.timeline_threats.length > 1 && (
                    <DetailCard title="Attack Timeline">
                      <div>
                        {threatDetail.timeline_threats.map((log, index, array) => (
                          <TimelineItem key={log.id} log={log} isLast={index === array.length - 1} />
                        ))}
                      </div>
                    </DetailCard>
                  )}

                  {/* MISP Summary - matching ThreatDetail.jsx */}
                  {threatDetail.misp_summary && (
                    <DetailCard title="Quantum Intel (MISP) Summary">
                      <p className="italic text-slate-200">{threatDetail.misp_summary}</p>
                    </DetailCard>
                  )}

                  {/* Correlated Threat Analysis - matching ThreatDetail.jsx */}
                  {threatDetail.correlation && (
                    <DetailCard title="Correlated Threat Analysis">
                      <h3 className="font-bold text-lg mb-2">{threatDetail.correlation.title}</h3>
                      <p className="mb-2">{threatDetail.correlation.summary}</p>
                      <div className="text-sm">
                        <span className="font-semibold">Associated CVE: </span>
                        <span className="font-mono">{threatDetail.correlation.cve_id || 'N/A'}</span>
                      </div>
                    </DetailCard>
                  )}

                  {/* AI Analysis - matching ThreatDetail.jsx */}
                  {threatDetail.recommendations ? (
                    <>
                      <DetailCard title="Quantum AI Analysis: Threat Explanation">
                        <p>{threatDetail.recommendations.explanation}</p>
                      </DetailCard>
                      <DetailCard title="Quantum AI Analysis: Potential Impact">
                        <p>{threatDetail.recommendations.impact}</p>
                      </DetailCard>
                      <DetailCard title="Quantum AI Analysis: Mitigation Protocols">
                        <ul className="list-disc list-inside space-y-2">
                          {threatDetail.recommendations.mitigation.map((step, index) => (
                            <li key={index}>{step}</li>
                          ))}
                        </ul>
                      </DetailCard>
                    </>
                  ) : (
                    <DetailCard title="AI Analysis">
                      <p>Could not generate AI recommendations for this threat.</p>
                    </DetailCard>
                  )}

                  {/* Explainable AI (XAI) Analysis - matching ThreatDetail.jsx */}
                  <DetailCard title="Explainable AI (XAI) Analysis">
                    <ModelExplanation 
                      explanation={threatDetail.xai_explanation}
                      threatId={selectedThreat.id}
                      existingFeedback={threatDetail.analyst_feedback}
                    />
                  </DetailCard>

                  {/* Automated Response Log - matching ThreatDetail.jsx */}
                  <DetailCard title="Automated Response Log">
                    <SoarActionLog actions={threatDetail.soar_actions} />
                  </DetailCard>

                  {/* AI Chat - matching ThreatDetail.jsx */}
                  {showAIChat && (
                    <DetailCard title="Quantum AI Bot">
                      <Chatbot threatContext={threatDetail} />
                    </DetailCard>
                  )}

                  {/* Analyst Feedback Form */}
                  {showAnalystFeedback && threatDetail.xai_explanation && (
                    <DetailCard title="Analyst Feedback & Model Update">
                      <AnalystFeedback
                        explanation={threatDetail.xai_explanation}
                        threatId={selectedThreat.id}
                        existingFeedback={threatDetail.analyst_feedback}
                        onFeedbackSubmitted={() => {
                          setShowAnalystFeedback(false);
                          fetchThreatDetail(selectedThreat.id);
                        }}
                      />
                    </DetailCard>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ThreatsManager;
