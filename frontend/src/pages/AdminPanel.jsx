import { useContext, useEffect, useState } from 'react';
import { UserContext } from '../context/UserContext';

const InviteUserForm = () => {
    const [email, setEmail] = useState('');
    const [role, setRole] = useState('viewer');
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage('');
        setError('');

        const response = await fetch('/api/admin/invite', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, role }),
        });

        const data = await response.json();
        if (response.ok) {
            setMessage(data.message);
            setEmail('');
        } else {
            setError(data.detail || 'Failed to send invitation.');
        }
    };

    return (
        <div className="mt-8">
            <h2 className="text-xl font-semibold mb-4 text-sky-400">Invite New User</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label htmlFor="email" className="block text-sm font-medium text-slate-300">User Email</label>
                    <input
                        type="email"
                        id="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                        className="mt-1 block w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-md shadow-sm placeholder-slate-400 focus:outline-none focus:ring-sky-500 focus:border-sky-500 sm:text-sm"
                    />
                </div>
                <div>
                    <label htmlFor="role" className="block text-sm font-medium text-slate-300">Assign Role</label>
                    <select
                        id="role"
                        value={role}
                        onChange={(e) => setRole(e.target.value)}
                        className="mt-1 block w-full pl-3 pr-10 py-2 bg-slate-800 border border-slate-600 rounded-md focus:outline-none focus:ring-sky-500 focus:border-sky-500 sm:text-sm"
                    >
                        <option>viewer</option>
                        <option>analyst</option>
                        <option>admin</option>
                    </select>
                </div>
                <button
                    type="submit"
                    className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-sky-600 hover:bg-sky-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-sky-500"
                >
                    Send Invitation
                </button>
            </form>
            {message && <p className="mt-2 text-green-400">{message}</p>}
            {error && <p className="mt-2 text-red-400">{error}</p>}
        </div>
    );
};

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
    return <p className="text-red-500 p-6">Unauthorized access. Only admins can access this panel.</p>;
  }

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6 text-slate-100">Admin Panel</h1>
      
      <div className="widget-card p-6">
        <h2 className="text-xl font-semibold mb-4 text-sky-400">System Settings</h2>
        <div className="space-y-4">
            <div>
                <label className="block text-sm font-medium text-slate-300">Alert Severity Threshold</label>
                <select value={severity} onChange={(e) => setSeverity(e.target.value)} className="mt-1 block w-full pl-3 pr-10 py-2 bg-slate-800 border border-slate-600 rounded-md focus:outline-none focus:ring-sky-500 focus:border-sky-500 sm:text-sm">
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                </select>
            </div>
            <button
                onClick={handleSubmit}
                className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-sky-600 hover:bg-sky-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-sky-500"
            >
                Save Settings
            </button>
            {message && <p className="mt-2 text-green-400">{message}</p>}
        </div>

        <InviteUserForm />
      </div>
    </div>
  );
}
