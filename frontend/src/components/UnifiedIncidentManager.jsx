import React, { useState, useEffect, useContext } from 'react';
import { UserContext } from '../context/UserContext';
import { useDevUser } from '../context/DevUserContext';
import { isDevelopment, getApiBaseUrl } from '../utils/environment';
import { Link } from 'react-router-dom';
import { 
    ExclamationTriangleIcon,
    ClockIcon,
    CheckCircleIcon,
    XCircleIcon,
    ChartBarIcon,
    FunnelIcon,
    EyeIcon,
    ArrowTopRightOnSquareIcon,
    CalendarIcon,
    UserIcon,
    TagIcon,
    MagnifyingGlassIcon,
    ShieldCheckIcon,
    CpuChipIcon,
    PlayIcon,
    SparklesIcon,
    Bars3Icon,
    PlusIcon
} from '@heroicons/react/24/outline';

/**
 * Unified Incident Management Component
 * Combines traditional incident management with AI-powered orchestration
 */
const UnifiedIncidentManager = () => {
    // Use appropriate context/hook based on environment
    let user = null;
    
    try {
        if (isDevelopment()) {
            const devContext = useDevUser();
            user = devContext.user;
            console.log('🔧 UnifiedIncidentManager using DevUserContext, user:', user);
        }
    } catch (e) {
        console.log('🔧 DevUserContext not available in UnifiedIncidentManager, falling back');
    }
    
    try {
        if (!isDevelopment()) {
            const prodContext = useContext(UserContext);
            user = prodContext?.user;
            console.log('🔒 UnifiedIncidentManager using UserContext, user:', user);
        }
    } catch (e) {
        console.log('🔒 UserContext not available in UnifiedIncidentManager');
    }

    // State management
    const [activeView, setActiveView] = useState('incidents'); // 'incidents', 'ai-orchestration', 'aggregation'
    const [incidents, setIncidents] = useState([]);
    const [filteredIncidents, setFilteredIncidents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    
    // Filter states for traditional view
    const [statusFilter, setStatusFilter] = useState('all');
    const [severityFilter, setSeverityFilter] = useState('all');
    const [searchTerm, setSearchTerm] = useState('');
    
    // AI Orchestration states
    const [orchestrationStatus, setOrchestrationStatus] = useState('idle');
    const [selectedIncident, setSelectedIncident] = useState(null);
    const [aiAnalysis, setAiAnalysis] = useState(null);
    const [dashboardMetrics, setDashboardMetrics] = useState(null);
    
    // Modal state
    const [showModal, setShowModal] = useState(false);
    
    // Statistics
    const [stats, setStats] = useState({
        total: 0,
        open: 0,
        inProgress: 0,
        resolved: 0,
        critical: 0,
        high: 0,
        medium: 0,
        low: 0
    });

    // Load data on component mount
    useEffect(() => {
        fetchIncidents();
        fetchDashboardMetrics();
        
        // Auto-refresh every 2 minutes
        const interval = setInterval(() => {
            fetchIncidents();
            fetchDashboardMetrics();
        }, 120000);
        
        return () => clearInterval(interval);
    }, []);

    // Filter incidents when filters change
    useEffect(() => {
        let filtered = incidents;
        
        if (statusFilter !== 'all') {
            filtered = filtered.filter(incident => 
                incident.status?.toLowerCase() === statusFilter.toLowerCase()
            );
        }
        
        if (severityFilter !== 'all') {
            filtered = filtered.filter(incident => 
                incident.severity?.toLowerCase() === severityFilter.toLowerCase()
            );
        }
        
        if (searchTerm) {
            const term = searchTerm.toLowerCase();
            filtered = filtered.filter(incident =>
                incident.title?.toLowerCase().includes(term) ||
                incident.description?.toLowerCase().includes(term) ||
                incident.source?.toLowerCase().includes(term) ||
                incident.assignee?.toLowerCase().includes(term)
            );
        }
        
        setFilteredIncidents(filtered);
        calculateStats(filtered);
    }, [incidents, statusFilter, severityFilter, searchTerm]);

    const fetchIncidents = async () => {
        try {
            setLoading(true);
            const apiBaseUrl = getApiBaseUrl();
            const response = await fetch(`${apiBaseUrl}/api/incidents`);
            
            if (response.ok) {
                const data = await response.json();
                setIncidents(data);
                setError(null);
            } else {
                setError('Failed to fetch incidents');
            }
        } catch (error) {
            console.error('Error fetching incidents:', error);
            setError('Failed to fetch incidents');
        } finally {
            setLoading(false);
        }
    };

    const fetchDashboardMetrics = async () => {
        try {
            const apiBaseUrl = getApiBaseUrl();
            const response = await fetch(`${apiBaseUrl}/api/analytics/incidents-summary`);
            
            if (response.ok) {
                const data = await response.json();
                setDashboardMetrics(data);
            }
        } catch (error) {
            console.error('Failed to fetch dashboard metrics:', error);
        }
    };

    const calculateStats = (incidents) => {
        const stats = {
            total: incidents.length,
            open: 0,
            inProgress: 0,
            resolved: 0,
            critical: 0,
            high: 0,
            medium: 0,
            low: 0
        };

        incidents.forEach(incident => {
            // Status stats
            const status = incident.status?.toLowerCase();
            if (status === 'open') stats.open++;
            else if (status === 'in-progress' || status === 'in_progress') stats.inProgress++;
            else if (status === 'resolved') stats.resolved++;

            // Severity stats  
            const severity = incident.severity?.toLowerCase();
            if (severity === 'critical') stats.critical++;
            else if (severity === 'high') stats.high++;
            else if (severity === 'medium') stats.medium++;
            else if (severity === 'low') stats.low++;
        });

        setStats(stats);
    };

    const triggerAIOrchestration = async () => {
        try {
            setOrchestrationStatus('running');
            const apiBaseUrl = getApiBaseUrl();
            
            // Trigger threat aggregation
            const response = await fetch(`${apiBaseUrl}/api/incidents/aggregate-threats`, {
                method: 'POST'
            });
            
            if (response.ok) {
                const result = await response.json();
                setOrchestrationStatus('completed');
                
                // Refresh incidents
                fetchIncidents();
                
                alert(`AI Orchestration completed! Created ${result.incidents_created || 0} new incidents.`);
            } else {
                setOrchestrationStatus('error');
                alert('AI Orchestration failed. Please try again.');
            }
        } catch (error) {
            console.error('AI Orchestration error:', error);
            setOrchestrationStatus('error');
            alert('AI Orchestration failed. Please try again.');
        }
    };

    // Helper components
    const SeverityBadge = ({ severity }) => {
        const severityStyles = {
            critical: 'bg-red-600 text-white border-red-500',
            high: 'bg-orange-500 text-white border-orange-400',
            medium: 'bg-yellow-400 text-black border-yellow-300',
            low: 'bg-sky-500 text-white border-sky-400',
            unknown: 'bg-slate-500 text-white border-slate-400'
        };

        return (
            <span className={`px-2 py-1 text-xs font-semibold rounded border ${severityStyles[severity?.toLowerCase()] || severityStyles.unknown}`}>
                {severity?.toUpperCase() || 'UNKNOWN'}
            </span>
        );
    };

    const StatusBadge = ({ status }) => {
        const statusStyles = {
            open: 'bg-red-600 text-white border-red-500',
            'in-progress': 'bg-orange-500 text-white border-orange-400',
            'in_progress': 'bg-orange-500 text-white border-orange-400',
            resolved: 'bg-green-600 text-white border-green-500',
            closed: 'bg-slate-600 text-white border-slate-500'
        };

        const statusIcons = {
            open: ExclamationTriangleIcon,
            'in-progress': ClockIcon,
            'in_progress': ClockIcon,
            resolved: CheckCircleIcon,
            closed: XCircleIcon
        };

        const statusKey = status?.toLowerCase();
        const IconComponent = statusIcons[statusKey] || ExclamationTriangleIcon;

        return (
            <span className={`inline-flex items-center px-2 py-1 text-xs font-semibold rounded border ${statusStyles[statusKey] || statusStyles.open}`}>
                <IconComponent className="w-3 h-3 mr-1" />
                {status?.replace('_', ' ').toUpperCase() || 'UNKNOWN'}
            </span>
        );
    };

    const StatCard = ({ title, value, icon: Icon, color = 'sky' }) => (
        <div className={`bg-gradient-to-br from-slate-800/50 to-slate-700/30 backdrop-blur-sm border border-slate-600/50 rounded-lg p-4`}>
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-slate-400 text-sm font-medium">{title}</p>
                    <p className={`text-2xl font-bold text-${color}-400`}>{value}</p>
                </div>
                <div className={`p-3 bg-${color}-500/20 rounded-lg`}>
                    <Icon className={`h-6 w-6 text-${color}-400`} />
                </div>
            </div>
        </div>
    );

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-blue-900 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-400 mx-auto mb-4"></div>
                    <p className="text-slate-400">Loading incidents...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-blue-900">
            <div className="max-w-7xl mx-auto px-6 py-8">
                {/* Header */}
                <div className="mb-8">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                            <div className="p-3 bg-gradient-to-r from-orange-500/20 to-red-500/20 rounded-lg backdrop-blur-sm border border-orange-500/20">
                                <ExclamationTriangleIcon className="h-8 w-8 text-orange-400" />
                            </div>
                            <div>
                                <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-red-400">
                                    Incident Management Center
                                </h1>
                                <p className="text-slate-400 mt-1">
                                    Unified incident tracking with AI-powered orchestration
                                </p>
                            </div>
                        </div>
                        <div className="flex items-center space-x-3">
                            <button
                                onClick={triggerAIOrchestration}
                                disabled={orchestrationStatus === 'running'}
                                className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white text-sm font-medium rounded-lg hover:from-purple-700 hover:to-pink-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 focus:ring-offset-slate-900 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                            >
                                <SparklesIcon className="w-4 h-4 mr-2" />
                                {orchestrationStatus === 'running' ? 'AI Processing...' : 'AI Orchestration'}
                            </button>
                        </div>
                    </div>
                </div>

                {/* Statistics Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    <StatCard title="Total Incidents" value={stats.total} icon={Bars3Icon} color="sky" />
                    <StatCard title="Open Incidents" value={stats.open} icon={ExclamationTriangleIcon} color="red" />
                    <StatCard title="In Progress" value={stats.inProgress} icon={ClockIcon} color="orange" />
                    <StatCard title="Resolved" value={stats.resolved} icon={CheckCircleIcon} color="green" />
                </div>

                {/* View Selector */}
                <div className="mb-8">
                    <nav className="flex space-x-8 border-b border-slate-700">
                        <button
                            onClick={() => setActiveView('incidents')}
                            className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                                activeView === 'incidents'
                                    ? 'border-orange-500 text-orange-400'
                                    : 'border-transparent text-slate-400 hover:text-slate-300 hover:border-slate-300'
                            }`}
                        >
                            <Bars3Icon className="w-4 h-4" />
                            <span>All Incidents</span>
                        </button>
                        <button
                            onClick={() => setActiveView('ai-orchestration')}
                            className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                                activeView === 'ai-orchestration'
                                    ? 'border-purple-500 text-purple-400'
                                    : 'border-transparent text-slate-400 hover:text-slate-300 hover:border-slate-300'
                            }`}
                        >
                            <SparklesIcon className="w-4 h-4" />
                            <span>AI Orchestration</span>
                        </button>
                    </nav>
                </div>

                {/* Content based on active view */}
                {activeView === 'incidents' && (
                    <div className="space-y-6">
                        {/* Filters */}
                        <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-lg p-6">
                            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-slate-300 mb-2">Status</label>
                                    <select
                                        value={statusFilter}
                                        onChange={(e) => setStatusFilter(e.target.value)}
                                        className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:ring-2 focus:ring-sky-500"
                                    >
                                        <option value="all">All Statuses</option>
                                        <option value="open">Open</option>
                                        <option value="in-progress">In Progress</option>
                                        <option value="resolved">Resolved</option>
                                        <option value="closed">Closed</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-slate-300 mb-2">Severity</label>
                                    <select
                                        value={severityFilter}
                                        onChange={(e) => setSeverityFilter(e.target.value)}
                                        className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:ring-2 focus:ring-sky-500"
                                    >
                                        <option value="all">All Severities</option>
                                        <option value="critical">Critical</option>
                                        <option value="high">High</option>
                                        <option value="medium">Medium</option>
                                        <option value="low">Low</option>
                                    </select>
                                </div>
                                <div className="md:col-span-2">
                                    <label className="block text-sm font-medium text-slate-300 mb-2">Search</label>
                                    <div className="relative">
                                        <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
                                        <input
                                            type="text"
                                            placeholder="Search incidents..."
                                            value={searchTerm}
                                            onChange={(e) => setSearchTerm(e.target.value)}
                                            className="w-full pl-10 pr-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-200 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500"
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Incidents Table */}
                        <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-lg overflow-hidden">
                            <div className="overflow-x-auto">
                                <table className="min-w-full divide-y divide-slate-700">
                                    <thead className="bg-slate-900/50">
                                        <tr>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">
                                                Incident
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">
                                                Status
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">
                                                Severity
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">
                                                Created
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">
                                                Actions
                                            </th>
                                        </tr>
                                    </thead>
                                    <tbody className="bg-transparent divide-y divide-slate-700">
                                        {filteredIncidents.length > 0 ? filteredIncidents.map((incident) => (
                                            <tr key={incident.id} className="hover:bg-slate-700/30 transition-colors duration-200">
                                                <td className="px-6 py-4 whitespace-nowrap">
                                                    <div>
                                                        <div className="text-sm font-medium text-slate-200">
                                                            {incident.title || `Incident #${incident.id}`}
                                                        </div>
                                                        <div className="text-sm text-slate-400 max-w-xs truncate">
                                                            {incident.description || incident.summary || 'No description available'}
                                                        </div>
                                                    </div>
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap">
                                                    <StatusBadge status={incident.status} />
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap">
                                                    <SeverityBadge severity={incident.severity} />
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                                                    {incident.created_at ? new Date(incident.created_at).toLocaleString() : 'Unknown'}
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                                    <Link 
                                                        to={`/incidents/${incident.id}`}
                                                        className="text-sky-400 hover:text-sky-300 flex items-center space-x-1"
                                                    >
                                                        <EyeIcon className="w-4 h-4" />
                                                        <span>View</span>
                                                    </Link>
                                                </td>
                                            </tr>
                                        )) : (
                                            <tr>
                                                <td colSpan="5" className="px-6 py-12 text-center text-slate-400">
                                                    No incidents found matching your criteria.
                                                </td>
                                            </tr>
                                        )}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                )}

                {activeView === 'ai-orchestration' && (
                    <div className="space-y-6">
                        <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-lg p-6">
                            <h2 className="text-xl font-semibold text-purple-400 mb-4 flex items-center">
                                <SparklesIcon className="w-6 h-6 mr-2" />
                                AI-Powered Incident Orchestration
                            </h2>
                            <p className="text-slate-400 mb-6">
                                Leverage artificial intelligence to automatically aggregate threats, correlate patterns, 
                                and create comprehensive investigation-ready incidents.
                            </p>
                            
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                <div className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/20 rounded-lg p-4">
                                    <CpuChipIcon className="w-8 h-8 text-purple-400 mb-3" />
                                    <h3 className="text-lg font-semibold text-purple-300 mb-2">Threat Correlation</h3>
                                    <p className="text-slate-400 text-sm">
                                        AI analyzes threat patterns and correlates related security events across multiple sources.
                                    </p>
                                </div>
                                
                                <div className="bg-gradient-to-br from-blue-500/10 to-cyan-500/10 border border-blue-500/20 rounded-lg p-4">
                                    <ShieldCheckIcon className="w-8 h-8 text-blue-400 mb-3" />
                                    <h3 className="text-lg font-semibold text-blue-300 mb-2">Smart Aggregation</h3>
                                    <p className="text-slate-400 text-sm">
                                        Automatically groups related threats into comprehensive incidents with full context.
                                    </p>
                                </div>
                                
                                <div className="bg-gradient-to-br from-green-500/10 to-teal-500/10 border border-green-500/20 rounded-lg p-4">
                                    <ChartBarIcon className="w-8 h-8 text-green-400 mb-3" />
                                    <h3 className="text-lg font-semibold text-green-300 mb-2">Investigation Intel</h3>
                                    <p className="text-slate-400 text-sm">
                                        Generates investigation-ready reports with timelines, attack chains, and recommendations.
                                    </p>
                                </div>
                            </div>

                            <div className="mt-6 p-4 bg-slate-900/30 rounded-lg">
                                <div className="flex items-center justify-between mb-3">
                                    <h4 className="text-lg font-medium text-slate-200">Orchestration Status</h4>
                                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                                        orchestrationStatus === 'idle' ? 'bg-slate-600 text-slate-200' :
                                        orchestrationStatus === 'running' ? 'bg-orange-600 text-white' :
                                        orchestrationStatus === 'completed' ? 'bg-green-600 text-white' :
                                        'bg-red-600 text-white'
                                    }`}>
                                        {orchestrationStatus.toUpperCase()}
                                    </span>
                                </div>
                                <p className="text-slate-400 text-sm mb-4">
                                    {orchestrationStatus === 'idle' && 'Ready to analyze threats and create incidents.'}
                                    {orchestrationStatus === 'running' && 'AI is analyzing threat patterns and creating incidents...'}
                                    {orchestrationStatus === 'completed' && 'Orchestration completed successfully. New incidents have been created.'}
                                    {orchestrationStatus === 'error' && 'Orchestration failed. Please check logs and try again.'}
                                </p>
                                <button
                                    onClick={triggerAIOrchestration}
                                    disabled={orchestrationStatus === 'running'}
                                    className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-medium rounded-lg hover:from-purple-700 hover:to-pink-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 focus:ring-offset-slate-900 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                                >
                                    <PlayIcon className="w-5 h-5 mr-2" />
                                    {orchestrationStatus === 'running' ? 'Processing...' : 'Run AI Orchestration'}
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default UnifiedIncidentManager;
