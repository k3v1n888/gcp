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



import React, { useState, useEffect } from 'react';
import { getApiBaseUrl } from '../utils/environment';

export default function AISummary() {
  const [summary, setSummary] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const apiBaseUrl = getApiBaseUrl();
    fetch(`${apiBaseUrl}/api/correlation/summary`)
      .then(res => {
        if (!res.ok) {
          throw new Error('Failed to fetch AI summary');
        }
        return res.json();
      })
      .then(data => {
        setSummary(data.summary);
      })
      .catch(err => {
        setError(err.message);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, []);

  const renderContent = () => {
    if (isLoading) {
      return <p className="text-gray-500">Generating AI summary...</p>;
    }
    if (error) {
      return <p className="text-red-500">Error: {error}</p>;
    }
    return (
      <blockquote className="border-l-4 border-blue-500 pl-4">
        <p className="text-gray-700 italic">{summary}</p>
      </blockquote>
    );
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md mb-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mr-2 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m12.728 0l.707-.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
        AI-Generated Executive Summary
      </h2>
      {renderContent()}
    </div>
  );
}
