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

import { useContext, useEffect, useState } from 'react';
import { 
  UserGroupIcon, 
  CogIcon, 
  HeartIcon,
  CircleStackIcon,
  CpuChipIcon,
  ClockIcon,
  DocumentTextIcon,
  ShieldCheckIcon,
  BuildingOfficeIcon,
  ServerIcon
} from '@heroicons/react/24/outline';
import { UserContext } from '../context/UserContext';
import { useDevUser } from '../context/DevUserContext';
import { isDevelopment, getApiBaseUrl } from '../utils/environment';
import HealthDashboard from './HealthDashboard';
import SentientAIModelsDashboard from '../components/admin/AIModelTestingDashboard';
import AuditLogsPanel from '../components/admin/AuditLogsPanel';
import SystemLogsPanel from '../components/admin/SystemLogsPanel';
import UserManagementPanel from '../components/admin/UserManagementPanel';
import TenantManagementPanel from '../components/admin/TenantManagementPanel';
import AuthenticationPanel from '../components/admin/AuthenticationPanel';

const InviteUserForm = () => {
    const [email, setEmail] = useState('');
    const [role, setRole] = useState('viewer');
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage('');
        setError('');

        const response = await fetch(`${getApiBaseUrl()}/api/admin/invite`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, role }),
        });

        if (response.ok) {
            setMessage('Invitation sent successfully!');
            setEmail('');
            setRole('viewer');
        } else {
            const errorData = await response.json();
            setError(errorData.detail || 'Failed to send invitation');
        }
    };

    return (
        <div className="mt-8">
            <h3 className="text-lg font-semibold mb-4 text-sky-400">Invite New User</h3>
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block text-sm font-medium text-slate-300">Email</label>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                        className="mt-1 block w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-md focus:outline-none focus:ring-sky-500 focus:border-sky-500 sm:text-sm"
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium text-slate-300">Role</label>
                    <select
                        value={role}
                        onChange={(e) => setRole(e.target.value)}
                        className="mt-1 block w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-md focus:outline-none focus:ring-sky-500 focus:border-sky-500 sm:text-sm"
                    >
                        <option value="viewer">Viewer</option>
                        <option value="analyst">Analyst</option>
                        <option value="admin">Admin</option>
                    </select>
                </div>
                <button
                    type="submit"
                    className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-sky-600 hover:bg-sky-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-sky-500"
                >
                    Send Invitation
                </button>
            </form>
            {message && <p className="mt-2 text-green-400">{message}</p>}
            {error && <p className="mt-2 text-red-400">{error}</p>}
        </div>
    );
};

export default function AdminPanel() {
  // Use appropriate context/hook based on environment
  let user = null;
  
  const [activeTab, setActiveTab] = useState('health');
  const [severity, setSeverity] = useState('critical');
  const [message, setMessage] = useState('');
  
  try {
      if (isDevelopment()) {
          const devContext = useDevUser();
          user = devContext.user;
      } else {
          const prodContext = useContext(UserContext);
          user = prodContext.user;
      }
  } catch (error) {
      console.error('Error getting user context:', error);
  }

  const handleSubmit = async () => {
    const res = await fetch(`${getApiBaseUrl()}/api/admin/settings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ alert_severity: severity }),
    });
    if (res.ok) setMessage('Settings updated successfully');
    else setMessage('Failed to update settings');
  };

  if (user?.role !== 'admin') {
    return <p className="text-red-500 p-6">Unauthorized access. Only admins can access this panel.</p>;
  }

  const tabs = [
    {
      id: 'health',
      name: 'System Health',
      icon: HeartIcon,
      description: 'Monitor system health and status'
    },
    {
      id: 'ai-models',
      name: 'AI Models',
      icon: CpuChipIcon,
      description: 'Sentient AI SOC Multi-Model Management'
    },
    {
      id: 'users',
      name: 'User Management',
      icon: UserGroupIcon,
      description: 'Manage users, roles, and authentication'
    },
    {
      id: 'tenants',
      name: 'Tenant Management',
      icon: BuildingOfficeIcon,
      description: 'Multi-tenant environment management'
    },
    {
      id: 'audit-logs',
      name: 'Audit Logs',
      icon: ClockIcon,
      description: 'View audit trail and user activities'
    },
    {
      id: 'system-logs',
      name: 'System Logs',
      icon: DocumentTextIcon,
      description: 'Monitor system logs and events'
    },
    {
      id: 'authentication',
      name: 'Authentication',
      icon: ShieldCheckIcon,
      description: 'Configure SSO and security settings'
    },
    {
      id: 'agents',
      name: 'SOC Agents',
      icon: ServerIcon,
      description: 'Manage distributed SOC agents'
    },
    {
      id: 'connectors',
      name: 'Data Connectors',
      icon: CircleStackIcon,
      description: 'Manage data connectors and sources'
    },
    {
      id: 'settings',
      name: 'System Settings',
      icon: CogIcon,
      description: 'Configure system settings'
    }
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'health':
        return <HealthDashboard />;
        
      case 'ai-models':
        return <SentientAIModelsDashboard />;
        
      case 'users':
        return (
          <div className="p-6">
            <h2 className="text-2xl font-bold mb-6 text-slate-100">User Management & Authentication</h2>
            <UserManagementPanel />
          </div>
        );
        
      case 'tenants':
        return (
          <div className="p-6">
            <h2 className="text-2xl font-bold mb-6 text-slate-100">Tenant Management</h2>
            <TenantManagementPanel />
          </div>
        );
        
      case 'audit-logs':
        return (
          <div className="p-6">
            <h2 className="text-2xl font-bold mb-6 text-slate-100">Audit Logs & Trail</h2>
            <AuditLogsPanel />
          </div>
        );
        
      case 'system-logs':
        return (
          <div className="p-6">
            <h2 className="text-2xl font-bold mb-6 text-slate-100">System Logs & Monitoring</h2>
            <SystemLogsPanel />
          </div>
        );
        
      case 'authentication':
        return (
          <div className="p-6">
            <h2 className="text-2xl font-bold mb-6 text-slate-100">Authentication & Security</h2>
            <AuthenticationPanel />
          </div>
        );
        
      case 'agents':
        return (
          <div className="p-6">
            <h2 className="text-2xl font-bold mb-6 text-slate-100">SOC Agent Management</h2>
            <div className="bg-slate-800 rounded-lg p-6">
              <div className="text-center py-8">
                <ServerIcon className="h-16 w-16 text-slate-500 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-slate-300 mb-2">SOC Agent Dashboard</h3>
                <p className="text-slate-400 mb-4">Monitor and manage distributed SOC agents across your infrastructure</p>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
                  <div className="bg-slate-700 rounded-lg p-4 border border-slate-600">
                    <h4 className="text-white font-medium mb-2">Agent Status</h4>
                    <p className="text-2xl font-bold text-green-400">0 Active</p>
                    <p className="text-slate-400 text-sm">Agents currently online</p>
                  </div>
                  
                  <div className="bg-slate-700 rounded-lg p-4 border border-slate-600">
                    <h4 className="text-white font-medium mb-2">Data Collection</h4>
                    <p className="text-2xl font-bold text-blue-400">0 GB</p>
                    <p className="text-slate-400 text-sm">Data collected today</p>
                  </div>
                  
                  <div className="bg-slate-700 rounded-lg p-4 border border-slate-600">
                    <h4 className="text-white font-medium mb-2">Coverage</h4>
                    <p className="text-2xl font-bold text-purple-400">0%</p>
                    <p className="text-slate-400 text-sm">Infrastructure coverage</p>
                  </div>
                </div>
                
                <div className="mt-6 p-4 bg-blue-900/20 border border-blue-800 rounded-lg">
                  <h4 className="text-blue-400 font-medium mb-2">Deploy SOC Agent</h4>
                  <p className="text-slate-300 text-sm mb-3">
                    Use our universal installer to deploy SOC agents on any environment:
                  </p>
                  <code className="bg-slate-900 text-green-400 px-3 py-2 rounded text-sm block">
                    curl -sSL https://your-soc-server.com/install | bash
                  </code>
                  <p className="text-slate-400 text-xs mt-2">
                    Agent installer supports Linux, macOS, and Windows environments
                  </p>
                </div>
              </div>
            </div>
          </div>
        );
        
      case 'connectors':
        return (
          <div className="p-6">
            <h2 className="text-2xl font-bold mb-4 text-slate-100">Data Connectors</h2>
            <div className="bg-slate-800 rounded-lg p-4">
              <p className="text-slate-300">Connector management interface coming soon...</p>
              <p className="text-sm text-slate-400 mt-2">
                Current connectors are managed via the main dashboard.
              </p>
            </div>
          </div>
        );
        
      case 'settings':
        return (
          <div className="p-6">
            <h2 className="text-2xl font-bold mb-4 text-slate-100">System Settings</h2>
            <div className="widget-card p-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300">Alert Severity Threshold</label>
                  <select 
                    value={severity} 
                    onChange={(e) => setSeverity(e.target.value)} 
                    className="mt-1 block w-full pl-3 pr-10 py-2 bg-slate-800 border border-slate-600 rounded-md focus:outline-none focus:ring-sky-500 focus:border-sky-500 sm:text-sm"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>
                <button
                  onClick={handleSubmit}
                  className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-sky-600 hover:bg-sky-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-sky-500"
                >
                  Save Settings
                </button>
                {message && <p className="mt-2 text-green-400">{message}</p>}
              </div>
              
              <div className="mt-8">
                <InviteUserForm />
              </div>
            </div>
          </div>
        );
        
      default:
        return <div>Select a tab</div>;
    }
  };

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Tab Navigation */}
      <div className="border-b border-slate-700">
        <nav className="px-6 py-4">
          <div className="flex flex-wrap gap-2">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-2 px-3 rounded-md transition-colors text-sm ${
                    activeTab === tab.id
                      ? 'bg-sky-600 text-white'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800'
                  }`}
                  title={tab.description}
                >
                  <Icon className="h-4 w-4" />
                  <span className="font-medium">{tab.name}</span>
                </button>
              );
            })}
          </div>
        </nav>
      </div>

      {/* Tab Content */}
      <div className="flex-1">
        {renderTabContent()}
      </div>
    </div>
  );
}
