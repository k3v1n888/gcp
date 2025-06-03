import { useContext, useEffect, useState } from 'react';
import { UserContext } from '../context/UserContext';

export default function AdminPanel() {
  const { user } = useContext(UserContext);
  const [severity, setSeverity] = useState('critical');
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (user?.role !== 'admin') return;
    fetch('/api/admin/settings')
      .then(res => res.json())
      .then(data => setSeverity(data.alert_severity))
      .catch(() => setMessage('Failed to load settings'));
  }, [user]);

  const handleChange = (e) => setSeverity(e.target.value);

  const handleSubmit = async () => {
    const res = await fetch('/api/admin/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ alert_severity: severity }),
    });
    if (res.ok) setMessage('Settings updated successfully');
    else setMessage('Failed to update settings');
  };

  if (user?.role !== 'admin') {
    return <p className="text-red-500">Unauthorized access. Only admins can access this panel.</p>;
  }

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Admin Panel</h1>
      <label className="block mb-2">Alert Severity Threshold</label>
      <select value={severity} onChange={handleChange} className="border p-2 rounded mb-4">
        <option value="low">Low</option>
        <option value="medium">Medium</option>
        <option value="high">High</option>
        <option value="critical">Critical</option>
      </select>
      <br />
      <button
        onClick={handleSubmit}
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
      >
        Save
      </button>
      {message && <p className="mt-2">{message}</p>}
    </div>
  );
}