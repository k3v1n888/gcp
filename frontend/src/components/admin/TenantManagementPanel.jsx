/*
 * Copyright (c) 2025 Kevin Zachary
 * All rights reserved.
 */

import React, { useState, useEffect } from 'react';
import { 
  BuildingOfficeIcon,
  PlusIcon,
  ServerIcon,
  UsersIcon,
  ChartBarIcon,
  CogIcon
} from '@heroicons/react/24/outline';
import { getApiBaseUrl } from '../../utils/environment';

const TenantManagementPanel = () => {
  const [tenants, setTenants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newTenant, setNewTenant] = useState({
    tenant_id: '',
    name: '',
    settings: {}
  });

  useEffect(() => {
    fetchTenants();
  }, []);

  const fetchTenants = async () => {
    try {
      const baseUrl = getApiBaseUrl();
      const response = await fetch(`${baseUrl}/api/admin/tenants`);
      const data = await response.json();
      setTenants(data.tenants || []);
    } catch (error) {
      console.error('Error fetching tenants:', error);
    } finally {
      setLoading(false);
    }
  };

  const createTenant = async () => {
    try {
      const baseUrl = getApiBaseUrl();
      const response = await fetch(`${baseUrl}/api/admin/tenants`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newTenant)
      });
      
      if (response.ok) {
        await fetchTenants();
        setShowCreateForm(false);
        setNewTenant({
          tenant_id: '',
          name: '',
          settings: {}
        });
      }
    } catch (error) {
      console.error('Error creating tenant:', error);
    }
  };

  const getStatusBadgeColor = (status) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'suspended':
        return 'bg-yellow-100 text-yellow-800';
      case 'deleted':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

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
          <BuildingOfficeIcon className="h-5 w-5 mr-2" />
          Tenant Management
        </h3>
        
        <button
          onClick={() => setShowCreateForm(true)}
          className="flex items-center px-4 py-2 bg-sky-600 text-white rounded-lg hover:bg-sky-700 transition-colors"
        >
          <PlusIcon className="h-4 w-4 mr-2" />
          Add Tenant
        </button>
      </div>

      {/* Create Tenant Form */}
      {showCreateForm && (
        <div className="mb-6 bg-slate-700 rounded-lg p-4 border border-slate-600">
          <h4 className="text-md font-medium text-white mb-4">Create New Tenant</h4>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Tenant ID</label>
              <input
                type="text"
                value={newTenant.tenant_id}
                onChange={(e) => setNewTenant({...newTenant, tenant_id: e.target.value})}
                className="w-full px-3 py-2 bg-slate-600 border border-slate-500 rounded-md text-white"
                placeholder="tenant-company-name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Tenant Name</label>
              <input
                type="text"
                value={newTenant.name}
                onChange={(e) => setNewTenant({...newTenant, name: e.target.value})}
                className="w-full px-3 py-2 bg-slate-600 border border-slate-500 rounded-md text-white"
                placeholder="Company Name Inc."
              />
            </div>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={createTenant}
              className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              <PlusIcon className="h-4 w-4 mr-2" />
              Create Tenant
            </button>
            <button
              onClick={() => setShowCreateForm(false)}
              className="flex items-center px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Tenants Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {tenants.map((tenant) => (
          <div key={tenant.id} className="bg-slate-700 rounded-lg p-4 border border-slate-600">
            <div className="flex items-start justify-between mb-3">
              <div>
                <h4 className="text-white font-medium">{tenant.name}</h4>
                <p className="text-slate-400 text-sm">{tenant.tenant_id}</p>
              </div>
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusBadgeColor(tenant.status)}`}>
                {tenant.status}
              </span>
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center text-slate-300 text-sm">
                <ServerIcon className="h-4 w-4 mr-2 text-slate-400" />
                <span>Database: Shared</span>
              </div>
              
              <div className="flex items-center text-slate-300 text-sm">
                <UsersIcon className="h-4 w-4 mr-2 text-slate-400" />
                <span>Users: 0</span>
              </div>
              
              <div className="flex items-center text-slate-300 text-sm">
                <ChartBarIcon className="h-4 w-4 mr-2 text-slate-400" />
                <span>Storage: 0 GB</span>
              </div>
              
              <div className="text-xs text-slate-400">
                Created: {new Date(tenant.created_at).toLocaleDateString()}
              </div>
            </div>
            
            <div className="mt-4 flex space-x-2">
              <button className="flex-1 flex items-center justify-center px-3 py-2 bg-blue-600 text-white text-xs rounded hover:bg-blue-700">
                <CogIcon className="h-3 w-3 mr-1" />
                Configure
              </button>
              <button className="flex-1 flex items-center justify-center px-3 py-2 bg-gray-600 text-white text-xs rounded hover:bg-gray-700">
                <ChartBarIcon className="h-3 w-3 mr-1" />
                Analytics
              </button>
            </div>
          </div>
        ))}
        
        {tenants.length === 0 && (
          <div className="col-span-full text-center py-8">
            <BuildingOfficeIcon className="h-12 w-12 text-slate-500 mx-auto mb-4" />
            <p className="text-slate-400">No tenants configured</p>
            <p className="text-slate-500 text-sm">Create your first tenant to enable multi-tenancy</p>
          </div>
        )}
      </div>
      
      {/* Tenant Information */}
      <div className="mt-6 bg-slate-700 rounded-lg p-4 border border-slate-600">
        <h4 className="text-white font-medium mb-3">Multi-Tenant Architecture</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div>
            <h5 className="text-sky-400 font-medium mb-2">Data Isolation</h5>
            <p className="text-slate-300">Each tenant has isolated data access and cannot see other tenant's information.</p>
          </div>
          <div>
            <h5 className="text-sky-400 font-medium mb-2">Resource Sharing</h5>
            <p className="text-slate-300">Compute resources are shared efficiently while maintaining security boundaries.</p>
          </div>
          <div>
            <h5 className="text-sky-400 font-medium mb-2">Independent Configuration</h5>
            <p className="text-slate-300">Each tenant can have custom settings, branding, and feature configurations.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TenantManagementPanel;
