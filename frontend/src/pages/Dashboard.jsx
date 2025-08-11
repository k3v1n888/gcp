import { useContext, useEffect, useState } from 'react';
import { UserContext } from '../context/UserContext';
import { useDevUser } from '../context/DevUserContext';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Link } from 'react-router-dom';
import { ChartBarIcon } from '@heroicons/react/24/outline';
import AISummary from '../components/AISummary';
import ThreatForecast from '../components/ThreatForecast';
import SecurityOutlook from '../components/SecurityOutlook';
import ThreatsManager from '../components/ThreatsManager';
import UnifiedIncidentManager from '../components/UnifiedIncidentManager';
import AIThreatHunting from '../components/AIThreatHunting';
import { sanitizeApiResponse, formatNumber } from '../utils/dataUtils';
import { isDevelopment, getApiBaseUrl } from '../utils/environment';

// Helper component for the IP Reputation progress bar
const ReputationScore = ({ score }) => {
    // Safely handle the score value
    const numericScore = (() => {
        if (score === null || score === undefined || isNaN(score) || !isFinite(score)) {
            return 0;
        }
        return Math.max(0, Math.min(100, Number(score))); // Clamp between 0-100
    })();
    
    const getScoreColor = () => {
        if (numericScore > 75) return 'bg-red-600';
        if (numericScore > 40) return 'bg-orange-500';
        return 'bg-green-600';
    };
    
    return (
        <div className="flex items-center">
            <div className="w-full bg-slate-700 rounded-full h-2.5">
                <div 
                    className={`${getScoreColor()} h-2.5 rounded-full`} 
                    style={{ width: `${numericScore}%` }} 
                    title={`MISP Score: ${formatNumber(numericScore)}`}
                ></div>
            </div>
            <span className="text-xs font-semibold ml-3 text-slate-300">
                {formatNumber(numericScore)}
            </span>
        </div>
    );
};

// Helper component for the color-coded severity badges
const SeverityBadge = ({ severity }) => {
    const severityStyles = {
        critical: 'bg-red-600 text-white',
        high: 'bg-orange-500 text-white',
        medium: 'bg-yellow-400 text-black',
        low: 'bg-sky-500 text-white',
        unknown: 'bg-slate-500 text-white',
    };
    const severityKey = typeof severity === 'string' ? severity.toLowerCase() : 'unknown';
    return (<span className={`px-2.5 py-1 rounded-full text-xs font-bold ${severityStyles[severityKey] || severityStyles.unknown}`}>{severity.toUpperCase()}</span>);
};

// --- NEW: Widget for AI-Driven Threat Hunting ---
const ThreatHuntWidget = () => {
    const [huntResults, setHuntResults] = useState(null);
    const [isHunting, setIsHunting] = useState(false);

    const startHunt = async () => {
        setIsHunting(true);
        setHuntResults(null);
        try {
            const apiBaseUrl = getApiBaseUrl();
            const response = await fetch(`${apiBaseUrl}/api/hunting/run`, { method: 'POST' });
            const data = await response.json();
            setHuntResults(data);
        } catch (error) {
            setHuntResults({ error: "Failed to run threat hunt." });
        } finally {
            setIsHunting(false);
        }
    };

    return (
        <div className="widget-card p-6">
            <h2 className="text-xl font-semibold mb-4 text-sky-400">AI-Driven Threat Hunting</h2>
            <p className="text-slate-400 mb-4">Launch a proactive hunt for stealthy threats based on the AI model's learned indicators of compromise.</p>
            <button onClick={startHunt} disabled={isHunting} className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-sky-600 hover:bg-sky-700 disabled:bg-slate-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-sky-500">
                {isHunting ? 'Hunting...' : 'Start New Hunt'}
            </button>
            {huntResults && (
                <div className="mt-4">
                    <h3 className="font-semibold text-slate-200">Hunt Complete</h3>
                    <p className="text-sm text-slate-400">Found {huntResults.results?.found_alerts?.length || 0} potential threats matching top indicators.</p>
                </div>
            )}
        </div>
    );
};

export default function Dashboard() {
    console.log('🔥 Dashboard component loading...');
    
    // Use appropriate context/hook based on environment
    let user = null;
    let devUser = null;
    let prodUser = null;
    
    try {
        if (isDevelopment()) {
            const devContext = useDevUser();
            devUser = devContext.user;
            user = devUser;
            console.log('🔧 Dashboard using DevUserContext, user:', user);
        }
    } catch (e) {
        console.log('🔧 DevUserContext not available, falling back');
    }
    
    try {
        if (!isDevelopment()) {
            const prodContext = useContext(UserContext);
            prodUser = prodContext?.user;
            user = prodUser;
            console.log('� Dashboard using UserContext, user:', user);
        }
    } catch (e) {
        console.log('🔒 UserContext not available');
    }
    
    const [logs, setLogs] = useState([]);
    const [analytics, setAnalytics] = useState(null);
    const [incidents, setIncidents] = useState([]);
    const [activeTab, setActiveTab] = useState('overview');

    console.log('🔥 Dashboard state initialized, user:', user);

    useEffect(() => {
        console.log('🔥 Dashboard useEffect starting...');
        const cacheBuster = `?_=${new Date().getTime()}`;
        const apiBaseUrl = getApiBaseUrl();
        console.log('🔥 Using API base URL:', apiBaseUrl);
        
        // Add timeout to fetch calls
        const fetchWithTimeout = (url, options = {}, timeout = 30000) => {
            return Promise.race([
                fetch(url, options),
                new Promise((_, reject) => 
                    setTimeout(() => reject(new Error('Request timeout')), timeout)
                )
            ]);
        };
        
        fetchWithTimeout(`${apiBaseUrl}/api/threats${cacheBuster}`, {}, 30000)
            .then(res => {
                console.log('🔥 Threats API response:', res.status);
                return res.json();
            })
            .then(data => {
                console.log('🔥 Threats data:', data?.length, 'items');
                setLogs(sanitizeApiResponse(data));
            })
            .catch(error => {
                console.error('❌ Threats API error:', error);
                setLogs([]); // Set empty array on timeout
            });
            
        fetchWithTimeout(`${apiBaseUrl}/api/analytics/summary${cacheBuster}`, {}, 30000)
            .then(res => {
                console.log('🔥 Analytics API response:', res.status);
                return res.json();
            })
            .then(data => {
                console.log('🔥 Analytics data:', data);
                const formattedData = {
                  by_type: Object.entries(data.by_type || {}).map(([name, value]) => ({ name, value })),
                  by_source: Object.entries(data.by_source || {}).map(([name, value]) => ({ name, value })),
                  sources: Object.entries(data.by_source || {}).map(([name, value]) => ({ name, value })),
                  daily: data.daily || []
                };
                setAnalytics(formattedData);
            })
            .catch(error => {
                console.error('❌ Analytics API error:', error);
                setAnalytics({ sources: [], daily: [], by_type: [], by_source: [] });
            });
            
        fetchWithTimeout(`${apiBaseUrl}/api/incidents${cacheBuster}`, {}, 30000)
            .then(res => {
                console.log('🔥 Incidents API response:', res.status);
                return res.json();
            })
            .then(data => {
                console.log('🔥 Incidents data:', data?.length, 'items');
                setIncidents(data);
            })
            .catch(error => {
                console.error('❌ Incidents API error:', error);
                setIncidents([]); // Set empty array on timeout
            });
        
        try {
            // Fix WebSocket URL for development
            const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = isDevelopment() 
                ? `ws://192.168.64.13:8000/ws/threats` 
                : `${wsProtocol}//${window.location.hostname}/ws/threats`;
            console.log('🔗 WebSocket URL:', wsUrl);
            const socket = new WebSocket(wsUrl);
            socket.onmessage = (event) => {
              const newLog = JSON.parse(event.data);
              setLogs((prev) => [newLog, ...prev]);
            };
            socket.onerror = (error) => console.error('❌ WebSocket error:', error);
            return () => socket.close();
        } catch (error) {
            console.error('❌ WebSocket setup error:', error);
        }
    }, []);

    const COLORS = ['#38bdf8', '#4ade80', '#facc15', '#fb923c', '#f87171'];

    console.log('🔥 Dashboard rendering, activeTab:', activeTab);

    try {
        return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-blue-900">
            <div className="max-w-7xl mx-auto px-6 py-8">
                {/* Header with same styling as AI Incident Manager */}
                <div className="mb-8">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                            <div className="p-3 bg-gradient-to-r from-sky-500/20 to-blue-500/20 rounded-lg backdrop-blur-sm border border-sky-500/20">
                                <ChartBarIcon className="h-8 w-8 text-sky-400" />
                            </div>
                            <div>
                                <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-sky-400 to-blue-400">
                                    Security Operations Center
                                </h1>
                                <p className="text-slate-400 mt-1">
                                    Comprehensive cybersecurity management platform
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Tab Navigation */}
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
                        Security Overview
                    </button>
                    <button
                        onClick={() => setActiveTab('incidents')}
                        className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                            activeTab === 'incidents'
                                ? 'border-orange-500 text-orange-400'
                                : 'border-transparent text-slate-400 hover:text-slate-300 hover:border-slate-300'
                        }`}
                    >
                        <span>⚠️</span>
                        <span>Incidents</span>
                    </button>
                    <button
                        onClick={() => setActiveTab('threats')}
                        className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                            activeTab === 'threats'
                                ? 'border-red-500 text-red-400'
                                : 'border-transparent text-slate-400 hover:text-slate-300 hover:border-slate-300'
                        }`}
                    >
                        <span>🔍</span>
                        <span>Threats</span>
                    </button>
                    <button
                        onClick={() => setActiveTab('ai-hunting')}
                        className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                            activeTab === 'ai-hunting'
                                ? 'border-pink-500 text-pink-400'
                                : 'border-transparent text-slate-400 hover:text-slate-300 hover:border-slate-300'
                        }`}
                    >
                        <span>🧠</span>
                        <span>AI Hunting</span>
                    </button>
                </nav>
            </div>

            {/* Tab Content */}
            {activeTab === 'overview' && (
                <div className="space-y-8">
                    {/* Enhanced Security Outlook - Full Width with AI Theme */}
                    <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-lg p-6">
                        <SecurityOutlook />
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-lg p-6">
                            <AISummary />
                        </div>
                        <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-lg p-6">
                            <ThreatForecast />
                        </div>
                    </div>

                    <div className="grid grid-cols-1 gap-6">
                        <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-lg p-6">
                            {analytics && (
                                <>
                                    <h2 className="text-xl font-semibold text-transparent bg-clip-text bg-gradient-to-r from-sky-400 to-blue-400 mb-4">
                                        Security Analytics
                                    </h2>
                                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                                        <div className="bg-slate-900/30 p-4 rounded-lg">
                                            <h3 className="text-slate-300 font-medium mb-2">Threat Sources</h3>
                                            <ResponsiveContainer width="100%" height={200}>
                                                <PieChart>
                                                    <Pie 
                                                        data={analytics.sources || []} 
                                                        cx="50%" 
                                                        cy="50%" 
                                                        outerRadius={80} 
                                                        fill="#8884d8" 
                                                        dataKey="value" 
                                                        label={({ name }) => name}
                                                    >
                                                        {(analytics.sources || []).map((entry, index) => (
                                                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                                        ))}
                                                    </Pie>
                                                    <Tooltip />
                                                </PieChart>
                                            </ResponsiveContainer>
                                        </div>
                                        <div className="bg-slate-900/30 p-4 rounded-lg">
                                            <h3 className="text-slate-300 font-medium mb-2">Daily Threats</h3>
                                            <ResponsiveContainer width="100%" height={200}>
                                                <BarChart data={analytics.daily || []}>
                                                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                                                    <XAxis dataKey="date" stroke="#9CA3AF" />
                                                    <YAxis stroke="#9CA3AF" />
                                                    <Tooltip />
                                                    <Bar dataKey="count" fill="#38bdf8" />
                                                </BarChart>
                                            </ResponsiveContainer>
                                        </div>
                                    </div>
                                </>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {activeTab === 'incidents' && (
                <UnifiedIncidentManager />
            )}

            {activeTab === 'threats' && (
                <ThreatsManager />
            )}

            {activeTab === 'ai-hunting' && (
                <AIThreatHunting />
            )}
            </div>
        </div>
    );
    } catch (error) {
        console.error('❌ Dashboard render error:', error);
        return (
            <div className="min-h-screen bg-red-900 p-8">
                <div className="text-white">
                    <h1>Dashboard Error</h1>
                    <p>Error: {error.message}</p>
                    <pre>{error.stack}</pre>
                </div>
            </div>
        );
    }
}