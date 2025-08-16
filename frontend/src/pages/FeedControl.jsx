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