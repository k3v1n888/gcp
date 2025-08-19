/*
 * Copyright (c) 2025 Kevin Zachary
 * All rights reserved.
 */

import React, { useState, useEffect } from 'react';
import { 
  ClockIcon, 
  UserIcon, 
  CogIcon,
  ShieldCheckIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';
import { getApiBaseUrl } from '../../utils/environment';

const AuditLogsPanel = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [limit, setLimit] = useState(50);

  useEffect(() => {
    fetchAuditLogs();
  }, [limit]);

  const fetchAuditLogs = async () => {
    try {
      const baseUrl = getApiBaseUrl();
      const response = await fetch(`${baseUrl}/api/admin/audit-logs?limit=${limit}`);
      const data = await response.json();
      setLogs(data.logs || []);
    } catch (error) {
      console.error('Error fetching audit logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const getActionIcon = (action) => {
    switch (action) {
      case 'login':
      case 'logout':
        return <UserIcon className="h-5 w-5 text-blue-400" />;
      case 'user_created':
      case 'user_updated':
        return <UserIcon className="h-5 w-5 text-green-400" />;
      case 'agent_heartbeat':
        return <InformationCircleIcon className="h-5 w-5 text-gray-400" />;
      case 'data_ingestion':
        return <ShieldCheckIcon className="h-5 w-5 text-purple-400" />;
      default:
        return <CogIcon className="h-5 w-5 text-yellow-400" />;
    }
  };

  const getActionBadgeColor = (action) => {
    switch (action) {
      case 'login':
        return 'bg-blue-100 text-blue-800';
      case 'user_created':
        return 'bg-green-100 text-green-800';
      case 'user_updated':
        return 'bg-yellow-100 text-yellow-800';
      case 'agent_heartbeat':
        return 'bg-gray-100 text-gray-800';
      case 'data_ingestion':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-orange-100 text-orange-800';
    }
  };

  const filteredLogs = logs.filter(log => {
    if (filter === 'all') return true;
    return log.action === filter;
  });

  const uniqueActions = [...new Set(logs.map(log => log.action))];

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
          <ClockIcon className="h-5 w-5 mr-2" />
          Audit Logs
        </h3>
        
        <div className="flex space-x-4">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-white text-sm"
          >
            <option value="all">All Actions</option>
            {uniqueActions.map(action => (
              <option key={action} value={action}>
                {action.replace('_', ' ').toUpperCase()}
              </option>
            ))}
          </select>
          
          <select
            value={limit}
            onChange={(e) => setLimit(parseInt(e.target.value))}
            className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-white text-sm"
          >
            <option value={25}>25 entries</option>
            <option value={50}>50 entries</option>
            <option value={100}>100 entries</option>
            <option value={200}>200 entries</option>
          </select>
        </div>
      </div>

      <div className="space-y-3 max-h-96 overflow-y-auto">
        {filteredLogs.map((log) => (
          <div key={log.id} className="bg-slate-700 rounded-lg p-4 border border-slate-600">
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-3">
                {getActionIcon(log.action)}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-1">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getActionBadgeColor(log.action)}`}>
                      {log.action.replace('_', ' ')}
                    </span>
                    <span className="text-xs text-slate-400">
                      {log.resource_type}
                    </span>
                  </div>
                  
                  <p className="text-sm text-white font-medium">
                    User: {log.user_id || 'system'}
                  </p>
                  
                  <p className="text-sm text-slate-300">
                    Resource: {log.resource_id}
                  </p>
                  
                  {log.details && Object.keys(log.details).length > 0 && (
                    <div className="mt-2">
                      <details className="text-xs">
                        <summary className="text-slate-400 cursor-pointer hover:text-slate-300">
                          Show details
                        </summary>
                        <pre className="mt-1 text-slate-400 overflow-x-auto">
                          {JSON.stringify(log.details, null, 2)}
                        </pre>
                      </details>
                    </div>
                  )}
                </div>
              </div>
              
              <div className="text-right">
                <p className="text-xs text-slate-400">
                  {new Date(log.timestamp).toLocaleString()}
                </p>
                {log.ip_address && (
                  <p className="text-xs text-slate-500">
                    IP: {log.ip_address}
                  </p>
                )}
              </div>
            </div>
          </div>
        ))}
        
        {filteredLogs.length === 0 && (
          <div className="text-center py-8">
            <ExclamationTriangleIcon className="h-12 w-12 text-slate-500 mx-auto mb-4" />
            <p className="text-slate-400">No audit logs found</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AuditLogsPanel;
