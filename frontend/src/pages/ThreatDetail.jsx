import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import Chatbot from '../components/Chatbot';
import SoarActionLog from '../components/SoarActionLog';

const SeverityBadge = ({ severity }) => {
  const severityStyles = {
    critical: 'bg-red-600 text-white', high: 'bg-orange-500 text-white',
    medium: 'bg-yellow-400 text-black', low: 'bg-blue-500 text-white',
    unknown: 'bg-gray-500 text-white',
  };
  const severityKey = typeof severity === 'string' ? severity.toLowerCase() : 'unknown';
  return (<span className={`px-2 py-0.5 rounded-full text-xs font-medium ${severityStyles[severityKey] || severityStyles.unknown}`}>{severity}</span>);
};

const ReputationScore = ({ score }) => {
  const numericScore = typeof score === 'number' ? score : 0;
  const getScoreColor = () => {
    if (numericScore > 75) return 'bg-red-500';
    if (numericScore > 40) return 'bg-orange-500';
    return 'bg-green-500';
  };
  return (
    <div className="flex items-center">
      <div className="w-full bg-gray-700 rounded-full h-2.5">
        <div className={`${getScoreColor()} h-2.5 rounded-full`} style={{ width: `${numericScore}%` }} title={`AbuseIPDB Score: ${numericScore}`}></div>
      </div>
      <span className="text-xs font-semibold ml-2 text-gray-400">{numericScore}</span>
    </div>
  );
};

const DetailCard = ({ title, children }) => (
  <div className="widget-card p-6 mb-6">
    <h2 className="text-xl font-semibold mb-4 glow-text">{title}</h2>
    <div className="text-slate-300 leading-relaxed prose prose-invert max-w-none">{children}</div>
  </div>
);

export default function ThreatDetail() {
  const { id } = useParams();
  const [threat, setThreat] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/threats/${id}`).then(res => res.ok ? res.json() : Promise.reject('Failed to load threat details')).then(data => setThreat(data)).catch(console.error).finally(() => setIsLoading(false));
  }, [id]);

  if (isLoading) return <div className="p-6 text-sky-400">Loading Analysis...</div>;
  if (!threat) return <div className="p-6 text-red-500">Error: Threat data could not be loaded.</div>;

  return (
    <div className="p-6">
      <Link to="/dashboard" className="text-sky-400 hover:underline mb-4 inline-block">&larr; Back to Dashboard</Link>
      
      <div className="flex items-center gap-4 mb-2">
        <h1 className="text-3xl font-bold text-slate-100">{threat.threat}</h1>
        {threat.is_anomaly && (<span className="bg-fuchsia-500/20 text-fuchsia-300 border border-fuchsia-400 text-sm font-semibold px-3 py-1 rounded-full">ANOMALY</span>)}
        {threat.source === 'UEBA Engine' && (<span className="bg-amber-500/20 text-amber-300 border border-amber-400 text-sm font-semibold px-3 py-1 rounded-full">INSIDER THREAT</span>)}
      </div>
      <p className="text-slate-400 mb-6">Detected from {threat.source} at {new Date(threat.timestamp).toLocaleString()}</p>
      
      <DetailCard title="Event Telemetry">
        <dl className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-4">
          <div className="py-2"><dt className="font-semibold text-slate-400">Attacker IP</dt><dd className="font-mono text-slate-200">{threat.ip}</dd></div>
          <div className="py-2"><dt className="font-semibold text-slate-400">IP Reputation Score</dt><dd className="mt-1 w-40"><ReputationScore score={threat.ip_reputation_score} /></dd></div>
          <div className="py-2"><dt className="font-semibold text-slate-400">AI-Assigned Severity</dt><dd className="mt-1"><SeverityBadge severity={threat.severity} /></dd></div>
          <div className="py-2"><dt className="font-semibold text-slate-400">Associated CVE</dt><dd className="font-mono text-slate-200">{threat.cve_id ? (<a href={`https://cve.mitre.org/cgi-bin/cvename.cgi?name=${threat.cve_id}`} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">{threat.cve_id}</a>) : ('N/A')}</dd></div>
        </dl>
      </DetailCard>

      {threat.correlation && (
        <DetailCard title="Correlated Threat Analysis">
          <h3 className="font-bold text-lg mb-2">{threat.correlation.title}</h3>
          <p className="mb-2">{threat.correlation.summary}</p>
          <div className="text-sm"><span className="font-semibold">Associated CVE: </span><span className="font-mono">{threat.correlation.cve_id || 'N/A'}</span></div>
        </DetailCard>
      )}

      {threat.recommendations ? (
        <>
          <DetailCard title="Quantum AI Analysis: Threat Explanation"><p>{threat.recommendations.explanation}</p></DetailCard>
          <DetailCard title="Quantum AI Analysis: Potential Impact"><p>{threat.recommendations.impact}</p></DetailCard>
          <DetailCard title="Quantum AI Analysis: Mitigation Protocols"><ul className="list-disc list-inside space-y-2">{threat.recommendations.mitigation.map((step, index) => (<li key={index}>{step}</li>))}</ul></DetailCard>
        </>
      ) : ( <DetailCard title="AI Analysis"><p>Could not generate AI recommendations for this threat.</p></DetailCard> )}

      <DetailCard title="Quantum AI Response">
        <SoarActionLog actions={threat.soar_actions} />
      </DetailCard>
      
      <DetailCard title="Quantum AI Bot">
        <Chatbot threatContext={threat} />
      </DetailCard>
    </div>
  );
}
