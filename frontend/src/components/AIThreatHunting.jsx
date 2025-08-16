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

/*
 * Author: Kevin Zachary
 * Copyright: Sentient Spire
 */



import React, { useState, useEffect, useContext } from 'react';
import { UserContext } from '../context/UserContext';
import { useDevUser } from '../context/DevUserContext';
import { isDevelopment, getApiBaseUrl } from '../utils/environment';
import { 
    MagnifyingGlassIcon,
    ShieldExclamationIcon,
    CommandLineIcon,
    EyeIcon,
    ClockIcon,
    ChartBarIcon,
    CpuChipIcon,
    DocumentMagnifyingGlassIcon,
    ArrowPathIcon,
    PlayIcon,
    PauseIcon,
    StopIcon,
    BoltIcon,
    FireIcon
} from '@heroicons/react/24/outline';

const AIThreatHunting = () => {
    // Use appropriate context/hook based on environment
    let user = null;
    
    try {
        if (isDevelopment()) {
            const devContext = useDevUser();
            user = devContext.user;
            console.log('🔧 AIThreatHunting using DevUserContext, user:', user);
        }
    } catch (e) {
        console.log('🔧 DevUserContext not available in AIThreatHunting, falling back');
    }
    
    try {
        if (!isDevelopment()) {
            const prodContext = useContext(UserContext);
            user = prodContext?.user;
            console.log('🔒 AIThreatHunting using UserContext, user:', user);
        }
    } catch (e) {
        console.log('🔒 UserContext not available in AIThreatHunting');
    }

    const [huntingJobs, setHuntingJobs] = useState([]);
    const [activeHunts, setActiveHunts] = useState([]);
    const [huntingResults, setHuntingResults] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isHunting, setIsHunting] = useState(false);
    
    // Query states
    const [huntQuery, setHuntQuery] = useState('');
    const [selectedHuntType, setSelectedHuntType] = useState('behavioral');
    const [timeRange, setTimeRange] = useState('24h');
    const [confidence, setConfidence] = useState(75);
    
    // Modal states
    const [selectedResult, setSelectedResult] = useState(null);
    const [showResultModal, setShowResultModal] = useState(false);
    
    // Statistics
    const [stats, setStats] = useState({
        totalHunts: 0,
        activeHunts: 0,
        threatsFound: 0,
        avgConfidence: 0
    });

    const huntTypes = [
        { value: 'behavioral', label: 'Behavioral Analysis', icon: '🧠' },
        { value: 'anomaly', label: 'Anomaly Detection', icon: '📊' },
        { value: 'ioc', label: 'IOC Hunting', icon: '🔍' },
        { value: 'ml', label: 'ML-Based Detection', icon: '🤖' },
        { value: 'pattern', label: 'Pattern Recognition', icon: '🕸️' }
    ];

    const timeRanges = [
        { value: '1h', label: 'Last Hour' },
        { value: '6h', label: 'Last 6 Hours' },
        { value: '24h', label: 'Last 24 Hours' },
        { value: '7d', label: 'Last 7 Days' },
        { value: '30d', label: 'Last 30 Days' }
    ];

    // Mock hunting templates
    const huntingTemplates = [
        {
            name: 'Suspicious PowerShell Activity',
            query: 'process_name:powershell AND (command_line:*encoded* OR command_line:*hidden*)',
            type: 'behavioral'
        },
        {
            name: 'Lateral Movement Detection',
            query: 'event_type:network AND (destination_port:445 OR destination_port:3389) AND source_ip:internal',
            type: 'behavioral'
        },
        {
            name: 'Privilege Escalation Attempts',
            query: 'event_type:process AND (command_line:*runas* OR command_line:*sudo* OR user_name:admin)',
            type: 'anomaly'
        },
        {
            name: 'Data Exfiltration Patterns',
            query: 'event_type:network AND bytes_out:>1000000 AND destination_ip:external',
            type: 'pattern'
        }
    ];

    // Helper components
    const ConfidenceBadge = ({ confidence }) => {
        const getConfidenceColor = () => {
            if (confidence >= 90) return 'bg-red-600 text-white border-red-500';
            if (confidence >= 75) return 'bg-orange-500 text-white border-orange-400';
            if (confidence >= 50) return 'bg-yellow-400 text-black border-yellow-300';
            return 'bg-green-600 text-white border-green-500';
        };

        return (
            <span className={`px-2 py-1 text-xs font-semibold rounded border ${getConfidenceColor()}`}>
                {confidence}%
            </span>
        );
    };

    const HuntStatusBadge = ({ status }) => {
        const statusStyles = {
            running: 'bg-green-600 text-white border-green-500',
            completed: 'bg-blue-600 text-white border-blue-500',
            failed: 'bg-red-600 text-white border-red-500',
            queued: 'bg-yellow-600 text-black border-yellow-500'
        };

        return (
            <span className={`px-2 py-1 text-xs font-semibold rounded border ${statusStyles[status] || statusStyles.queued}`}>
                {status?.toUpperCase() || 'UNKNOWN'}
            </span>
        );
    };

    // Fetch hunting data
    const fetchHuntingData = async () => {
        try {
            setLoading(true);
            
            // Mock API calls - replace with real endpoints
            const mockData = {
                huntingJobs: [
                    {
                        id: 'hunt_001',
                        name: 'PowerShell Anomaly Hunt',
                        type: 'behavioral',
                        status: 'running',
                        confidence: 85,
                        startTime: new Date(Date.now() - 3600000).toISOString(),
                        endTime: null,
                        progress: 65
                    },
                    {
                        id: 'hunt_002',
                        name: 'IOC Match Hunt',
                        type: 'ioc',
                        status: 'completed',
                        confidence: 92,
                        startTime: new Date(Date.now() - 7200000).toISOString(),
                        endTime: new Date(Date.now() - 3600000).toISOString(),
                        progress: 100
                    }
                ],
                results: [
                    {
                        id: 'result_001',
                        huntId: 'hunt_002',
                        title: 'Suspicious File Hash Detected',
                        confidence: 92,
                        severity: 'high',
                        timestamp: new Date(Date.now() - 1800000).toISOString(),
                        details: {
                            file_hash: 'a1b2c3d4e5f6...',
                            file_path: 'C:\\Windows\\Temp\\suspicious.exe',
                            process_id: '1234',
                            user: 'system'
                        }
                    },
                    {
                        id: 'result_002',
                        huntId: 'hunt_001',
                        title: 'Encoded PowerShell Command',
                        confidence: 78,
                        severity: 'medium',
                        timestamp: new Date(Date.now() - 2700000).toISOString(),
                        details: {
                            command: 'powershell.exe -EncodedCommand ...',
                            user: 'user123',
                            process_id: '5678'
                        }
                    }
                ]
            };
            
            setHuntingJobs(mockData.huntingJobs);
            setHuntingResults(mockData.results);
            setActiveHunts(mockData.huntingJobs.filter(job => job.status === 'running'));
            
            // Calculate stats
            const newStats = {
                totalHunts: mockData.huntingJobs.length,
                activeHunts: mockData.huntingJobs.filter(job => job.status === 'running').length,
                threatsFound: mockData.results.length,
                avgConfidence: Math.round(mockData.results.reduce((acc, r) => acc + r.confidence, 0) / mockData.results.length) || 0
            };
            setStats(newStats);
            
        } catch (error) {
            console.error('Error fetching hunting data:', error);
        } finally {
            setLoading(false);
        }
    };

    // Start hunting job
    const startHunt = async () => {
        if (!huntQuery.trim()) return;
        
        setIsHunting(true);
        
        // Mock API call
        setTimeout(() => {
            const newHunt = {
                id: `hunt_${Date.now()}`,
                name: `Custom Hunt - ${selectedHuntType}`,
                type: selectedHuntType,
                status: 'running',
                confidence: confidence,
                startTime: new Date().toISOString(),
                endTime: null,
                progress: 0,
                query: huntQuery
            };
            
            setHuntingJobs(prev => [newHunt, ...prev]);
            setActiveHunts(prev => [newHunt, ...prev]);
            setIsHunting(false);
            setHuntQuery('');
        }, 2000);
    };

    // Initialize data
    useEffect(() => {
        fetchHuntingData();
        
        // Set up polling for updates
        const interval = setInterval(fetchHuntingData, 15000);
        return () => clearInterval(interval);
    }, []);

    const openResultModal = (result) => {
        setSelectedResult(result);
        setShowResultModal(true);
    };

    const closeResultModal = () => {
        setShowResultModal(false);
        setSelectedResult(null);
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-blue-900 p-6">
                <div className="max-w-7xl mx-auto">
                    <div className="flex items-center justify-center h-64">
                        <div className="text-slate-400">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-400 mx-auto mb-4"></div>
                            Loading threat hunting data...
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-blue-900 p-6">
            <div className="max-w-7xl mx-auto space-y-8">
                {/* Header */}
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                        <div className="p-3 bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-lg backdrop-blur-sm border border-purple-500/20">
                            <MagnifyingGlassIcon className="h-8 w-8 text-purple-400" />
                        </div>
                        <div>
                            <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">
                                AI Threat Hunting
                            </h1>
                            <p className="text-slate-400 mt-1">
                                Advanced threat detection and hunting platform
                            </p>
                        </div>
                    </div>
                    
                    <div className="flex items-center space-x-4">
                        <button
                            onClick={fetchHuntingData}
                            className="p-2 text-slate-400 hover:text-slate-300 hover:bg-slate-700/50 rounded-lg transition-colors"
                            title="Refresh"
                        >
                            <ArrowPathIcon className="h-5 w-5" />
                        </button>
                        <div className="flex items-center space-x-2 text-sm text-slate-400">
                            <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse"></div>
                            <span>AI Powered</span>
                        </div>
                    </div>
                </div>

                {/* Statistics */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-lg p-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-slate-400 text-sm">Total Hunts</p>
                                <p className="text-2xl font-bold text-white">{stats.totalHunts}</p>
                            </div>
                            <ChartBarIcon className="h-8 w-8 text-purple-400" />
                        </div>
                    </div>
                    
                    <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-lg p-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-slate-400 text-sm">Active Hunts</p>
                                <p className="text-2xl font-bold text-green-400">{stats.activeHunts}</p>
                            </div>
                            <PlayIcon className="h-8 w-8 text-green-400" />
                        </div>
                    </div>
                    
                    <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-lg p-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-slate-400 text-sm">Threats Found</p>
                                <p className="text-2xl font-bold text-red-400">{stats.threatsFound}</p>
                            </div>
                            <FireIcon className="h-8 w-8 text-red-400" />
                        </div>
                    </div>
                    
                    <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-lg p-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-slate-400 text-sm">Avg Confidence</p>
                                <p className="text-2xl font-bold text-yellow-400">{stats.avgConfidence}%</p>
                            </div>
                            <CpuChipIcon className="h-8 w-8 text-yellow-400" />
                        </div>
                    </div>
                </div>

                {/* Hunt Creation Panel */}
                <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-lg p-6">
                    <div className="flex items-center space-x-3 mb-6">
                        <CommandLineIcon className="h-6 w-6 text-purple-400" />
                        <h2 className="text-xl font-semibold text-white">Create New Hunt</h2>
                    </div>
                    
                    <div className="space-y-6">
                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                            <div>
                                <label className="block text-slate-400 text-sm mb-2">Hunt Type</label>
                                <select
                                    value={selectedHuntType}
                                    onChange={(e) => setSelectedHuntType(e.target.value)}
                                    className="w-full px-4 py-2 bg-slate-900/50 border border-slate-600 rounded-lg text-white focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
                                >
                                    {huntTypes.map(type => (
                                        <option key={type.value} value={type.value} className="bg-slate-900">
                                            {type.icon} {type.label}
                                        </option>
                                    ))}
                                </select>
                            </div>
                            
                            <div>
                                <label className="block text-slate-400 text-sm mb-2">Time Range</label>
                                <select
                                    value={timeRange}
                                    onChange={(e) => setTimeRange(e.target.value)}
                                    className="w-full px-4 py-2 bg-slate-900/50 border border-slate-600 rounded-lg text-white focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
                                >
                                    {timeRanges.map(range => (
                                        <option key={range.value} value={range.value} className="bg-slate-900">
                                            {range.label}
                                        </option>
                                    ))}
                                </select>
                            </div>
                            
                            <div>
                                <label className="block text-slate-400 text-sm mb-2">Min Confidence: {confidence}%</label>
                                <input
                                    type="range"
                                    min="1"
                                    max="100"
                                    value={confidence}
                                    onChange={(e) => setConfidence(parseInt(e.target.value))}
                                    className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer slider"
                                />
                            </div>
                        </div>
                        
                        <div>
                            <label className="block text-slate-400 text-sm mb-2">Hunt Query</label>
                            <div className="relative">
                                <textarea
                                    value={huntQuery}
                                    onChange={(e) => setHuntQuery(e.target.value)}
                                    placeholder="Enter your threat hunting query or select a template below..."
                                    rows={3}
                                    className="w-full px-4 py-3 bg-slate-900/50 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:border-purple-500 focus:ring-1 focus:ring-purple-500 font-mono text-sm"
                                />
                                <button
                                    onClick={startHunt}
                                    disabled={!huntQuery.trim() || isHunting}
                                    className="absolute bottom-3 right-3 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-slate-600 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
                                >
                                    {isHunting ? (
                                        <>
                                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                                            <span>Starting...</span>
                                        </>
                                    ) : (
                                        <>
                                            <BoltIcon className="h-4 w-4" />
                                            <span>Start Hunt</span>
                                        </>
                                    )}
                                </button>
                            </div>
                        </div>
                        
                        {/* Templates */}
                        <div>
                            <label className="block text-slate-400 text-sm mb-3">Quick Templates</label>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                {huntingTemplates.map((template, index) => (
                                    <button
                                        key={index}
                                        onClick={() => setHuntQuery(template.query)}
                                        className="p-3 bg-slate-900/30 border border-slate-600/50 rounded-lg text-left hover:bg-slate-700/30 transition-colors"
                                    >
                                        <div className="flex items-center justify-between mb-1">
                                            <span className="text-white text-sm font-medium">{template.name}</span>
                                            <span className="text-xs text-slate-400 bg-slate-700 px-2 py-1 rounded">{template.type}</span>
                                        </div>
                                        <code className="text-xs text-slate-400 font-mono truncate block">{template.query}</code>
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Active Hunts */}
                {activeHunts.length > 0 && (
                    <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-lg p-6">
                        <div className="flex items-center justify-between mb-6">
                            <div className="flex items-center space-x-3">
                                <PlayIcon className="h-6 w-6 text-green-400" />
                                <h2 className="text-xl font-semibold text-white">Active Hunts</h2>
                            </div>
                            <span className="text-sm text-slate-400">({activeHunts.length} running)</span>
                        </div>
                        
                        <div className="space-y-4">
                            {activeHunts.map(hunt => (
                                <div key={hunt.id} className="bg-slate-900/30 border border-slate-600/50 rounded-lg p-4">
                                    <div className="flex items-center justify-between mb-3">
                                        <div className="flex items-center space-x-3">
                                            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                                            <span className="text-white font-medium">{hunt.name}</span>
                                        </div>
                                        <HuntStatusBadge status={hunt.status} />
                                    </div>
                                    
                                    <div className="flex items-center justify-between text-sm text-slate-400">
                                        <span>Started: {new Date(hunt.startTime).toLocaleString()}</span>
                                        <span>Progress: {hunt.progress}%</span>
                                    </div>
                                    
                                    <div className="mt-3">
                                        <div className="w-full bg-slate-700 rounded-full h-2">
                                            <div 
                                                className="bg-green-600 h-2 rounded-full transition-all duration-1000" 
                                                style={{ width: `${hunt.progress}%` }}
                                            />
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Hunting Results */}
                <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-lg p-6">
                    <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center space-x-3">
                            <DocumentMagnifyingGlassIcon className="h-6 w-6 text-red-400" />
                            <h2 className="text-xl font-semibold text-white">Hunting Results</h2>
                        </div>
                        <span className="text-sm text-slate-400">({huntingResults.length} found)</span>
                    </div>
                    
                    {huntingResults.length > 0 ? (
                        <div className="space-y-4">
                            {huntingResults.map(result => (
                                <div key={result.id} className="bg-slate-900/30 border border-slate-600/50 rounded-lg p-4 hover:bg-slate-700/20 transition-colors cursor-pointer"
                                     onClick={() => openResultModal(result)}>
                                    <div className="flex items-start justify-between">
                                        <div className="flex-1">
                                            <div className="flex items-center space-x-3 mb-2">
                                                <h3 className="text-white font-medium">{result.title}</h3>
                                                <ConfidenceBadge confidence={result.confidence} />
                                            </div>
                                            <div className="text-sm text-slate-400 space-y-1">
                                                <p>Hunt ID: {result.huntId}</p>
                                                <p>Detected: {new Date(result.timestamp).toLocaleString()}</p>
                                            </div>
                                        </div>
                                        <EyeIcon className="h-5 w-5 text-slate-400" />
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-12">
                            <ShieldExclamationIcon className="h-16 w-16 text-slate-600 mx-auto mb-4" />
                            <h3 className="text-lg font-medium text-slate-300 mb-2">No Results Found</h3>
                            <p className="text-slate-500">Start a new hunt to detect potential threats</p>
                        </div>
                    )}
                </div>

                {/* Result Detail Modal */}
                {showResultModal && selectedResult && (
                    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                        <div className="bg-slate-800 border border-slate-700 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
                            <div className="p-6">
                                <div className="flex items-center justify-between mb-6">
                                    <h2 className="text-2xl font-bold text-white">Threat Detection Result</h2>
                                    <button
                                        onClick={closeResultModal}
                                        className="p-2 text-slate-400 hover:text-slate-300 hover:bg-slate-700 rounded-lg"
                                    >
                                        ✕
                                    </button>
                                </div>
                                
                                <div className="space-y-6">
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        <div>
                                            <label className="block text-slate-400 text-sm mb-2">Detection Title</label>
                                            <p className="text-white text-lg font-medium">{selectedResult.title}</p>
                                        </div>
                                        <div>
                                            <label className="block text-slate-400 text-sm mb-2">Confidence Score</label>
                                            <ConfidenceBadge confidence={selectedResult.confidence} />
                                        </div>
                                        <div>
                                            <label className="block text-slate-400 text-sm mb-2">Hunt ID</label>
                                            <p className="text-white font-mono">{selectedResult.huntId}</p>
                                        </div>
                                        <div>
                                            <label className="block text-slate-400 text-sm mb-2">Detection Time</label>
                                            <p className="text-white">{new Date(selectedResult.timestamp).toLocaleString()}</p>
                                        </div>
                                    </div>
                                    
                                    <div>
                                        <label className="block text-slate-400 text-sm mb-2">Detection Details</label>
                                        <div className="bg-slate-900/50 rounded-lg p-4">
                                            <pre className="text-slate-300 text-sm overflow-x-auto">
                                                {JSON.stringify(selectedResult.details, null, 2)}
                                            </pre>
                                        </div>
                                    </div>
                                    
                                    <div className="flex justify-end space-x-4 pt-6 border-t border-slate-700">
                                        <button
                                            onClick={closeResultModal}
                                            className="px-4 py-2 bg-slate-700 text-slate-300 rounded-lg hover:bg-slate-600 transition-colors"
                                        >
                                            Close
                                        </button>
                                        <button className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors">
                                            Create Incident
                                        </button>
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

export default AIThreatHunting;
