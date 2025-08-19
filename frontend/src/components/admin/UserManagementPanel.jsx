/*
 * Copyright (c) 2025 Kevin Zachary
 * All rights reserved.
 */

import React, { useState, useEffect } from 'react';
import { 
  UserGroupIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  CheckIcon,
  XMarkIcon,
  ShieldCheckIcon,
  UserIcon
} from '@heroicons/react/24/outline';
import { getApiBaseUrl } from '../../utils/environment';

const UserManagementPanel = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [newUser, setNewUser] = useState({
    user_id: '',
    email: '',
    name: '',
    role: 'viewer',
    auth_provider: 'local'
  });

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const baseUrl = getApiBaseUrl();
      const response = await fetch(`${baseUrl}/api/admin/users`);
      const data = await response.json();
      setUsers(data.users || []);
    } catch (error) {
      console.error('Error fetching users:', error);
    } finally {
      setLoading(false);
    }
  };

  const createUser = async () => {
    try {
      const baseUrl = getApiBaseUrl();
      const response = await fetch(`${baseUrl}/api/admin/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newUser)
      });
      
      if (response.ok) {
        await fetchUsers();
        setShowCreateForm(false);
        setNewUser({
          user_id: '',
          email: '',
          name: '',
          role: 'viewer',
          auth_provider: 'local'
        });
      }
    } catch (error) {
      console.error('Error creating user:', error);
    }
  };

  const updateUser = async (userId, updates) => {
    try {
      const baseUrl = getApiBaseUrl();
      const response = await fetch(`${baseUrl}/api/admin/users/${userId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      });
      
      if (response.ok) {
        await fetchUsers();
        setEditingUser(null);
      }
    } catch (error) {
      console.error('Error updating user:', error);
    }
  };

  const getRoleBadgeColor = (role) => {
    switch (role) {
      case 'admin':
        return 'bg-red-100 text-red-800';
      case 'analyst':
        return 'bg-blue-100 text-blue-800';
      case 'viewer':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getProviderIcon = (provider) => {
    switch (provider) {
      case 'microsoft':
        return <div className="w-4 h-4 bg-blue-500 rounded"></div>;
      case 'google':
        return <div className="w-4 h-4 bg-red-500 rounded"></div>;
      case 'local':
        return <UserIcon className="w-4 h-4 text-gray-500" />;
      default:
        return <ShieldCheckIcon className="w-4 h-4 text-gray-500" />;
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
          <UserGroupIcon className="h-5 w-5 mr-2" />
          User Management
        </h3>
        
        <button
          onClick={() => setShowCreateForm(true)}
          className="flex items-center px-4 py-2 bg-sky-600 text-white rounded-lg hover:bg-sky-700 transition-colors"
        >
          <PlusIcon className="h-4 w-4 mr-2" />
          Add User
        </button>
      </div>

      {/* Create User Form */}
      {showCreateForm && (
        <div className="mb-6 bg-slate-700 rounded-lg p-4 border border-slate-600">
          <h4 className="text-md font-medium text-white mb-4">Create New User</h4>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">User ID</label>
              <input
                type="text"
                value={newUser.user_id}
                onChange={(e) => setNewUser({...newUser, user_id: e.target.value})}
                className="w-full px-3 py-2 bg-slate-600 border border-slate-500 rounded-md text-white"
                placeholder="unique_user_id"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Email</label>
              <input
                type="email"
                value={newUser.email}
                onChange={(e) => setNewUser({...newUser, email: e.target.value})}
                className="w-full px-3 py-2 bg-slate-600 border border-slate-500 rounded-md text-white"
                placeholder="user@company.com"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Name</label>
              <input
                type="text"
                value={newUser.name}
                onChange={(e) => setNewUser({...newUser, name: e.target.value})}
                className="w-full px-3 py-2 bg-slate-600 border border-slate-500 rounded-md text-white"
                placeholder="Full Name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Role</label>
              <select
                value={newUser.role}
                onChange={(e) => setNewUser({...newUser, role: e.target.value})}
                className="w-full px-3 py-2 bg-slate-600 border border-slate-500 rounded-md text-white"
              >
                <option value="viewer">Viewer</option>
                <option value="analyst">Analyst</option>
                <option value="admin">Admin</option>
              </select>
            </div>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={createUser}
              className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              <CheckIcon className="h-4 w-4 mr-2" />
              Create
            </button>
            <button
              onClick={() => setShowCreateForm(false)}
              className="flex items-center px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
            >
              <XMarkIcon className="h-4 w-4 mr-2" />
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Users Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-600">
              <th className="text-left text-slate-300 font-medium py-3 px-4">User</th>
              <th className="text-left text-slate-300 font-medium py-3 px-4">Email</th>
              <th className="text-left text-slate-300 font-medium py-3 px-4">Role</th>
              <th className="text-left text-slate-300 font-medium py-3 px-4">Provider</th>
              <th className="text-left text-slate-300 font-medium py-3 px-4">Status</th>
              <th className="text-left text-slate-300 font-medium py-3 px-4">Last Login</th>
              <th className="text-left text-slate-300 font-medium py-3 px-4">Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id} className="border-b border-slate-700 hover:bg-slate-700">
                <td className="py-3 px-4">
                  <div>
                    <p className="text-white font-medium">{user.name}</p>
                    <p className="text-slate-400 text-xs">{user.user_id}</p>
                  </div>
                </td>
                <td className="py-3 px-4 text-slate-300">{user.email}</td>
                <td className="py-3 px-4">
                  {editingUser === user.id ? (
                    <select
                      defaultValue={user.role}
                      onChange={(e) => updateUser(user.user_id, { role: e.target.value })}
                      className="px-2 py-1 bg-slate-600 border border-slate-500 rounded text-white text-xs"
                    >
                      <option value="viewer">Viewer</option>
                      <option value="analyst">Analyst</option>
                      <option value="admin">Admin</option>
                    </select>
                  ) : (
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRoleBadgeColor(user.role)}`}>
                      {user.role}
                    </span>
                  )}
                </td>
                <td className="py-3 px-4">
                  <div className="flex items-center space-x-2">
                    {getProviderIcon(user.auth_provider)}
                    <span className="text-slate-300 text-xs">{user.auth_provider}</span>
                  </div>
                </td>
                <td className="py-3 px-4">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {user.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td className="py-3 px-4 text-slate-300 text-xs">
                  {user.last_login 
                    ? new Date(user.last_login).toLocaleDateString()
                    : 'Never'
                  }
                </td>
                <td className="py-3 px-4">
                  <div className="flex space-x-2">
                    <button
                      onClick={() => setEditingUser(editingUser === user.id ? null : user.id)}
                      className="p-1 text-blue-400 hover:text-blue-300"
                    >
                      <PencilIcon className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => updateUser(user.user_id, { is_active: !user.is_active })}
                      className={`p-1 ${user.is_active ? 'text-red-400 hover:text-red-300' : 'text-green-400 hover:text-green-300'}`}
                    >
                      {user.is_active ? <XMarkIcon className="h-4 w-4" /> : <CheckIcon className="h-4 w-4" />}
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        {users.length === 0 && (
          <div className="text-center py-8">
            <UserGroupIcon className="h-12 w-12 text-slate-500 mx-auto mb-4" />
            <p className="text-slate-400">No users found</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default UserManagementPanel;
