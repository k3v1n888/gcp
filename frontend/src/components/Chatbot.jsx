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



import React, { useState } from 'react';

export default function Chatbot({ threatContext }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMessage = { role: 'user', content: input };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInput('');
    setIsLoading(true);

    try {
        const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            threat_context: threatContext,
            history: newMessages
        })
        });
        const aiMessage = await response.json();
        setMessages([...newMessages, aiMessage]);
    } catch (error) {
        const errorMessage = {role: 'assistant', content: 'Sorry, I encountered an error.'}
        setMessages([...newMessages, errorMessage]);
    } finally {
        setIsLoading(false);
    }
  };

  return (
    <div className="bg-gray-50 p-4 rounded-lg shadow-inner">
      <h3 className="font-semibold text-lg mb-2">Ask the AI Analyst</h3>
      <div className="h-64 overflow-y-auto mb-2 border p-2 rounded bg-white flex flex-col">
        {messages.map((msg, index) => (
          <div key={index} className={`my-2 ${msg.role === 'user' ? 'self-end' : 'self-start'}`}>
            <span className={`inline-block p-2 rounded-lg max-w-sm ${msg.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}>
              {msg.content}
            </span>
          </div>
        ))}
         {isLoading && <div className="self-start"><span className="p-2 rounded-lg bg-gray-200">...</span></div>}
      </div>
      <div className="flex">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && !isLoading && handleSend()}
          className="flex-grow border p-2 rounded-l-md"
          placeholder="Ask a follow-up question..."
          disabled={isLoading}
        />
        <button onClick={handleSend} className="bg-blue-600 text-white px-4 rounded-r-md hover:bg-blue-700 disabled:bg-gray-400" disabled={isLoading}>Send</button>
      </div>
    </div>
  );
}
