import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';

// Helper component for the color-coded severity badges
const SeverityBadge = ({ severity }) => {
    const severityStyles = {
        critical: 'bg-red-600 text-white',
        high: 'bg-orange-500 text-white',
        medium: 'bg-yellow-400 text-black',
        low: 'bg-sky-500 text-white',
        unknown: 'bg-slate-500 text-white',
    };
    const severityKey = typeof severity === 'string' ? severity.toLowerCase() : 'unknown';
    return (<span className={`px-2.5 py-1 rounded-full text-xs font-bold ${severityStyles[severityKey] || severityStyles.unknown}`}>{severity.toUpperCase()}</span>);
};

// Helper component for the main card layout
const DetailCard = ({ title, children }) => (
  <div className="widget-card p-6 mb-6">
    <h2 className="text-xl font-semibold mb-4 text-sky-400">{title}</h2>
    <div className="text-slate-300 leading-relaxed prose prose-invert max-w-none">{children}</div>
  </div>
);

// Helper component to render a single event in the timeline
const TimelineItem = ({ log, isLast }) => {
  const borderColor = isLast ? 'border-transparent' : 'border-slate-600';
  return (
    <div className="relative flex items-start pl-8">
      <div className="absolute left-0 flex flex-col items-center h-full">
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-sky-500 flex items-center justify-center ring-4 ring-slate-800 z-10">
          <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
        </div>
        <div className={`w-px flex-grow ${borderColor}`}></div>
      </div>
      <div className="pb-8 ml-4">
        <p className="text-sm text-slate-400">{new Date(log.timestamp).toLocaleString()}</p>
        <h3 className="font-semibold text-slate-200">{log.threat}</h3>
        <p className="text-sm text-slate-500">Source: {log.source} | IP: {log.ip}</p>
      </div>
    </div>
  );
};

export default function IncidentDetail() {
  const { id } = useParams();
  const [incident, setIncident] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/incidents/${id}`)
      .then(res => res.ok ? res.json() : Promise.reject('Failed to load incident details'))
      .then(data => setIncident(data))
      .catch(console.error)
      .finally(() => setIsLoading(false));
  }, [id]);

  if (isLoading) return <div className="p-6 text-sky-400">Loading Incident Timeline...</div>;
  if (!incident) return <div className="p-6 text-red-500">Error: Incident data could not be loaded.</div>;

  return (
    <div className="p-6">
      <Link to="/dashboard" className="text-sky-400 hover:underline mb-4 inline-block">&larr; Back to Dashboard</Link>
      
      <div className="flex items-center gap-4 mb-2">
          <h1 className="text-3xl font-bold text-slate-100">{incident.title}</h1>
      </div>
      <p className="text-slate-400 mb-6">
        Status: <span className="font-semibold text-orange-400">{incident.status.toUpperCase()}</span> |
        Overall Severity: <SeverityBadge severity={incident.severity} />
      </p>

      <DetailCard title="Attack Storytelling: Timeline of Events">
          <div>
            {incident.threat_logs && incident.threat_logs
                .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
                .map((log, index, array) => (
                <TimelineItem key={log.id} log={log} isLast={index === array.length - 1} />
            ))}
          </div>
      </DetailCard>
    </div>
  );
}