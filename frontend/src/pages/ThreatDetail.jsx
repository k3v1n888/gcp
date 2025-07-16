import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';

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
      <h1 className="text-3xl font-bold mb-2">{threat.threat}</h1>
      <p className="text-gray-500 mb-6">Detected at {new Date(threat.timestamp).toLocaleString()}</p>

      {threat.recommendations ? (
        <>
          <DetailCard title="AI Analysis: What is this threat?">
            <p>{threat.recommendations.explanation}</p>
          </DetailCard>
          <DetailCard title="AI Analysis: Potential Impact">
            <p>{threat.recommendations.impact}</p>
          </DetailCard>
          <DetailCard title="AI Analysis: Recommended Mitigation Steps">
            <ul className="list-disc list-inside space-y-2">
              {threat.recommendations.mitigation.map((step, index) => (
                <li key={index}>{step}</li>
              ))}
            </ul>
          </DetailCard>
        </>
      ) : (
        <DetailCard title="AI Analysis">
            <p>Could not generate AI recommendations for this threat.</p>
        </DetailCard>
      )}
    </div>
  );
}
