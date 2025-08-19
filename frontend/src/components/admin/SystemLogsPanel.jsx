/*
 * Copyright (c) 2025 Kevin Zachary
 * All rights reserved.
 */

import React, { useState, useEffect } from 'react';
import { 
  DocumentTextIcon,
  ServerIcon,
  BugAntIcon,
  ShieldCheckIcon,
  CpuChipIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline';
import { getApiBaseUrl } from '../../utils/environment';

const SystemLogsPanel = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchSystemLogs();
    const interval = setInterval(fetchSystemLogs, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchSystemLogs = async () => {
    try {
      const baseUrl = getApiBaseUrl();
      const response = await fetch(`${baseUrl}/api/admin/system-logs`);
      const data = await response.json();
      setLogs(data.logs || []);
    } catch (error) {
      console.error('Error fetching system logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const getLogIcon = (source) => {
    switch (source) {
      case 'ai_orchestration':
        return <CpuChipIcon className="h-5 w-5 text-purple-400" />;
      case 'threat_hunting':
        return <ShieldCheckIcon className="h-5 w-5 text-red-400" />;
      case 'system':
        return <ServerIcon className="h-5 w-5 text-blue-400" />;
      case 'error':
        return <BugAntIcon className="h-5 w-5 text-red-500" />;
      default:
        return <DocumentTextIcon className="h-5 w-5 text-gray-400" />;
    }
  };

  const getLogLevelColor = (level) => {
    switch (level) {
      case 'ERROR':
        return 'bg-red-100 text-red-800';
      case 'WARN':
      case 'WARNING':
        return 'bg-yellow-100 text-yellow-800';
      case 'INFO':
        return 'bg-blue-100 text-blue-800';
      case 'DEBUG':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-green-100 text-green-800';
    }
  };

  const filteredLogs = logs.filter(log => {
    const matchesFilter = filter === 'all' || log.source === filter;
    const matchesSearch = searchTerm === '' || 
                         log.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         log.source.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const uniqueSources = [...new Set(logs.map(log => log.source))];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sky-500"></div>
      </div>
    );
  }

  return (
    <div className="bg-slate-800 rounded-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-sky-400 flex items-center">
          <DocumentTextIcon className="h-5 w-5 mr-2" />
          System Logs
        </h3>
        
        <div className="flex space-x-4">
          <div className="relative">
            <MagnifyingGlassIcon className="h-5 w-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search logs..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 bg-slate-700 border border-slate-600 rounded-md text-white text-sm w-64"
            />
          </div>
          
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-white text-sm"
          >
            <option value="all">All Sources</option>
            {uniqueSources.map(source => (
              <option key={source} value={source}>
                {source.replace('_', ' ').toUpperCase()}
              </option>
            ))}
          </select>
          
          <button
            onClick={fetchSystemLogs}
            className="px-4 py-2 bg-sky-600 text-white rounded-md hover:bg-sky-700 text-sm"
          >
            Refresh
          </button>
        </div>
      </div>

      {/* System Status Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-slate-700 rounded-lg p-4 border border-slate-600">
          <div className="flex items-center">
            <CpuChipIcon className="h-8 w-8 text-purple-400 mr-3" />
            <div>
              <p className="text-slate-300 text-sm">AI Orchestration</p>
              <p className="text-white font-semibold">Active</p>
            </div>
          </div>
        </div>
        
        <div className="bg-slate-700 rounded-lg p-4 border border-slate-600">
          <div className="flex items-center">
            <ShieldCheckIcon className="h-8 w-8 text-red-400 mr-3" />
            <div>
              <p className="text-slate-300 text-sm">Threat Hunting</p>
              <p className="text-white font-semibold">Running</p>
            </div>
          </div>
        </div>
        
        <div className="bg-slate-700 rounded-lg p-4 border border-slate-600">
          <div className="flex items-center">
            <ServerIcon className="h-8 w-8 text-blue-400 mr-3" />
            <div>
              <p className="text-slate-300 text-sm">Database</p>
              <p className="text-white font-semibold">Healthy</p>
            </div>
          </div>
        </div>
        
        <div className="bg-slate-700 rounded-lg p-4 border border-slate-600">
          <div className="flex items-center">
            <DocumentTextIcon className="h-8 w-8 text-green-400 mr-3" />
            <div>
              <p className="text-slate-300 text-sm">Log Entries</p>
              <p className="text-white font-semibold">{logs.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Logs Display */}
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {filteredLogs.map((log, index) => (
          <div key={index} className="bg-slate-700 rounded-lg p-4 border border-slate-600">
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-3">
                {getLogIcon(log.source)}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-1">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getLogLevelColor(log.level)}`}>
                      {log.level}
                    </span>
                    <span className="text-xs text-slate-400">
                      {log.source.replace('_', ' ')}
                    </span>
                  </div>
                  
                  <p className="text-sm text-white">
                    {log.message}
                  </p>
                  
                  {log.details && Object.keys(log.details).length > 0 && (
                    <div className="mt-2">
                      <details className="text-xs">
                        <summary className="text-slate-400 cursor-pointer hover:text-slate-300">
                          Show details
                        </summary>
                        <div className="mt-1 grid grid-cols-2 md:grid-cols-4 gap-2">
                          {Object.entries(log.details).map(([key, value]) => (
                            <div key={key} className="bg-slate-800 rounded p-2">
                              <p className="text-slate-400 text-xs">{key}</p>
                              <p className="text-white text-xs font-medium">{value}</p>
                            </div>
                          ))}
                        </div>
                      </details>
                    </div>
                  )}
                </div>
              </div>
              
              <div className="text-right">
                <p className="text-xs text-slate-400">
                  {new Date(log.timestamp).toLocaleString()}
                </p>
              </div>
            </div>
          </div>
        ))}
        
        {filteredLogs.length === 0 && (
          <div className="text-center py-8">
            <DocumentTextIcon className="h-12 w-12 text-slate-500 mx-auto mb-4" />
            <p className="text-slate-400">No system logs found</p>
            {searchTerm && <p className="text-slate-500 text-sm">Try adjusting your search criteria</p>}
          </div>
        )}
      </div>
    </div>
  );
};

export default SystemLogsPanel;
