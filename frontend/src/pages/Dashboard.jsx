import { useContext, useEffect, useState } from 'react';
import { UserContext } from '../context/UserContext';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Link } from 'react-router-dom';
import AISummary from '../components/AISummary';
import ThreatForecast from '../components/ThreatForecast';

// Helper components remain the same, but their styles will be updated by index.css
const ReputationScore = ({ score }) => {
    const numericScore = typeof score === 'number' ? score : 0;
    const getScoreColor = () => {
        if (numericScore > 75) return 'bg-red-600';
        if (numericScore > 40) return 'bg-orange-500';
        return 'bg-green-600';
    };
    return (
        <div className="flex items-center">
            <div className="w-full bg-slate-700 rounded-full h-2.5">
                <div className={`${getScoreColor()} h-2.5 rounded-full`} style={{ width: `${numericScore}%` }} title={`AbuseIPDB Score: ${numericScore}`}></div>
            </div>
            <span className="text-xs font-semibold ml-3 text-slate-300">{numericScore}</span>
        </div>
    );
};

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


export default function Dashboard() {
    const { user } = useContext(UserContext);
    const [logs, setLogs] = useState([]);
    const [analytics, setAnalytics] = useState(null);

    useEffect(() => {
        const cacheBuster = `?_=${new Date().getTime()}`;
        fetch(`/api/threats${cacheBuster}`).then(res => res.json()).then(data => setLogs(data));
        fetch(`/api/analytics/summary${cacheBuster}`).then(res => res.json()).then(data => {
            const formattedData = {
              by_type: Object.entries(data.by_type).map(([name, value]) => ({ name, value })),
              by_source: Object.entries(data.by_source).map(([name, value]) => ({ name, value }))
            };
            setAnalytics(formattedData);
        });
        const socket = new WebSocket(`wss://${window.location.hostname}/ws/threats`);
        socket.onmessage = (event) => {
          const newLog = JSON.parse(event.data);
          setLogs((prev) => [newLog, ...prev]);
        };
        return () => socket.close();
    }, []);

    const COLORS = ['#38bdf8', '#4ade80', '#facc15', '#fb923c', '#f87171'];

    return (
        <div className="p-4 md:p-6">
            <h1 className="text-3xl font-bold mb-6 text-slate-100">Cyber Operations Dashboard</h1>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                <div className="widget-card p-6"><AISummary /></div>
                <div className="widget-card p-6"><ThreatForecast /></div>
            </div>

            {(user?.role === 'admin' || user?.role === 'analyst') && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6 mb-6">
                    <div className="widget-card p-6">
                        <h2 className="text-xl font-semibold mb-4 glow-text">Threats by Type</h2>
                        <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                                <Pie data={analytics?.by_type} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={70} outerRadius={90} fill="#8884d8" paddingAngle={5} labelLine={false}>
                                    {analytics?.by_type.map((entry, index) => (<Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />))}
                                </Pie>
                                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }} itemStyle={{ color: '#e2e8f0' }}/>
                                <Legend />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                    <div className="widget-card p-6">
                        <h2 className="text-xl font-semibold mb-4 glow-text">Threats by Source</h2>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={analytics?.by_source}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                                <XAxis dataKey="name" stroke="#94a3b8" tick={{ fontSize: 12 }} />
                                <YAxis stroke="#94a3b8" />
                                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }} itemStyle={{ color: '#e2e8f0' }}/>
                                <Bar dataKey="value" fill="#38bdf8" fillOpacity={0.8} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            )}

            <div className="col-span-12 widget-card p-6">
                <h2 className="text-xl font-semibold mb-4 glow-text">Live Threat Intel Feed</h2>
                <div className="overflow-x-auto">
                    <table className="cyber-table">
                        <thead>
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
                            {logs.map((log) => (
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
                                    <td>{new Date(log.timestamp).toLocaleString()}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
