import React, { useState, useContext } from 'react';
import { UserContext } from '../context/UserContext';
import { ChartBarIcon } from '@heroicons/react/24/outline';

// Simple test dashboard to identify the issue
const TestDashboard = () => {
    const { user } = useContext(UserContext);
    const [activeTab, setActiveTab] = useState('overview');

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-blue-900">
            <div className="max-w-7xl mx-auto px-6 py-8">
                {/* Header */}
                <div className="mb-8">
                    <div className="flex items-center space-x-3">
                        <div className="p-3 bg-gradient-to-r from-sky-500/20 to-blue-500/20 rounded-lg backdrop-blur-sm border border-sky-500/20">
                            <ChartBarIcon className="h-8 w-8 text-sky-400" />
                        </div>
                        <div>
                            <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-sky-400 to-blue-400">
                                Security Operations Center
                            </h1>
                            <p className="text-slate-400 mt-1">Test Dashboard</p>
                        </div>
                    </div>
                </div>

                {/* Simple Navigation */}
                <div className="mb-8">
                    <nav className="flex space-x-8 border-b border-slate-700">
                        <button
                            onClick={() => setActiveTab('overview')}
                            className={`py-2 px-1 border-b-2 font-medium text-sm ${
                                activeTab === 'overview'
                                    ? 'border-sky-500 text-sky-400'
                                    : 'border-transparent text-slate-400 hover:text-slate-300 hover:border-slate-300'
                            }`}
                        >
                            Test Overview
                        </button>
                    </nav>
                </div>

                {/* Simple Content */}
                <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-lg p-6">
                    <h2 className="text-xl font-semibold text-white">Dashboard Test</h2>
                    <p className="text-slate-400 mt-2">
                        If you can see this, the basic structure works. User: {user?.email || 'Not logged in'}
                    </p>
                </div>
            </div>
        </div>
    );
};

export default TestDashboard;
