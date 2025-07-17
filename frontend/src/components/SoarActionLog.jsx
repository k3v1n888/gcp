// frontend/src/components/SoarActionLog.jsx
import React from 'react';

const ActionStatus = ({ type }) => {
  const isSuccess = type.includes("SUCCESS");
  const color = isSuccess ? 'text-green-400 border-green-400' : 'text-red-400 border-red-400';
  const text = isSuccess ? 'Success' : 'Failure';
  
  return <span className={`border ${color} px-2 py-1 rounded-full text-xs`}>{text}</span>;
};

export default function SoarActionLog({ actions }) {
  if (!actions || actions.length === 0) {
    return <p className="text-gray-400 italic">No automated actions have been taken for this threat.</p>;
  }

  return (
    <div className="space-y-4">
      {actions.map((action, index) => (
        <div key={index} className="flex items-start gap-4">
          <div className="flex-shrink-0">
            <ActionStatus type={action.action_type} />
          </div>
          <div>
            <p className="font-semibold text-gray-300">{action.details}</p>
            <p className="text-xs text-gray-500">{new Date(action.timestamp).toLocaleString()}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
