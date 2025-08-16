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



import { useEffect, useState } from 'react';

export default function ThreatStream() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    const ws = new WebSocket(`ws://${window.location.hostname}/ws/threats`);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setEvents((prev) => [data, ...prev].slice(0, 50)); // keep latest 50 events
    };

    return () => ws.close();
  }, []);

  return (
    <div className="p-2 bg-gray-50 rounded h-64 overflow-y-auto border">
      <h3 className="font-semibold mb-2">Live Threat Stream</h3>
      {events.length === 0 && <p className="text-gray-500">No recent events</p>}
      <ul className="text-xs space-y-1">
        {events.map((evt, i) => (
          <li key={i} className="border-b border-gray-200 pb-1">
            <span className="font-semibold">{evt.threat}</span> from <span>{evt.ip}</span> at {new Date(evt.timestamp).toLocaleTimeString()}
          </li>
        ))}
      </ul>
    </div>
  );
}