import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import Chatbot from '../components/Chatbot';

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

const ReputationScore = ({ score }) => {
  const numericScore = typeof score === 'number' ? score : 0;
  const getScoreColor = () => {
    if (numericScore > 75) return 'bg-red-500';
    if (numericScore > 40) return 'bg-orange-500';
    return 'bg-green-500';
  };
  return (
    <div className="flex items-center">
      <div className="w-full bg-gray-200 rounded-full h-2.5">
        <div
          className={`${getScoreColor()} h-2.5 rounded-full`}
          style={{ width: `${numericScore === 0 ? 1 : numericScore}%` }}
          title={`AbuseIPDB Score: ${numericScore}`}
        ></div>
      </div>
      <span className="text-xs font-semibold ml-2 text-gray-700">{numericScore}</span>
    </div>
  );
};

const DetailCard = ({ title, children }) => (
  <div className="bg-white p-6 rounded-lg shadow-md mb-6">
    <h2 className="text-xl font-semibold text-gray-800 mb-3">{title}</h2>
    <div className="text-gray-700 leading-relaxed">{children}</div>
  </div>
);

export default function ThreatDetail() {
  const { id } = useParams();
  const [threat, setThreat] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/threats/${id}`)
      .then(res => res.ok ? res.json() : Promise.reject('Failed to load threat details'))
      .then(data => setThreat(data))
      .catch(console.error)
      .finally(() => setIsLoading(false));
  }, [id]);

  if (isLoading) return <div className="p-6">Loading threat analysis...</div>;
  if (!threat) return <div className="p-6 text-red-500">Threat not found or failed to load details.</div>;

  return (
    <div className="p-6">
      <Link to="/dashboard" className="text-blue-600 hover:underline mb-4 inline-block">&larr; Back to Dashboard</Link>
      
      <div className="flex items-center gap-4 mb-2">
        <h1 className="text-3xl font-bold">{threat.threat}</h1>
        {/* --- Anomaly Indicator --- */}
        {threat.is_anomaly && (
            <span className="bg-purple-200 text-purple-800 text-xs font-medium px-2.5 py-1 rounded-full animate-pulse">
                Anomaly Detected
            </span>
        )}
      </div>
      <p className="text-gray-500 mb-6">Detected from {threat.source} at {new Date(threat.timestamp).toLocaleString()}</p>
      
      <DetailCard title="Threat Event Details">
        <dl className="grid grid-cols-1 md:grid-cols-2 gap-x-4 gap-y-2">
          <div className="py-2">
            <dt className="font-medium text-gray-500">Attacker IP</dt>
            <dd className="font-mono text-gray-900">{threat.ip}</dd>
          </div>
          <div className="py-2">
            <dt className="font-medium text-gray-500">IP Reputation</dt>
            <dd className="mt-1 w-32"><ReputationScore score={threat.ip_reputation_score} /></dd>
          </div>
          <div className="py-2">
            <dt className="font-medium text-gray-500">Detected Severity</dt>
            <dd className="mt-1"><SeverityBadge severity={threat.severity} /></dd>
          </div>
          <div className="py-2">
            <dt className="font-medium text-gray-500">Associated CVE</dt>
            <dd className="font-mono text-gray-900">
              {threat.cve_id ? (
                <a 
                  href={`https://cve.mitre.org/cgi-bin/cvename.cgi?name=${threat.cve_id}`} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  {threat.cve_id}
                </a>
              ) : ('N/A')}
            </dd>
          </div>
        </dl>
      </DetailCard>

      {threat.correlation && (
        <DetailCard title="Quantum AI Correlated Threat Analysis">
          <h3 className="font-bold text-lg mb-2">{threat.correlation.title}</h3>
          <p className="mb-2">{threat.correlation.summary}</p>
          <div className="text-sm">
            <span className="font-semibold">Associated CVE: </span>
            <span className="font-mono">{threat.correlation.cve_id || 'N/A'}</span>
          </div>
        </DetailCard>
      )}

      {threat.recommendations ? (
        <>
          <DetailCard title="Quantum AI Analysis: What is this threat?">
            <p>{threat.recommendations.explanation}</p>
          </DetailCard>
          <DetailCard title="Quantum AI Analysis: Potential Impact">
            <p>{threat.recommendations.impact}</p>
          </DetailCard>
          <DetailCard title="Quantum AI Analysis: Recommended Mitigation Steps">
            <ul className="list-disc list-inside space-y-2">
              {threat.recommendations.mitigation.map((step, index) => (
                <li key={index}>{step}</li>
              ))}
            </ul>
          </DetailCard>
        </>
      ) : (
        <DetailCard title="Quantum AI Analysis">
            <p>Could not generate AI recommendations for this threat.</p>
        </DetailCard>
      )}

      {/* --- Chatbot Widget --- */}
      <DetailCard title="Quantum AI Interactive Investigation">
        <Chatbot threatContext={threat} />
      </DetailCard>
    </div>
  );
}
