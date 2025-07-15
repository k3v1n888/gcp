import React, { useState, useEffect } from 'react';

export default function ThreatForecast() {
  const [forecast, setForecast] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetch('/api/forecasting/24_hour')
      .then(res => res.json())
      .then(data => {
        setForecast(data);
      })
      .catch(() => {
        setForecast({ error: 'Failed to load forecast' });
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, []);

  const renderContent = () => {
    if (isLoading) {
      return <p className="text-sm text-gray-500">Generating 24-hour forecast...</p>;
    }
    if (forecast?.error || !forecast?.predicted_threats) {
      return <p className="text-sm text-red-500">{forecast?.error || 'No forecast data available.'}</p>;
    }
    if (Object.keys(forecast.predicted_threats).length === 0) {
        return <p className="text-sm text-gray-500">No significant threats predicted in the next 24 hours.</p>;
    }
    return (
      <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
        {Object.entries(forecast.predicted_threats).map(([threat, score]) => (
          <li key={threat}>
            <span className="font-medium">{threat}</span>
          </li>
        ))}
      </ul>
    );
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md mb-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mr-2 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
        </svg>
        Predicted Threats (Next 24 Hours)
      </h2>
      {renderContent()}
    </div>
  );
}
