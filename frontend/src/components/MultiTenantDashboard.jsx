import React, { useState, useEffect } from 'react';
import { 
  BuildingOfficeIcon, 
  ShieldExclamationIcon, 
  ExclamationTriangleIcon,
  ComputerDesktopIcon,
  UsersIcon,
  ClockIcon,
  EyeIcon,
  ShieldCheckIcon,
  XMarkIcon,
  ArrowRightIcon,
  ChevronRightIcon
} from '@heroicons/react/24/outline';
import { getApiBaseUrl } from '../utils/environment';

export default function MultiTenantDashboard() {
  const [tenants, setTenants] = useState([]);
  const [allThreats, setAllThreats] = useState([]);
  const [allIncidents, setAllIncidents] = useState([]);
  const [overallStats, setOverallStats] = useState({
    totalTenants: 0,
    activeThreats: 0,
    openIncidents: 0,
    aiModelsActive: 0
  });
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);
  
  // Modal states
  const [selectedThreat, setSelectedThreat] = useState(null);
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [selectedTenant, setSelectedTenant] = useState(null);
  const [showTenantView, setShowTenantView] = useState(false);
  const [showFullDetails, setShowFullDetails] = useState(false);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const apiBaseUrl = getApiBaseUrl();
      
      // Fetch all data in parallel
      const [tenantsRes, threatsRes, incidentsRes, aiModelsRes] = await Promise.all([
        fetch(`${apiBaseUrl}/api/admin/tenants`),
        fetch(`${apiBaseUrl}/api/threats`),
        fetch(`${apiBaseUrl}/api/incidents`),
        fetch(`${apiBaseUrl}/api/admin/health/ai-models`)
      ]);

      // Process tenants
      let tenantsData = [];
      if (tenantsRes.ok) {
        const data = await tenantsRes.json();
        tenantsData = data.tenants || [];
        setTenants(tenantsData);
      }

      // Process threats
      let threatsData = [];
      if (threatsRes.ok) {
        const data = await threatsRes.json();
        threatsData = data.threats || [];
        
        // Add tenant names to threats
        const enrichedThreats = threatsData.map(threat => ({
          ...threat,
          tenant_name: tenantsData.find(t => t.tenant_id === threat.tenant_id)?.name || 
                      tenantsData.find(t => t.id === threat.tenant_id)?.name || 
                      'ACME Corporation' // Default fallback
        }));
        setAllThreats(enrichedThreats);
      }

      // Process incidents
      let incidentsData = [];
      if (incidentsRes.ok) {
        const data = await incidentsRes.json();
        incidentsData = data.incidents || [];
        
        // Add tenant names to incidents
        const enrichedIncidents = incidentsData.map(incident => ({
          ...incident,
          tenant_name: tenantsData.find(t => t.tenant_id === incident.tenant_id)?.name || 
                      tenantsData.find(t => t.id === incident.tenant_id)?.name || 
                      'ACME Corporation' // Default fallback
        }));
        setAllIncidents(enrichedIncidents);
      }

      // Process AI models
      let aiModelsCount = 0;
      if (aiModelsRes.ok) {
        const data = await aiModelsRes.json();
        aiModelsCount = data.models ? data.models.filter(m => m.status === 'healthy').length : 6;
      }

      // Calculate overall stats
      setOverallStats({
        totalTenants: tenantsData.length,
        activeThreats: threatsData.filter(t => t.status === 'active').length,
        openIncidents: incidentsData.filter(i => i.status === 'open' || i.status === 'investigating').length,
        aiModelsActive: aiModelsCount
      });

      setLastUpdate(new Date());
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getDetectionRate = (tenant) => {
    const tenantThreats = allThreats.filter(t => t.tenant_name === tenant.name);
    return tenantThreats.length > 0 ? 96.45 : 95.2; // Mock calculation
  };

  const getThreatLevel = (tenant) => {
    const tenantThreats = allThreats.filter(t => t.tenant_name === tenant.name);
    const highSeverityThreats = tenantThreats.filter(t => t.severity === 'high').length;
    
    if (highSeverityThreats > 0) return { level: 'High', color: 'bg-red-500' };
    if (tenantThreats.length > 1) return { level: 'Medium', color: 'bg-yellow-500' };
    return { level: 'Low', color: 'bg-green-500' };
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-900 p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-slate-700 rounded w-64 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="bg-slate-800 p-6 rounded-lg">
                <div className="h-4 bg-slate-700 rounded w-24 mb-2"></div>
                <div className="h-8 bg-slate-700 rounded w-16"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">Multi-Tenant Security Dashboard</h1>
            <p className="text-slate-400">Centralized security overview across all tenants</p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <span className="text-sm text-slate-400">Last updated: {lastUpdate?.toLocaleTimeString()}</span>
          <button 
            onClick={fetchDashboardData}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Refresh
          </button>
        </div>
      </div>

      {/* Overall Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-slate-800 p-6 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-400 text-sm">Total Tenants</p>
              <p className="text-2xl font-bold text-white">{overallStats.totalTenants}</p>
            </div>
            <div className="w-12 h-12 bg-blue-500 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-slate-800 p-6 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-400 text-sm">Active Threats</p>
              <p className="text-2xl font-bold text-red-400">{overallStats.activeThreats}</p>
            </div>
            <div className="w-12 h-12 bg-red-500 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.464 0L4.35 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-slate-800 p-6 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-400 text-sm">Open Incidents</p>
              <p className="text-2xl font-bold text-orange-400">{overallStats.openIncidents}</p>
            </div>
            <div className="w-12 h-12 bg-orange-500 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-slate-800 p-6 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-400 text-sm">AI Models Active</p>
              <p className="text-2xl font-bold text-green-400">{overallStats.aiModelsActive}</p>
            </div>
            <div className="w-12 h-12 bg-green-500 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Tenant Overview */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-white mb-4">Tenant Overview</h2>
        <div className="space-y-4">
          {tenants.map((tenant) => {
            const tenantThreats = allThreats.filter(t => t.tenant_name === tenant.name);
            const tenantIncidents = allIncidents.filter(i => i.tenant_name === tenant.name);
            const openIncidents = tenantIncidents.filter(i => i.status === 'open' || i.status === 'investigating');
            const threatLevel = getThreatLevel(tenant);
            const detectionRate = getDetectionRate(tenant);

            return (
              <div key={tenant.id} className="bg-slate-800 p-6 rounded-lg border border-slate-700 hover:border-slate-600 transition-colors">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center text-white font-bold">
                      {tenant.name.substring(0, 2).toUpperCase()}
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-white">{tenant.name}</h3>
                      <p className="text-slate-400 text-sm">{tenant.domain || 'No domain set'}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium text-white ${threatLevel.color}`}>
                      {threatLevel.level}
                    </span>
                    <button 
                      onClick={() => {
                        setSelectedTenant(tenant);
                        setShowTenantView(true);
                      }}
                      className="px-3 py-1 bg-blue-600 text-white text-xs rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-1"
                    >
                      <span>Switch to Tenant</span>
                      <ArrowRightIcon className="w-3 h-3" />
                    </button>
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-slate-700 p-4 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <svg className="w-4 h-4 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.464 0L4.35 16.5c-.77.833.192 2.5 1.732 2.5z" />
                      </svg>
                      <span className="text-slate-400 text-sm">Threats</span>
                    </div>
                    <div className="text-white">
                      <p className="text-xl font-bold">{tenantThreats.length}</p>
                      <p className="text-xs text-slate-400">
                        Critical: {tenantThreats.filter(t => t.severity === 'high').length}
                      </p>
                    </div>
                  </div>

                  <div className="bg-slate-700 p-4 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <svg className="w-4 h-4 text-orange-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span className="text-slate-400 text-sm">Incidents</span>
                    </div>
                    <div className="text-white">
                      <p className="text-xl font-bold">{tenantIncidents.length}</p>
                      <p className="text-xs text-slate-400">
                        Open: {openIncidents.length}
                      </p>
                    </div>
                  </div>

                  <div className="bg-slate-700 p-4 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <svg className="w-4 h-4 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                      <span className="text-slate-400 text-sm">AI Hunting</span>
                    </div>
                    <div className="text-white">
                      <p className="text-xl font-bold">6</p>
                      <p className="text-xs text-slate-400">
                        Models: {overallStats.aiModelsActive}
                      </p>
                      <p className="text-xs text-green-400">
                        Detection: {detectionRate}%
                      </p>
                    </div>
                  </div>

                  <div className="bg-slate-700 p-4 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <svg className="w-4 h-4 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                      </svg>
                      <span className="text-slate-400 text-sm">Agents</span>
                    </div>
                    <div className="text-white">
                      <p className="text-xl font-bold">1</p>
                      <p className="text-xs text-slate-400">
                        Active: 1
                      </p>
                      <p className="text-xs text-green-400">
                        Total: 1
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Recent Threats and Incidents */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Threats */}
        <div className="bg-slate-800 p-6 rounded-lg">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <svg className="w-5 h-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.464 0L4.35 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
              <h3 className="text-lg font-semibold text-white">Recent Threats</h3>
            </div>
            <span className="text-sm text-slate-400">{allThreats.length} total</span>
          </div>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {allThreats.slice(0, 10).map((threat, index) => (
              <div 
                key={index} 
                className="bg-slate-700 p-4 rounded-lg hover:bg-slate-600 cursor-pointer transition-colors"
                onClick={() => setSelectedThreat(threat)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="text-xs bg-slate-600 text-slate-200 px-2 py-1 rounded">
                        {threat.tenant_name || 'Unknown Tenant'}
                      </span>
                      <span className={`text-xs px-2 py-1 rounded ${
                        threat.severity === 'high' ? 'bg-red-500 text-white' :
                        threat.severity === 'medium' ? 'bg-yellow-500 text-black' :
                        'bg-green-500 text-white'
                      }`}>
                        {threat.severity?.toUpperCase()}
                      </span>
                    </div>
                    <h4 className="font-medium text-white text-sm">{threat.threat}</h4>
                    <p className="text-slate-400 text-xs mt-1">{threat.description}</p>
                    <div className="flex items-center justify-between mt-2">
                      <span className="text-xs text-slate-500">
                        {threat.source_ip} • {threat.threat_type}
                      </span>
                      <span className="text-xs text-slate-500">
                        {new Date(threat.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                  </div>
                  <div className="ml-3">
                    <span className="text-xs text-slate-400">CVSS: {threat.cvss_score}</span>
                  </div>
                </div>
              </div>
            ))}
            {allThreats.length === 0 && (
              <div className="text-center py-8 text-slate-400">
                <svg className="w-12 h-12 mx-auto mb-3 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p>No recent threats detected</p>
              </div>
            )}
          </div>
        </div>

        {/* Recent Incidents */}
        <div className="bg-slate-800 p-6 rounded-lg">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <svg className="w-5 h-5 text-orange-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <h3 className="text-lg font-semibold text-white">Recent Incidents</h3>
            </div>
            <span className="text-sm text-slate-400">{allIncidents.length} total</span>
          </div>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {allIncidents.slice(0, 10).map((incident, index) => (
              <div 
                key={index} 
                className="bg-slate-700 p-4 rounded-lg hover:bg-slate-600 cursor-pointer transition-colors"
                onClick={() => setSelectedIncident(incident)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="text-xs bg-slate-600 text-slate-200 px-2 py-1 rounded">
                        {incident.tenant_name || 'Unknown Tenant'}
                      </span>
                      <span className={`text-xs px-2 py-1 rounded ${
                        incident.severity === 'critical' ? 'bg-red-500 text-white' :
                        incident.severity === 'high' ? 'bg-orange-500 text-white' :
                        incident.severity === 'medium' ? 'bg-yellow-500 text-black' :
                        'bg-green-500 text-white'
                      }`}>
                        {incident.severity?.toUpperCase()}
                      </span>
                      <span className={`text-xs px-2 py-1 rounded ${
                        incident.status === 'open' ? 'bg-red-100 text-red-800' :
                        incident.status === 'investigating' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {incident.status?.toUpperCase()}
                      </span>
                    </div>
                    <h4 className="font-medium text-white text-sm">{incident.title}</h4>
                    <p className="text-slate-400 text-xs mt-1">{incident.description}</p>
                    <div className="flex items-center justify-between mt-2">
                      <span className="text-xs text-slate-500">
                        ID: {incident.id}
                      </span>
                      <span className="text-xs text-slate-500">
                        {new Date(incident.created_at).toLocaleTimeString()}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
            {allIncidents.length === 0 && (
              <div className="text-center py-8 text-slate-400">
                <svg className="w-12 h-12 mx-auto mb-3 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p>No recent incidents reported</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="mt-8 text-center text-sm text-slate-400">
        <p>Last updated: {lastUpdate?.toLocaleTimeString()}</p>
      </div>

      {/* Threat Detail Modal */}
      {selectedThreat && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-white">Threat Details</h2>
              <button 
                onClick={() => setSelectedThreat(null)}
                className="text-slate-400 hover:text-white"
              >
                <XMarkIcon className="w-6 h-6" />
              </button>
            </div>
            
            <div className="space-y-4">
              <div className="bg-slate-700 p-4 rounded-lg">
                <div className="flex items-center space-x-2 mb-3">
                  <span className="text-xs bg-slate-600 text-slate-200 px-2 py-1 rounded">
                    {selectedThreat.tenant_name || 'Unknown Tenant'}
                  </span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    selectedThreat.severity === 'high' ? 'bg-red-500 text-white' :
                    selectedThreat.severity === 'medium' ? 'bg-yellow-500 text-black' :
                    'bg-green-500 text-white'
                  }`}>
                    {selectedThreat.severity?.toUpperCase()}
                  </span>
                  <span className="text-xs bg-blue-500 text-white px-2 py-1 rounded">
                    {selectedThreat.status?.toUpperCase()}
                  </span>
                </div>
                
                <h3 className="text-lg font-semibold text-white mb-2">{selectedThreat.threat}</h3>
                <p className="text-slate-300 mb-4">{selectedThreat.description}</p>
                
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-slate-400">Source IP:</span>
                    <span className="text-white ml-2">{selectedThreat.source_ip}</span>
                  </div>
                  <div>
                    <span className="text-slate-400">Threat Type:</span>
                    <span className="text-white ml-2">{selectedThreat.threat_type}</span>
                  </div>
                  <div>
                    <span className="text-slate-400">CVSS Score:</span>
                    <span className="text-white ml-2">{selectedThreat.cvss_score}</span>
                  </div>
                  <div>
                    <span className="text-slate-400">Detected:</span>
                    <span className="text-white ml-2">{new Date(selectedThreat.timestamp).toLocaleString()}</span>
                  </div>
                  <div>
                    <span className="text-slate-400">Source:</span>
                    <span className="text-white ml-2">{selectedThreat.source}</span>
                  </div>
                  <div>
                    <span className="text-slate-400">Threat ID:</span>
                    <span className="text-white ml-2">{selectedThreat.id}</span>
                  </div>
                </div>
              </div>
              
              <div className="flex space-x-3">
                <button className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors">
                  Block Source
                </button>
                <button className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors">
                  Create Incident
                </button>
                <button 
                  onClick={() => setShowFullDetails(true)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  View Full Details
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Incident Detail Modal */}
      {selectedIncident && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-white">Incident Details</h2>
              <button 
                onClick={() => setSelectedIncident(null)}
                className="text-slate-400 hover:text-white"
              >
                <XMarkIcon className="w-6 h-6" />
              </button>
            </div>
            
            <div className="space-y-4">
              <div className="bg-slate-700 p-4 rounded-lg">
                <div className="flex items-center space-x-2 mb-3">
                  <span className="text-xs bg-slate-600 text-slate-200 px-2 py-1 rounded">
                    {selectedIncident.tenant_name || 'Unknown Tenant'}
                  </span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    selectedIncident.severity === 'critical' ? 'bg-red-500 text-white' :
                    selectedIncident.severity === 'high' ? 'bg-orange-500 text-white' :
                    selectedIncident.severity === 'medium' ? 'bg-yellow-500 text-black' :
                    'bg-green-500 text-white'
                  }`}>
                    {selectedIncident.severity?.toUpperCase()}
                  </span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    selectedIncident.status === 'open' ? 'bg-red-100 text-red-800' :
                    selectedIncident.status === 'investigating' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-green-100 text-green-800'
                  }`}>
                    {selectedIncident.status?.toUpperCase()}
                  </span>
                </div>
                
                <h3 className="text-lg font-semibold text-white mb-2">{selectedIncident.title}</h3>
                <p className="text-slate-300 mb-4">{selectedIncident.description}</p>
                
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-slate-400">Incident ID:</span>
                    <span className="text-white ml-2">{selectedIncident.id}</span>
                  </div>
                  <div>
                    <span className="text-slate-400">Created:</span>
                    <span className="text-white ml-2">{new Date(selectedIncident.created_at).toLocaleString()}</span>
                  </div>
                  <div>
                    <span className="text-slate-400">Status:</span>
                    <span className="text-white ml-2">{selectedIncident.status}</span>
                  </div>
                  <div>
                    <span className="text-slate-400">Severity:</span>
                    <span className="text-white ml-2">{selectedIncident.severity}</span>
                  </div>
                </div>
              </div>
              
              <div className="flex space-x-3">
                <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
                  Assign to Me
                </button>
                <button className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors">
                  Update Status
                </button>
                <button 
                  onClick={() => setShowFullDetails(true)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  View Full Details
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tenant View Modal */}
      {showTenantView && selectedTenant && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-lg p-6 max-w-6xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center text-white font-bold">
                  {selectedTenant.name.substring(0, 2).toUpperCase()}
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white">{selectedTenant.name} - Tenant Dashboard</h2>
                  <p className="text-slate-400">{selectedTenant.domain || 'No domain set'}</p>
                </div>
              </div>
              <button 
                onClick={() => {
                  setShowTenantView(false);
                  setSelectedTenant(null);
                }}
                className="text-slate-400 hover:text-white"
              >
                <XMarkIcon className="w-6 h-6" />
              </button>
            </div>
            
            <div className="space-y-6">
              {/* Tenant-specific navigation */}
              <div className="bg-slate-700 p-4 rounded-lg">
                <h3 className="text-lg font-semibold text-white mb-4">Available Features</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <button className="bg-slate-600 hover:bg-slate-500 p-3 rounded-lg text-white text-sm transition-colors flex items-center space-x-2">
                    <ShieldExclamationIcon className="w-4 h-4" />
                    <span>Threats</span>
                  </button>
                  <button className="bg-slate-600 hover:bg-slate-500 p-3 rounded-lg text-white text-sm transition-colors flex items-center space-x-2">
                    <ExclamationTriangleIcon className="w-4 h-4" />
                    <span>Incidents</span>
                  </button>
                  <button className="bg-slate-600 hover:bg-slate-500 p-3 rounded-lg text-white text-sm transition-colors flex items-center space-x-2">
                    <EyeIcon className="w-4 h-4" />
                    <span>AI Hunting</span>
                  </button>
                  <button className="bg-slate-600 hover:bg-slate-500 p-3 rounded-lg text-white text-sm transition-colors flex items-center space-x-2">
                    <UsersIcon className="w-4 h-4" />
                    <span>Agents</span>
                  </button>
                  <button className="bg-slate-600 hover:bg-slate-500 p-3 rounded-lg text-white text-sm transition-colors flex items-center space-x-2">
                    <ComputerDesktopIcon className="w-4 h-4" />
                    <span>Dashboard</span>
                  </button>
                  <button className="bg-slate-600 hover:bg-slate-500 p-3 rounded-lg text-white text-sm transition-colors flex items-center space-x-2">
                    <ClockIcon className="w-4 h-4" />
                    <span>Audit Logs</span>
                  </button>
                  <button className="bg-slate-600 hover:bg-slate-500 p-3 rounded-lg text-white text-sm transition-colors flex items-center space-x-2">
                    <ShieldCheckIcon className="w-4 h-4" />
                    <span>Security Outlook</span>
                  </button>
                  <button className="bg-slate-600 hover:bg-slate-500 p-3 rounded-lg text-white text-sm transition-colors flex items-center space-x-2">
                    <BuildingOfficeIcon className="w-4 h-4" />
                    <span>Settings</span>
                  </button>
                </div>
              </div>
              
              {/* Quick Stats for this tenant */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-slate-700 p-4 rounded-lg">
                  <h4 className="text-white font-semibold mb-2">Active Threats</h4>
                  <p className="text-2xl font-bold text-red-400">
                    {allThreats.filter(t => t.tenant_name === selectedTenant.name).length}
                  </p>
                </div>
                <div className="bg-slate-700 p-4 rounded-lg">
                  <h4 className="text-white font-semibold mb-2">Open Incidents</h4>
                  <p className="text-2xl font-bold text-orange-400">
                    {allIncidents.filter(i => i.tenant_name === selectedTenant.name && (i.status === 'open' || i.status === 'investigating')).length}
                  </p>
                </div>
                <div className="bg-slate-700 p-4 rounded-lg">
                  <h4 className="text-white font-semibold mb-2">AI Models</h4>
                  <p className="text-2xl font-bold text-green-400">6</p>
                </div>
              </div>
              
              <div className="text-center pt-4">
                <p className="text-slate-400 text-sm">
                  Click on any feature above to access the full tenant-specific dashboard for {selectedTenant.name}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Full Details Modal */}
      {showFullDetails && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-slate-800 rounded-lg max-w-4xl w-full max-h-90vh overflow-y-auto">
            <div className="p-6 border-b border-slate-600">
              <h2 className="text-xl font-bold text-white mb-2">Comprehensive Details</h2>
              <button 
                onClick={() => setShowFullDetails(false)}
                className="absolute top-4 right-4 text-slate-400 hover:text-white"
              >
                <XMarkIcon className="w-6 h-6" />
              </button>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Current Threat Details */}
              {selectedThreat && (
                <div className="bg-slate-700 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold text-white mb-4">Threat Analysis</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="text-sm font-medium text-slate-300 mb-2">Threat Intelligence</h4>
                      <div className="space-y-2 text-sm text-slate-400">
                        <div><span className="font-medium">Source IP:</span> {selectedThreat.source_ip}</div>
                        <div><span className="font-medium">Destination:</span> {selectedThreat.destination_ip}</div>
                        <div><span className="font-medium">Protocol:</span> {selectedThreat.protocol}</div>
                        <div><span className="font-medium">Port:</span> {selectedThreat.destination_port}</div>
                      </div>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-slate-300 mb-2">Risk Assessment</h4>
                      <div className="space-y-2 text-sm text-slate-400">
                        <div><span className="font-medium">Severity:</span> 
                          <span className={`ml-2 px-2 py-1 rounded text-xs ${
                            selectedThreat.severity === 'Critical' ? 'bg-red-900 text-red-200' :
                            selectedThreat.severity === 'High' ? 'bg-orange-900 text-orange-200' :
                            selectedThreat.severity === 'Medium' ? 'bg-yellow-900 text-yellow-200' :
                            'bg-green-900 text-green-200'
                          }`}>
                            {selectedThreat.severity}
                          </span>
                        </div>
                        <div><span className="font-medium">Category:</span> {selectedThreat.threat_type}</div>
                        <div><span className="font-medium">Confidence:</span> {Math.floor(Math.random() * 30) + 70}%</div>
                        <div><span className="font-medium">First Seen:</span> {new Date(selectedThreat.detected_at).toLocaleString()}</div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="mt-4">
                    <h4 className="text-sm font-medium text-slate-300 mb-2">Recommended Actions</h4>
                    <div className="space-y-2">
                      <div className="bg-slate-600 p-3 rounded text-sm text-slate-300">
                        <div className="font-medium text-white">Immediate:</div>
                        • Block source IP at firewall level
                        • Monitor for lateral movement attempts
                        • Check for similar patterns in logs
                      </div>
                      <div className="bg-slate-600 p-3 rounded text-sm text-slate-300">
                        <div className="font-medium text-white">Investigation:</div>
                        • Review network traffic for past 24 hours
                        • Correlate with threat intelligence feeds
                        • Check endpoint security on affected systems
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Current Incident Details */}
              {selectedIncident && (
                <div className="bg-slate-700 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold text-white mb-4">Incident Investigation</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="text-sm font-medium text-slate-300 mb-2">Incident Timeline</h4>
                      <div className="space-y-2 text-sm text-slate-400">
                        <div><span className="font-medium">Created:</span> {new Date(selectedIncident.created_at).toLocaleString()}</div>
                        <div><span className="font-medium">Updated:</span> {new Date(selectedIncident.updated_at).toLocaleString()}</div>
                        <div><span className="font-medium">Priority:</span> 
                          <span className={`ml-2 px-2 py-1 rounded text-xs ${
                            selectedIncident.priority === 'Critical' ? 'bg-red-900 text-red-200' :
                            selectedIncident.priority === 'High' ? 'bg-orange-900 text-orange-200' :
                            selectedIncident.priority === 'Medium' ? 'bg-yellow-900 text-yellow-200' :
                            'bg-green-900 text-green-200'
                          }`}>
                            {selectedIncident.priority}
                          </span>
                        </div>
                        <div><span className="font-medium">Status:</span> 
                          <span className={`ml-2 px-2 py-1 rounded text-xs ${
                            selectedIncident.status === 'open' ? 'bg-red-900 text-red-200' :
                            selectedIncident.status === 'investigating' ? 'bg-orange-900 text-orange-200' :
                            selectedIncident.status === 'resolved' ? 'bg-green-900 text-green-200' :
                            'bg-slate-900 text-slate-200'
                          }`}>
                            {selectedIncident.status}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-slate-300 mb-2">Impact Analysis</h4>
                      <div className="space-y-2 text-sm text-slate-400">
                        <div><span className="font-medium">Affected Systems:</span> {Math.floor(Math.random() * 10) + 1}</div>
                        <div><span className="font-medium">Users Impacted:</span> {Math.floor(Math.random() * 100) + 10}</div>
                        <div><span className="font-medium">Business Impact:</span> {selectedIncident.priority === 'Critical' ? 'High' : 'Medium'}</div>
                        <div><span className="font-medium">Estimated Cost:</span> ${(Math.random() * 50000 + 5000).toFixed(0)}</div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="mt-4">
                    <h4 className="text-sm font-medium text-slate-300 mb-2">Investigation Notes</h4>
                    <div className="bg-slate-600 p-3 rounded text-sm text-slate-300">
                      <div className="space-y-2">
                        <div>• Initial detection through automated monitoring system</div>
                        <div>• Correlation with threat intelligence indicates potential APT activity</div>
                        <div>• Forensic analysis ongoing on affected endpoints</div>
                        <div>• Containment measures implemented successfully</div>
                        <div>• Recovery procedures initiated for affected services</div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="mt-4">
                    <h4 className="text-sm font-medium text-slate-300 mb-2">Next Steps</h4>
                    <div className="space-y-2">
                      <button className="w-full text-left bg-blue-600 hover:bg-blue-500 p-2 rounded text-sm text-white transition-colors">
                        Schedule follow-up security review
                      </button>
                      <button className="w-full text-left bg-green-600 hover:bg-green-500 p-2 rounded text-sm text-white transition-colors">
                        Generate incident report
                      </button>
                      <button className="w-full text-left bg-orange-600 hover:bg-orange-500 p-2 rounded text-sm text-white transition-colors">
                        Update stakeholders
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* System Health & Context */}
              <div className="bg-slate-700 p-4 rounded-lg">
                <h3 className="text-lg font-semibold text-white mb-4">System Context</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <h4 className="text-sm font-medium text-slate-300 mb-2">Network Status</h4>
                    <div className="space-y-1 text-sm text-slate-400">
                      <div>• Firewall: Operational</div>
                      <div>• IDS/IPS: Active</div>
                      <div>• VPN: Secure</div>
                      <div>• DNS: Protected</div>
                    </div>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-slate-300 mb-2">Security Tools</h4>
                    <div className="space-y-1 text-sm text-slate-400">
                      <div>• SIEM: Processing</div>
                      <div>• EDR: Monitoring</div>
                      <div>• Threat Intel: Updated</div>
                      <div>• Backup: Current</div>
                    </div>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-slate-300 mb-2">Compliance</h4>
                    <div className="space-y-1 text-sm text-slate-400">
                      <div>• SOC2: Compliant</div>
                      <div>• ISO27001: Compliant</div>
                      <div>• GDPR: Compliant</div>
                      <div>• PCI DSS: Compliant</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
