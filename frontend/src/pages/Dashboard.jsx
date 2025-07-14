// frontend/src/pages/Dashboard.jsx
import { useContext, useEffect, useState } from 'react';
import { UserContext } from '../context/UserContext';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import AISummary from '../components/AISummary';

// --- A helper component for the IP Reputation progress bar ---
const ReputationScore = ({ score }) => {
  const getScoreColor = () => {
    if (score > 75) return 'bg-red-500';
    if (score > 40) return 'bg-orange-500';
    return 'bg-green-500';
  };

  return (
    <div className="w-full bg-gray-200 rounded-full h-2.5 my-1">
      <div
        className={`${getScoreColor()} h-2.5 rounded-full`}
        style={{ width: `${score}%` }}
        title={`AbuseIPDB Score: ${score}`}
      ></div>
    </div>
  );
};

// --- SeverityBadge component remains the same ---
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
    // Fetch initial threat logs
    fetch('/api/threats')
      .then(res => res.json())
      .then(data => setLogs(data));

    // Fetch analytics data
    fetch('/api/analytics/summary')
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
      <AISummary />

      {(user?.role === 'admin' || user?.role === 'analyst') && (
        <div className="mb-6 grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Charts section remains the same */}
        </div>
      )}

      <h2 className="text-lg font-semibold mb-2">Recent Threat Logs</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full border text-sm bg-white shadow-md rounded-lg">
          <thead className="bg-gray-200">
            <tr className="text-left">
              <th className="px-3 py-2">IP</th>
              {/* --- ADD NEW HEADER --- */}
              <th className="px-3 py-2 w-32">IP Reputation</th>
              <th className="px-3 py-2">Threat</th>
              <th className="px-3 py-2">Source</th>
              <th className="px-3 py-2">Severity</th>
              <th className="px-3 py-2">Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log, idx) => (
              <tr key={idx} className="border-t hover:bg-gray-50">
                <td className="px-3 py-2 font-mono">{log.ip}</td>
                {/* --- ADD NEW CELL --- */}
                <td className="px-3 py-2">
                  <ReputationScore score={log.ip_reputation_score} />
                </td>
                <td className="px-3 py-2">{log.threat}</td>
                <td className="px-3 py-2">{log.source}</td>
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
