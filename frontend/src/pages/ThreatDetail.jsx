// frontend/src/pages/ThreatDetail.jsx
import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import Chatbot from '../components/Chatbot';
import SoarActionLog from '../components/SoarActionLog';
import ModelExplanation from '../components/ModelExplanation'; // Import the component

const SeverityBadge = ({ severity }) => {
    const severityStyles = {
        critical: 'bg-red-600 text-white', high: 'bg-orange-500 text-white',
        medium: 'bg-yellow-400 text-black', low: 'bg-sky-500 text-white',
        unknown: 'bg-slate-500 text-white',
    };
    const severityKey = typeof severity === 'string' ? severity.toLowerCase() : 'unknown';
    return (<span className={`px-2.5 py-1 rounded-full text-xs font-bold ${severityStyles[severityKey] || severityStyles.unknown}`}>{severity.toUpperCase()}</span>);
};

const ReputationScore = ({ score }) => {
    const numericScore = typeof score === 'number' ? score : 0;
    const getScoreColor = () => {
        if (numericScore > 75) return 'bg-red-600';
        if (numericScore > 40) return 'bg-orange-500';
        return 'bg-green-600';
    };
    return (
        <div className="flex items-center">
            <div className="w-full bg-slate-700 rounded-full h-2.5">
                <div className={`${getScoreColor()} h-2.5 rounded-full`} style={{ width: `${numericScore}%` }} title={`MISP Score: ${numericScore}`}></div>
            </div>
            <span className="text-xs font-semibold ml-3 text-slate-300">{numericScore}</span>
        </div>
    );
};

const DetailCard = ({ title, children }) => (
  <div className="widget-card p-6 mb-6">
    <h2 className="text-xl font-semibold mb-4 text-sky-400">{title}</h2>
    <div className="text-slate-300 leading-relaxed prose prose-invert max-w-none">{children}</div>
  </div>
);

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

// --- NEW: Component to visualize the AI's reasoning ---
// const ModelExplanation = ({ explanation }) => {
//     if (!explanation || !explanation.shap_values || !explanation.features) {
//         return <p className="text-slate-400">Explanation data not available for this prediction.</p>;
//     }

//     const FeatureImpact = ({ feature, value, impact }) => {
//         const isPushingHigher = impact > 0;
//         const color = isPushingHigher ? 'text-red-400' : 'text-green-400';
//         const arrow = isPushingHigher ? '↑' : '↓';

//         return (
//             <div className="flex justify-between items-center text-sm p-2 bg-slate-800 rounded">
//                 <span>{feature}: <span className="font-semibold">{String(value)}</span></span>
//                 <span className={`${color} font-bold`}>{arrow} {Math.abs(impact).toFixed(4)}</span>
//             </div>
//         );
//     };

//     // Pair features with their SHAP values for display
//     const featureImpacts = Object.keys(explanation.features).map((key, index) => ({
//         feature: key,
//         value: explanation.features[key],
//         impact: explanation.shap_values[0][index]
//     })).sort((a, b) => Math.abs(b.impact) - Math.abs(a.impact));

//     return (
//         <div className="space-y-2">
//             <p className="text-slate-400 text-sm mb-4">
//                 The model's base prediction value was {explanation.base_value.toFixed(4)}.
//                 The following features had the largest impact on this prediction, either pushing the risk score higher (red arrow) or lower (green arrow).
//             </p>
//             {featureImpacts.slice(0, 5).map(fi => (
//                 <FeatureImpact key={fi.feature} {...fi} />
//             ))}
//         </div>
//     );
// };

export default function ThreatDetail() {
  const { id } = useParams();
  const [threat, setThreat] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/threats/${id}`)
      .then(res => res.ok ? res.json() : Promise.reject('Failed to load threat details'))
      .then(data => {
        // Sanitize the data on the frontend as well
        const sanitizeData = (obj) => {
          if (Array.isArray(obj)) {
            return obj.map(item => sanitizeData(item));
          } else if (obj !== null && typeof obj === 'object') {
            const sanitized = {};
            for (const [key, value] of Object.entries(obj)) {
              if (typeof value === 'number' && (isNaN(value) || !isFinite(value))) {
                sanitized[key] = 0;
              } else {
                sanitized[key] = sanitizeData(value);
              }
            }
            return sanitized;
          }
          return obj;
        };
        
        setThreat(sanitizeData(data));
      })
      .catch(console.error)
      .finally(() => setIsLoading(false));
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
          <div className="py-2"><dt className="font-semibold text-slate-400">IP Reputation Score (from MISP)</dt><dd className="mt-1 w-40"><ReputationScore score={threat.ip_reputation_score} /></dd></div>
          <div className="py-2"><dt className="font-semibold text-slate-400">AI-Assigned Severity</dt><dd className="mt-1"><SeverityBadge severity={threat.severity} /></dd></div>
          <div className="py-2"><dt className="font-semibold text-slate-400">Associated CVE</dt><dd className="font-mono text-slate-200">{threat.cve_id ? (<a href={`https://cve.mitre.org/cgi-bin/cvename.cgi?name=${threat.cve_id}`} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">{threat.cve_id}</a>) : ('N/A')}</dd></div>
        </dl>
      </DetailCard>
      
      {threat.timeline_threats && threat.timeline_threats.length > 1 && (
        <DetailCard title="Attack Timeline">
          <div>
            {threat.timeline_threats.map((log, index, array) => (
              <TimelineItem key={log.id} log={log} isLast={index === array.length - 1} />
            ))}
          </div>
        </DetailCard>
      )}

      {threat.misp_summary && (
        <DetailCard title="Quantum Intel (MISP) Summary">
            <p className="italic text-slate-200">{threat.misp_summary}</p>
        </DetailCard>
      )}

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
      
      {/* --- ADD THIS NEW CARD --- */}
      <DetailCard title="Explainable AI (XAI) Analysis">
        <ModelExplanation 
            explanation={threat.xai_explanation}
            threatId={parseInt(id)}  // Make sure threatId is a number
            existingFeedback={threat.analyst_feedback}
        />
      </DetailCard>
      
      <DetailCard title="Automated Response Log">
        <SoarActionLog actions={threat.soar_actions} />
      </DetailCard>
      
      <DetailCard title="Quantum AI Bot">
        <Chatbot threatContext={threat} />
      </DetailCard>
    </div>
  );
}