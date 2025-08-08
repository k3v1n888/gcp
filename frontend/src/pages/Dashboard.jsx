import { useContext, useEffect, useState } from 'react';
import { UserContext } from '../context/UserContext';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Link } from 'react-router-dom';
import { ChartBarIcon } from '@heroicons/react/24/outline';
import AISummary from '../components/AISummary';
import ThreatForecast from '../components/ThreatForecast';
import SecurityOutlook from '../components/SecurityOutlook';
import AIIncidentManager from '../components/AIIncidentManager';
import ThreatsManager from '../components/ThreatsManager';
import IncidentsManager from '../components/IncidentsManager';
import AIThreatHunting from '../components/AIThreatHunting';
import { sanitizeApiResponse, formatNumber } from '../utils/dataUtils';

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
            const response = await fetch('/api/hunting/run', { method: 'POST' });
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
    const { user } = useContext(UserContext);
    const [logs, setLogs] = useState([]);
    const [analytics, setAnalytics] = useState(null);
    const [incidents, setIncidents] = useState([]);
    const [activeTab, setActiveTab] = useState('overview');

    useEffect(() => {
        const cacheBuster = `?_=${new Date().getTime()}`;
        fetch(`/api/threats${cacheBuster}`).then(res => res.json()).then(data => setLogs(sanitizeApiResponse(data)));
        fetch(`/api/analytics/summary${cacheBuster}`).then(res => res.json()).then(data => {
            const formattedData = {
              by_type: Object.entries(data.by_type).map(([name, value]) => ({ name, value })),
              by_source: Object.entries(data.by_source).map(([name, value]) => ({ name, value }))
            };
            setAnalytics(formattedData);
        });
        fetch(`/api/incidents${cacheBuster}`).then(res => res.json()).then(data => setIncidents(data));
        
        const socket = new WebSocket(`wss://${window.location.hostname}/ws/threats`);
        socket.onmessage = (event) => {
          const newLog = JSON.parse(event.data);
          setLogs((prev) => [newLog, ...prev]);
        };
        return () => socket.close();
    }, []);

    const COLORS = ['#38bdf8', '#4ade80', '#facc15', '#fb923c', '#f87171'];

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
                    <button
                        onClick={() => setActiveTab('ai-incidents')}
                        className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                            activeTab === 'ai-incidents'
                                ? 'border-purple-500 text-purple-400'
                                : 'border-transparent text-slate-400 hover:text-slate-300 hover:border-slate-300'
                        }`}
                    >
                        <span>🤖</span>
                        <span>AI Incident Orchestrator</span>
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

                    <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                        <div className="space-y-6">
                            <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-lg p-6">
                                <ThreatHuntWidget />
                            </div>
                        </div>
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
                                                        data={analytics.sources} 
                                                        cx="50%" 
                                                        cy="50%" 
                                                        outerRadius={80} 
                                                        fill="#8884d8" 
                                                        dataKey="value" 
                                                        label={({ name }) => name}
                                                    >
                                                        {analytics.sources.map((entry, index) => (
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
                                                <BarChart data={analytics.daily}>
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

                    <div className="grid grid-cols-12 gap-6">
                        <div className="col-span-12 bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-lg p-6 mb-6">
                            <div className="flex items-center justify-between mb-4">
                                <h2 className="text-xl font-semibold text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-red-400">
                                    Open Security Incidents
                                </h2>
                                <span className="text-sm text-slate-400 bg-slate-800/50 px-3 py-1 rounded-full">
                                    {incidents.length} Total
                                </span>
                            </div>
                            <div className="max-h-80 overflow-y-auto scrollbar-thin scrollbar-track-slate-800 scrollbar-thumb-sky-600">
                                <div className="overflow-x-auto">
                                    <table className="cyber-table">
                                        <thead className="sticky top-0 bg-slate-900 z-10">
                                            <tr>
                                                <th>Incident</th>
                                                <th>Status</th>
                                                <th>Severity</th>
                                                <th>Last Activity</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {incidents.length > 0 ? (
                                                incidents.map((incident) => (
                                                    <tr key={incident.id} className="hover:bg-slate-800">
                                                        <td><Link to={`/incidents/${incident.id}`} className="text-sky-400 hover:underline">{incident.title}</Link></td>
                                                        <td><span className="text-orange-400 font-semibold">{incident.status.toUpperCase()}</span></td>
                                                        <td><SeverityBadge severity={incident.severity} /></td>
                                                        <td>{new Date(incident.end_time).toLocaleString()}</td>
                                                    </tr>
                                                ))
                                            ) : (
                                                <tr>
                                                    <td colSpan="4" className="text-center text-slate-500 py-8">
                                                        No security incidents found
                                                    </td>
                                                </tr>
                                            )}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>

                        <div className="col-span-12 bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-lg p-6">
                            <div className="flex items-center justify-between mb-4">
                                <h2 className="text-xl font-semibold text-transparent bg-clip-text bg-gradient-to-r from-red-400 to-pink-400">
                                    Live Threat Intel Feed
                                </h2>
                                <div className="flex items-center space-x-3">
                                    <span className="text-sm text-slate-400 bg-slate-800/50 px-3 py-1 rounded-full">
                                        {logs.length} Active Threats
                                    </span>
                                    <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                                    <span className="text-xs text-red-400 font-semibold">LIVE</span>
                                </div>
                            </div>
                            <div className="max-h-96 overflow-y-auto scrollbar-thin scrollbar-track-slate-800 scrollbar-thumb-sky-600">
                                <div className="overflow-x-auto">
                                    <table className="cyber-table">
                                        <thead className="sticky top-0 bg-slate-900 z-10">
                                            <tr>
                                                <th>IP</th>
                                                <th className="w-40">IP Reputation</th>
                                                <th>Threat</th>
                                                <th>Source</th>
                                                <th>CVE</th>
                                                <th>Severity</th>
                                                <th>Status</th>
                                                <th>Timestamp</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {logs.length > 0 ? (
                                                logs.map((log) => (
                                                    <tr key={log.id} className="hover:bg-slate-800 transition-colors duration-200">
                                                        <td className="font-mono text-slate-400">{log.ip}</td>
                                                        <td><ReputationScore score={log.ip_reputation_score} /></td>
                                                        <td><Link to={`/threats/${log.id}`} className="text-sky-400 hover:underline">{log.threat}</Link></td>
                                                        <td>{log.source}</td>
                                                        <td className="font-mono">{log.cve_id || 'N/A'}</td>
                                                        <td><SeverityBadge severity={log.severity} /></td>
                                                        <td>
                                                            {log.is_anomaly && (<span className="text-fuchsia-400 font-semibold mr-2">Anomaly</span>)}
                                                            {log.source === 'UEBA Engine' && (<span className="text-amber-400 font-semibold">Insider</span>)}
                                                        </td>
                                                        <td>{log.timestamp ? new Date(log.timestamp).toLocaleString() : 'N/A'}</td>
                                                    </tr>
                                                ))
                                            ) : (
                                                <tr>
                                                    <td colSpan="8" className="text-center text-slate-500 py-8">
                                                        <div className="flex flex-col items-center">
                                                            <div className="w-12 h-12 bg-slate-700 rounded-full flex items-center justify-center mb-3">
                                                                <svg className="w-6 h-6 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.031 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                                                                </svg>
                                                            </div>
                                                            <span>No active threats detected</span>
                                                        </div>
                                                    </td>
                                                </tr>
                                            )}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {activeTab === 'incidents' && (
                <IncidentsManager />
            )}

            {activeTab === 'threats' && (
                <ThreatsManager />
            )}

            {activeTab === 'ai-hunting' && (
                <AIThreatHunting />
            )}

            {activeTab === 'ai-incidents' && (
                <AIIncidentManager />
            )}
            </div>
        </div>
    );
}