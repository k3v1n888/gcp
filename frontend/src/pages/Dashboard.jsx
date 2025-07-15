import { useContext, useEffect, useState } from 'react';
import { UserContext } from '../context/UserContext';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
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
      <div className="w-full bg-gray-200 rounded-full h-2.5">
        <div
          className={`${getScoreColor()} h-2.5 rounded-full`}
          style={{ width: `${numericScore === 0 ? 1 : numericScore}%` }}
          title={`AbuseIPDB Score: ${numericScore}`}
        ></div>
      </div>
      <span className="text-xs font-semibold ml-2 text-gray-700">{numericScore}</span>
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
    unknown: 'bg-gray-400 text-white',
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
    // Add a unique timestamp to the URL to bypass any caches
    const cacheBuster = `?_=${new Date().getTime()}`;

    // Fetch initial threat logs with the cache-busting parameter
    fetch(`/api/threats${cacheBuster}`)
      .then(res => res.json())
      .then(data => setLogs(data));

    // Fetch analytics data
    fetch(`/api/analytics/summary${cacheBuster}`)
      .then(res => res.json())
      .then(data => {
        const formattedData = {
          by_type: Object.entries(data.by_type).map(([name, value]) => ({ name, value })),
          by_source: Object.entries(data.by_source).map(([name, value]) => ({ name, value }))
        };
        setAnalytics(formattedData);
      });

    // WebSocket for live updates
    const socket = new WebSocket(`wss://${window.location.hostname}/ws/threats`);
    socket.onmessage = (event) => {
      const newLog = JSON.parse(event.data);
      setLogs((prev) => [newLog, ...prev]);
    };

    return () => socket.close();
  }, []);

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Threat Dashboard</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <AISummary />
        <ThreatForecast />
      </div>

      {(user?.role === 'admin' || user?.role === 'analyst') && (
        <div className="mb-6 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h2 className="text-lg font-semibold">Threats by Type</h2>
            {analytics && (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie data={analytics.by_type} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} fill="#8884d8" label>
                    {analytics.by_type.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
          <div>
            <h2 className="text-lg font-semibold">Threats by Source</h2>
            {analytics && (
               <ResponsiveContainer width="100%" height={300}>
                <BarChart data={analytics.by_source}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="value" fill="#82ca9d" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      )}

      <h2 className="text-lg font-semibold mb-2">Recent Threat Logs</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full border text-sm bg-white shadow-md rounded-lg">
          <thead className="bg-gray-200">
            <tr className="text-left">
              <th className="px-3 py-2">IP</th>
              <th className="px-3 py-2 w-32">IP Reputation</th>
              <th className="px-3 py-2">Threat</th>
              <th className="px-3 py-2">Source</th>
              <th className="px-3 py-2">CVE</th>
              <th className="px-3 py-2">Severity</th>
              <th className="px-3 py-2">Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log, idx) => (
              <tr key={idx} className="border-t hover:bg-gray-50">
                <td className="px-3 py-2 font-mono">{log.ip}</td>
                <td className="px-3 py-2">
                  <ReputationScore score={log.ip_reputation_score} />
                </td>
                <td className="px-3 py-2">{log.threat}</td>
                <td className="px-3 py-2">{log.source}</td>
                <td className="px-3 py-2 font-mono">
                  {log.cve_id ? (
                    <a 
                      href={`https://cve.mitre.org/cgi-bin/cvename.cgi?name=${log.cve_id}`} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline"
                    >
                      {log.cve_id}
                    </a>
                  ) : (
                    'N/A'
                  )}
                </td>
                <td className="px-3 py-2">
                  <SeverityBadge severity={log.severity} />
                </td>
                <td className="px-3 py-2">{new Date(log.timestamp).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
