import { useContext } from 'react';
import { UserContext } from '../context/UserContext';

export default function FeedControl() {
  const { user } = useContext(UserContext);

  const handleIngest = async () => {
    const res = await fetch('/api/feeds/ingest', { method: 'POST' });
    if (res.ok) alert('Feeds ingested!');
    else alert('Ingestion failed.');
  };

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold mb-4">Threat Feed Control</h1>
      {(user?.role === 'admin' || user?.role === 'analyst') && (
        <button
          onClick={handleIngest}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Ingest Threat Feeds
        </button>
      )}
      {user?.role === 'viewer' && (
        <p className="text-gray-500">View-only access. Contact your admin for elevated permissions.</p>
      )}
    </div>
  );
}