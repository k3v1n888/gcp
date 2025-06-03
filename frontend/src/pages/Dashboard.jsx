import { useContext, useEffect, useState } from 'react';
import { UserContext } from '../context/UserContext';

export default function Dashboard() {
  const { user } = useContext(UserContext);
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    fetch('/api/threats')
      .then(res => res.json())
      .then(data => setLogs(data));

    const socket = new WebSocket(`ws://${window.location.hostname}/ws/threats`);

    socket.onmessage = (event) => {
      const newLog = JSON.parse(event.data);
      setLogs((prev) => [newLog, ...prev]);
    };

    return () => socket.close();
  }, []);

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Threat Dashboard</h1>

      {(user?.role === 'admin' || user?.role === 'analyst') && (
        <div className="mb-6">
          <h2 className="text-lg font-semibold">Live Threat Analytics</h2>
          <p className="text-sm text-gray-500 mb-2">Streaming real-time threats</p>
          <div className="w-full h-48 bg-gray-100 rounded-lg flex items-center justify-center text-gray-400">
            (Placeholder for analytics visualizations)
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