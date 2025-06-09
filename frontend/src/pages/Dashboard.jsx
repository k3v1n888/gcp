// frontend/src/pages/Dashboard.jsx
import { useContext, useEffect, useState } from 'react';
import { UserContext } from '../context/UserContext';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

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
    const socket = new WebSocket(`ws://${window.location.hostname}/ws/threats`);
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
        <table className="min-w-full border text-sm">
          <thead>
            <tr className="bg-gray-200 text-left">
              <th className="px-2 py-1">IP</th>
              <th className="px-2 py-1">Threat</th>
              <th className="px-2 py-1">Source</th>
              <th className="px-2 py-1">Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log, idx) => (
              <tr key={idx} className="border-t">
                <td className="px-2 py-1">{log.ip}</td>
                <td className="px-2 py-1">{log.threat}</td>
                <td className="px-2 py-1">{log.source}</td>
                <td className="px-2 py-1">{new Date(log.timestamp).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
