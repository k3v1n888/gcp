

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
    MagnifyingGlassIcon
} from '@heroicons/react/24/outline';

const IncidentsManager = () => {
    // Use appropriate context/hook based on environment
    let user = null;
    
    try {
        if (isDevelopment()) {
            const devContext = useDevUser();
            user = devContext.user;
            console.log('🔧 IncidentsManager using DevUserContext, user:', user);
        }
    } catch (e) {
        console.log('🔧 DevUserContext not available in IncidentsManager, falling back');
    }
    
    try {
        if (!isDevelopment()) {
            const prodContext = useContext(UserContext);
            user = prodContext?.user;
            console.log('🔒 IncidentsManager using UserContext, user:', user);
        }
    } catch (e) {
        console.log('🔒 UserContext not available in IncidentsManager');
    }

    const [incidents, setIncidents] = useState([]);
    const [filteredIncidents, setFilteredIncidents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    
    // Filter states
    const [statusFilter, setStatusFilter] = useState('all');
    const [severityFilter, setSeverityFilter] = useState('all');
    const [searchTerm, setSearchTerm] = useState('');
    
    // Modal state
    const [selectedIncident, setSelectedIncident] = useState(null);
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

    // Status options
    const statusOptions = ['all', 'open', 'in-progress', 'resolved', 'closed'];
    const severityOptions = ['all', 'critical', 'high', 'medium', 'low'];

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
            resolved: 'bg-green-600 text-white border-green-500',
            closed: 'bg-slate-600 text-white border-slate-500'
        };

        const statusIcons = {
            open: ExclamationTriangleIcon,
            'in-progress': ClockIcon,
            resolved: CheckCircleIcon,
            closed: XCircleIcon
        };

        const IconComponent = statusIcons[status?.toLowerCase()] || ClockIcon;

        return (
            <div className={`flex items-center space-x-1 px-2 py-1 text-xs font-semibold rounded border ${statusStyles[status?.toLowerCase()] || statusStyles.closed}`}>
                <IconComponent className="w-3 h-3" />
                <span>{status?.toUpperCase().replace('-', ' ') || 'UNKNOWN'}</span>
            </div>
        );
    };

    // Fetch incidents
    const fetchIncidents = async () => {
        try {
            setLoading(true);
            const apiBaseUrl = getApiBaseUrl();
            const response = await fetch(`${apiBaseUrl}/api/incidents`, {
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            setIncidents(data);
            
            // Calculate statistics
            const newStats = {
                total: data.length,
                open: data.filter(i => i.status === 'open').length,
                inProgress: data.filter(i => i.status === 'in-progress').length,
                resolved: data.filter(i => i.status === 'resolved').length,
                critical: data.filter(i => i.severity === 'critical').length,
                high: data.filter(i => i.severity === 'high').length,
                medium: data.filter(i => i.severity === 'medium').length,
                low: data.filter(i => i.severity === 'low').length
            };
            setStats(newStats);

        } catch (error) {
            console.error('Error fetching incidents:', error);
            setError('Failed to load incidents');
        } finally {
            setLoading(false);
        }
    };

    // Filter incidents
    useEffect(() => {
        let filtered = incidents;

        if (statusFilter !== 'all') {
            filtered = filtered.filter(incident => 
                incident.status?.toLowerCase() === statusFilter
            );
        }

        if (severityFilter !== 'all') {
            filtered = filtered.filter(incident => 
                incident.severity?.toLowerCase() === severityFilter
            );
        }

        if (searchTerm) {
            filtered = filtered.filter(incident =>
                incident.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                incident.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                incident.id?.toString().includes(searchTerm)
            );
        }

        setFilteredIncidents(filtered);
    }, [incidents, statusFilter, severityFilter, searchTerm]);

    // Initialize data
    useEffect(() => {
        fetchIncidents();
        
        // Set up polling for real-time updates
        const interval = setInterval(fetchIncidents, 30000);
        return () => clearInterval(interval);
    }, []);

    const openIncidentModal = (incident) => {
        setSelectedIncident(incident);
        setShowModal(true);
    };

    const closeModal = () => {
        setShowModal(false);
        setSelectedIncident(null);
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-blue-900 p-6">
                <div className="max-w-7xl mx-auto">
                    <div className="flex items-center justify-center h-64">
                        <div className="text-slate-400">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sky-400 mx-auto mb-4"></div>
                            Loading incidents...
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-blue-900 p-6">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                            <div className="p-3 bg-gradient-to-r from-orange-500/20 to-red-500/20 rounded-lg backdrop-blur-sm border border-orange-500/20">
                                <ExclamationTriangleIcon className="h-8 w-8 text-orange-400" />
                            </div>
                            <div>
                                <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-red-400">
                                    Security Incidents
                                </h1>
                                <p className="text-slate-400 mt-1">
                                    Monitor and manage security incidents
                                </p>
                            </div>
                        </div>
                        
                        <div className="flex items-center space-x-2 text-sm text-slate-400">
                            <div className="flex items-center space-x-2">
                                <div className="w-2 h-2 bg-orange-500 rounded-full animate-pulse"></div>
                                <span>Live Updates</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Statistics Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-lg p-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-slate-400 text-sm">Total Incidents</p>
                                <p className="text-2xl font-bold text-white">{stats.total}</p>
                            </div>
                            <ChartBarIcon className="h-8 w-8 text-slate-400" />
                        </div>
                    </div>
                    
                    <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-lg p-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-slate-400 text-sm">Open</p>
                                <p className="text-2xl font-bold text-red-400">{stats.open}</p>
                            </div>
                            <ExclamationTriangleIcon className="h-8 w-8 text-red-400" />
                        </div>
                    </div>
                    
                    <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-lg p-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-slate-400 text-sm">In Progress</p>
                                <p className="text-2xl font-bold text-orange-400">{stats.inProgress}</p>
                            </div>
                            <ClockIcon className="h-8 w-8 text-orange-400" />
                        </div>
                    </div>
                    
                    <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-lg p-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-slate-400 text-sm">Resolved</p>
                                <p className="text-2xl font-bold text-green-400">{stats.resolved}</p>
                            </div>
                            <CheckCircleIcon className="h-8 w-8 text-green-400" />
                        </div>
                    </div>
                </div>

                {/* Filters */}
                <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-lg p-6 mb-8">
                    <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0 lg:space-x-6">
                        <div className="flex items-center space-x-4">
                            <FunnelIcon className="h-5 w-5 text-slate-400" />
                            <span className="text-slate-300 font-medium">Filters:</span>
                        </div>
                        
                        <div className="flex flex-col lg:flex-row space-y-4 lg:space-y-0 lg:space-x-4 flex-1">
                            {/* Search */}
                            <div className="relative flex-1 max-w-md">
                                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
                                <input
                                    type="text"
                                    placeholder="Search incidents..."
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                    className="pl-10 pr-4 py-2 bg-slate-900/50 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:border-sky-500 focus:ring-1 focus:ring-sky-500 w-full"
                                />
                            </div>
                            
                            {/* Status Filter */}
                            <select
                                value={statusFilter}
                                onChange={(e) => setStatusFilter(e.target.value)}
                                className="px-4 py-2 bg-slate-900/50 border border-slate-600 rounded-lg text-white focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
                            >
                                {statusOptions.map(status => (
                                    <option key={status} value={status} className="bg-slate-900">
                                        {status === 'all' ? 'All Status' : status.toUpperCase().replace('-', ' ')}
                                    </option>
                                ))}
                            </select>
                            
                            {/* Severity Filter */}
                            <select
                                value={severityFilter}
                                onChange={(e) => setSeverityFilter(e.target.value)}
                                className="px-4 py-2 bg-slate-900/50 border border-slate-600 rounded-lg text-white focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
                            >
                                {severityOptions.map(severity => (
                                    <option key={severity} value={severity} className="bg-slate-900">
                                        {severity === 'all' ? 'All Severity' : severity.toUpperCase()}
                                    </option>
                                ))}
                            </select>
                            
                            <button
                                onClick={() => {
                                    setStatusFilter('all');
                                    setSeverityFilter('all');
                                    setSearchTerm('');
                                }}
                                className="px-4 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-slate-300 hover:bg-slate-600/50 transition-colors"
                            >
                                Clear
                            </button>
                        </div>
                    </div>
                </div>

                {/* Incidents Table */}
                <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-lg overflow-hidden">
                    <div className="p-6">
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-xl font-semibold text-white">
                                Security Incidents
                                <span className="ml-3 text-sm text-slate-400">({filteredIncidents.length} of {incidents.length})</span>
                            </h2>
                        </div>
                        
                        {error ? (
                            <div className="text-center py-12">
                                <ExclamationTriangleIcon className="h-12 w-12 text-red-400 mx-auto mb-4" />
                                <p className="text-red-400 mb-2">Error Loading Incidents</p>
                                <p className="text-slate-400 text-sm">{error}</p>
                                <button
                                    onClick={fetchIncidents}
                                    className="mt-4 px-4 py-2 bg-red-600/20 border border-red-500/50 text-red-400 rounded-lg hover:bg-red-500/20 transition-colors"
                                >
                                    Retry
                                </button>
                            </div>
                        ) : filteredIncidents.length > 0 ? (
                            <div className="overflow-x-auto">
                                <table className="w-full">
                                    <thead>
                                        <tr className="border-b border-slate-700">
                                            <th className="text-left py-3 px-4 text-slate-300 font-medium">ID</th>
                                            <th className="text-left py-3 px-4 text-slate-300 font-medium">Title</th>
                                            <th className="text-left py-3 px-4 text-slate-300 font-medium">Status</th>
                                            <th className="text-left py-3 px-4 text-slate-300 font-medium">Severity</th>
                                            <th className="text-left py-3 px-4 text-slate-300 font-medium">Created</th>
                                            <th className="text-left py-3 px-4 text-slate-300 font-medium">Updated</th>
                                            <th className="text-left py-3 px-4 text-slate-300 font-medium">Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {filteredIncidents.map((incident, index) => (
                                            <tr key={incident.id} className={`border-b border-slate-700/50 hover:bg-slate-700/20 transition-colors ${index % 2 === 0 ? 'bg-slate-800/10' : ''}`}>
                                                <td className="py-4 px-4 text-slate-300 font-mono">
                                                    #{incident.id}
                                                </td>
                                                <td className="py-4 px-4">
                                                    <div className="flex flex-col">
                                                        <span className="text-white font-medium truncate max-w-xs">{incident.title}</span>
                                                        {incident.description && (
                                                            <span className="text-slate-400 text-sm truncate max-w-xs mt-1">
                                                                {incident.description}
                                                            </span>
                                                        )}
                                                    </div>
                                                </td>
                                                <td className="py-4 px-4">
                                                    <StatusBadge status={incident.status} />
                                                </td>
                                                <td className="py-4 px-4">
                                                    <SeverityBadge severity={incident.severity} />
                                                </td>
                                                <td className="py-4 px-4 text-slate-400 text-sm">
                                                    {incident.start_time ? new Date(incident.start_time).toLocaleString() : 'N/A'}
                                                </td>
                                                <td className="py-4 px-4 text-slate-400 text-sm">
                                                    {incident.end_time ? new Date(incident.end_time).toLocaleString() : 'N/A'}
                                                </td>
                                                <td className="py-4 px-4">
                                                    <div className="flex items-center space-x-2">
                                                        <button
                                                            onClick={() => openIncidentModal(incident)}
                                                            className="p-2 text-sky-400 hover:text-sky-300 hover:bg-sky-500/10 rounded-lg transition-colors"
                                                            title="View Details"
                                                        >
                                                            <EyeIcon className="h-4 w-4" />
                                                        </button>
                                                        <Link
                                                            to={`/incidents/${incident.id}`}
                                                            className="p-2 text-slate-400 hover:text-slate-300 hover:bg-slate-500/10 rounded-lg transition-colors"
                                                            title="Open Incident"
                                                        >
                                                            <ArrowTopRightOnSquareIcon className="h-4 w-4" />
                                                        </Link>
                                                    </div>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        ) : (
                            <div className="text-center py-12">
                                <CheckCircleIcon className="h-16 w-16 text-slate-600 mx-auto mb-4" />
                                <h3 className="text-lg font-medium text-slate-300 mb-2">No Incidents Found</h3>
                                <p className="text-slate-500">
                                    {searchTerm || statusFilter !== 'all' || severityFilter !== 'all'
                                        ? 'No incidents match your current filters.'
                                        : 'No security incidents have been reported.'}
                                </p>
                            </div>
                        )}
                    </div>
                </div>

                {/* Incident Detail Modal */}
                {showModal && selectedIncident && (
                    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                        <div className="bg-slate-800 border border-slate-700 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
                            <div className="p-6">
                                <div className="flex items-center justify-between mb-6">
                                    <h2 className="text-2xl font-bold text-white">Incident Details</h2>
                                    <button
                                        onClick={closeModal}
                                        className="p-2 text-slate-400 hover:text-slate-300 hover:bg-slate-700 rounded-lg"
                                    >
                                        <XCircleIcon className="h-6 w-6" />
                                    </button>
                                </div>
                                
                                <div className="space-y-6">
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        <div>
                                            <label className="block text-slate-400 text-sm mb-2">Incident ID</label>
                                            <p className="text-white font-mono">#{selectedIncident.id}</p>
                                        </div>
                                        <div>
                                            <label className="block text-slate-400 text-sm mb-2">Status</label>
                                            <StatusBadge status={selectedIncident.status} />
                                        </div>
                                        <div>
                                            <label className="block text-slate-400 text-sm mb-2">Severity</label>
                                            <SeverityBadge severity={selectedIncident.severity} />
                                        </div>
                                        <div>
                                            <label className="block text-slate-400 text-sm mb-2">Created</label>
                                            <p className="text-white">
                                                {selectedIncident.start_time ? new Date(selectedIncident.start_time).toLocaleString() : 'N/A'}
                                            </p>
                                        </div>
                                    </div>
                                    
                                    <div>
                                        <label className="block text-slate-400 text-sm mb-2">Title</label>
                                        <p className="text-white text-lg font-medium">{selectedIncident.title}</p>
                                    </div>
                                    
                                    {selectedIncident.description && (
                                        <div>
                                            <label className="block text-slate-400 text-sm mb-2">Description</label>
                                            <p className="text-slate-300 whitespace-pre-wrap">{selectedIncident.description}</p>
                                        </div>
                                    )}
                                    
                                    <div className="flex justify-end space-x-4 pt-6 border-t border-slate-700">
                                        <button
                                            onClick={closeModal}
                                            className="px-4 py-2 bg-slate-700 text-slate-300 rounded-lg hover:bg-slate-600 transition-colors"
                                        >
                                            Close
                                        </button>
                                        <Link
                                            to={`/incidents/${selectedIncident.id}`}
                                            className="px-4 py-2 bg-sky-600 text-white rounded-lg hover:bg-sky-700 transition-colors flex items-center space-x-2"
                                            onClick={closeModal}
                                        >
                                            <ArrowTopRightOnSquareIcon className="h-4 w-4" />
                                            <span>View Full Details</span>
                                        </Link>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default IncidentsManager;
