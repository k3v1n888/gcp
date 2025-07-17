import { useContext, useEffect, useState } from 'react';
import { UserContext } from '../context/UserContext';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Link } from 'react-router-dom';
import AISummary from '../components/AISummary';
import ThreatForecast from '../components/ThreatForecast';

// Helper component for the IP Reputation progress bar
const ReputationScore = ({ score }) => {
  const numericScore = typeof score === 'number' ? score : 0;
  const getScoreColor = () => {
    if (numericScore > 75) return 'bg-red-500';
    if (numericScore > 40) return 'bg-orange-500';
    return 'bg-green-500';
  };
  return (
    <div className="flex items-center">
      <div className="w-full bg-gray-700 rounded-full h-2.5">
        <div
          className={`${getScoreColor()} h-2.5 rounded-full`}
          style={{ width: `${numericScore}%` }}
          title={`AbuseIPDB Score: ${numericScore}`}
        ></div>
      </div>
      <span className="text-xs font-semibold ml-2 text-gray-400">{numericScore}</span>
    </div>
  );
};

// Helper component for the color-coded severity badges
const SeverityBadge = ({ severity }) => {
  const severityStyles = {
    critical: 'bg-red-600 text-white',
    high: 'bg-orange-500 text-white',
    medium: 'bg-yellow-400 text-black',
    low: 'bg-blue-500 text-white',
    unknown: 'bg-gray-500 text-white',
  };
  const severityKey = typeof severity === 'string' ? severity.toLowerCase() : 'unknown';
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${severityStyles[severityKey] || severityStyles.unknown}`}>
      {severity}
    </span>
  );
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

    const COLORS = ['#00E5FF', '#00C49F', '#FFBB28', '#FF8042', '#AF1B3F'];

    return (
        <div className="p-4 md:p-6">
            <h1 className="text-3xl font-bold mb-6 glow-text">Cyber Operations Dashboard</h1>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                <div className="widget-card p-4"><AISummary /></div>
                <div className="widget-card p-4"><ThreatForecast /></div>
            </div>

            {(user?.role === 'admin' || user?.role === 'analyst') && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6 mb-6">
                    <div className="widget-card p-4">
                        <h2 className="text-lg font-semibold mb-2 glow-text">Threats by Type</h2>
                        <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                                <Pie data={analytics?.by_type} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={60} outerRadius={80} fill="#8884d8" paddingAngle={5}>
                                    {analytics?.by_type.map((entry, index) => (<Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />))}
                                </Pie>
                                <Tooltip contentStyle={{ backgroundColor: '#0d1117', border: '1px solid #00E5FF' }} itemStyle={{ color: '#c9d1d9' }}/>
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                    <div className="widget-card p-4">
                        <h2 className="text-lg font-semibold mb-2 glow-text">Threats by Source</h2>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={analytics?.by_source}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                                <XAxis dataKey="name" stroke="#8892b0" tick={{ fontSize: 12 }} />
                                <YAxis stroke="#8892b0" />
                                <Tooltip contentStyle={{ backgroundColor: '#0d1117', border: '1px solid #00E5FF' }} itemStyle={{ color: '#c9d1d9' }}/>
                                <Bar dataKey="value" fill="#00E5FF" fillOpacity={0.6} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            )}

            <div className="col-span-12 widget-card p-4">
                <h2 className="text-lg font-semibold mb-2 glow-text">Live Threat Intel Feed</h2>
                <div className="overflow-x-auto">
                    <table className="cyber-table">
                        <thead>
                            <tr>
                                <th>IP</th>
                                <th className="w-32">IP Reputation</th>
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
                                <tr key={log.id} className="hover:bg-cyan-500/10 transition-colors duration-200">
                                    <td className="font-mono">{log.ip}</td>
                                    <td><ReputationScore score={log.ip_reputation_score} /></td>
                                    <td>
                                        <Link to={`/threats/${log.id}`} className="text-cyan-400 hover:underline">
                                            {log.threat}
                                        </Link>
                                    </td>
                                    <td>{log.source}</td>
                                    <td className="font-mono">{log.cve_id || 'N/A'}</td>
                                    <td><SeverityBadge severity={log.severity} /></td>
                                    <td>
                                        {log.is_anomaly && (<span className="text-purple-400 animate-pulse mr-2">Anomaly</span>)}
                                        {log.source === 'UEBA Engine' && (<span className="text-yellow-400 animate-pulse">Insider</span>)}
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
