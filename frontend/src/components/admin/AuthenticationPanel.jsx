/*
 * Copyright (c) 2025 Kevin Zachary
 * All rights reserved.
 */

import React, { useState } from 'react';
import { 
  ShieldCheckIcon,
  UserIcon,
  KeyIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

const AuthenticationPanel = () => {
  const [authSettings, setAuthSettings] = useState({
    local_auth_enabled: true,
    google_sso_enabled: false,
    microsoft_sso_enabled: false,
    require_mfa: false,
    session_timeout: 8 // hours
  });
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleMicrosoftSSO = async () => {
    try {
      // In a real implementation, this would initiate Microsoft OAuth flow
      setMessage('Microsoft SSO configuration would be initiated here');
      
      // Mock Microsoft authentication
      const mockUserInfo = {
        email: 'user@company.com',
        name: 'John Doe',
        id: 'ms_12345'
      };
      
      const response = await fetch('/api/auth/microsoft', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token: 'mock_microsoft_token',
          user_info: mockUserInfo
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setMessage(`Microsoft SSO test successful for ${data.user.email}`);
      } else {
        setError('Microsoft SSO test failed');
      }
    } catch (err) {
      setError('Error testing Microsoft SSO: ' + err.message);
    }
  };

  const handleGoogleSSO = async () => {
    try {
      setMessage('Google SSO is already implemented. Configure OAuth credentials in environment variables.');
    } catch (err) {
      setError('Error with Google SSO: ' + err.message);
    }
  };

  const updateAuthSettings = (key, value) => {
    setAuthSettings(prev => ({
      ...prev,
      [key]: value
    }));
    setMessage(`Updated ${key.replace('_', ' ')} setting`);
  };

  return (
    <div className="bg-slate-800 rounded-lg p-6">
      <div className="flex items-center mb-6">
        <ShieldCheckIcon className="h-6 w-6 text-sky-400 mr-3" />
        <h3 className="text-lg font-semibold text-sky-400">Authentication & Authorization</h3>
      </div>

      {/* Authentication Methods */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        {/* Local Authentication */}
        <div className="bg-slate-700 rounded-lg p-4 border border-slate-600">
          <div className="flex items-center mb-3">
            <UserIcon className="h-5 w-5 text-blue-400 mr-2" />
            <h4 className="text-white font-medium">Local Authentication</h4>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-slate-300 text-sm">Enabled</span>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={authSettings.local_auth_enabled}
                  onChange={(e) => updateAuthSettings('local_auth_enabled', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
              </label>
            </div>
            <p className="text-slate-400 text-xs">Allow users to create local accounts with username/password</p>
          </div>
        </div>

        {/* Microsoft SSO */}
        <div className="bg-slate-700 rounded-lg p-4 border border-slate-600">
          <div className="flex items-center mb-3">
            <div className="w-5 h-5 bg-blue-500 rounded mr-2"></div>
            <h4 className="text-white font-medium">Microsoft SSO</h4>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-slate-300 text-sm">Enabled</span>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={authSettings.microsoft_sso_enabled}
                  onChange={(e) => updateAuthSettings('microsoft_sso_enabled', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
              </label>
            </div>
            <button
              onClick={handleMicrosoftSSO}
              className="w-full px-3 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
            >
              Test Microsoft SSO
            </button>
            <p className="text-slate-400 text-xs">Azure AD / Office 365 authentication</p>
          </div>
        </div>

        {/* Google SSO */}
        <div className="bg-slate-700 rounded-lg p-4 border border-slate-600">
          <div className="flex items-center mb-3">
            <div className="w-5 h-5 bg-red-500 rounded mr-2"></div>
            <h4 className="text-white font-medium">Google SSO</h4>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-slate-300 text-sm">Enabled</span>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={authSettings.google_sso_enabled}
                  onChange={(e) => updateAuthSettings('google_sso_enabled', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
              </label>
            </div>
            <button
              onClick={handleGoogleSSO}
              className="w-full px-3 py-2 bg-red-600 text-white text-sm rounded hover:bg-red-700"
            >
              Configure Google SSO
            </button>
            <p className="text-slate-400 text-xs">Google Workspace authentication</p>
          </div>
        </div>
      </div>

      {/* Security Settings */}
      <div className="bg-slate-700 rounded-lg p-4 border border-slate-600 mb-6">
        <div className="flex items-center mb-4">
          <KeyIcon className="h-5 w-5 text-yellow-400 mr-2" />
          <h4 className="text-white font-medium">Security Settings</h4>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-slate-300 text-sm">Require MFA</span>
              <p className="text-slate-400 text-xs">Enforce multi-factor authentication for all users</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={authSettings.require_mfa}
                onChange={(e) => updateAuthSettings('require_mfa', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
            </label>
          </div>
          
          <div>
            <label className="block text-slate-300 text-sm mb-2">Session Timeout (hours)</label>
            <select
              value={authSettings.session_timeout}
              onChange={(e) => updateAuthSettings('session_timeout', parseInt(e.target.value))}
              className="w-full px-3 py-2 bg-slate-600 border border-slate-500 rounded-md text-white text-sm"
            >
              <option value={1}>1 hour</option>
              <option value={4}>4 hours</option>
              <option value={8}>8 hours</option>
              <option value={24}>24 hours</option>
            </select>
          </div>
        </div>
      </div>

      {/* Status Messages */}
      {message && (
        <div className="mb-4 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
          {message}
        </div>
      )}
      
      {error && (
        <div className="mb-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded flex items-center">
          <ExclamationTriangleIcon className="h-5 w-5 mr-2" />
          {error}
        </div>
      )}

      {/* Configuration Instructions */}
      <div className="bg-slate-700 rounded-lg p-4 border border-slate-600">
        <h4 className="text-white font-medium mb-3">Configuration Instructions</h4>
        <div className="space-y-3 text-sm">
          <div>
            <h5 className="text-sky-400 font-medium">Microsoft SSO Setup:</h5>
            <ol className="text-slate-300 list-decimal list-inside space-y-1 ml-4">
              <li>Register your application in Azure AD</li>
              <li>Configure redirect URI: <code className="bg-slate-800 px-1 rounded">https://your-domain.com/auth/microsoft/callback</code></li>
              <li>Set environment variables: <code className="bg-slate-800 px-1 rounded">MICROSOFT_CLIENT_ID</code>, <code className="bg-slate-800 px-1 rounded">MICROSOFT_CLIENT_SECRET</code></li>
              <li>Add API permissions for User.Read</li>
            </ol>
          </div>
          
          <div>
            <h5 className="text-sky-400 font-medium">Google SSO Setup:</h5>
            <ol className="text-slate-300 list-decimal list-inside space-y-1 ml-4">
              <li>Create OAuth 2.0 credentials in Google Cloud Console</li>
              <li>Configure authorized redirect URI</li>
              <li>Set environment variables: <code className="bg-slate-800 px-1 rounded">GOOGLE_CLIENT_ID</code>, <code className="bg-slate-800 px-1 rounded">GOOGLE_CLIENT_SECRET</code></li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthenticationPanel;
