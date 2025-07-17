import React, { useState } from 'react';

export default function Chatbot({ threatContext }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMessage = { role: 'user', content: input };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInput('');

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
  };

  return (
    <div className="bg-gray-50 p-4 rounded-lg shadow-inner">
      <h3 className="font-semibold text-lg mb-2">Ask the AI Analyst</h3>
      <div className="h-64 overflow-y-auto mb-2 border p-2 rounded bg-white">
        {messages.map((msg, index) => (
          <div key={index} className={`mb-2 ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
            <span className={`inline-block p-2 rounded-lg ${msg.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}>
              {msg.content}
            </span>
          </div>
        ))}
      </div>
      <div className="flex">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          className="flex-grow border p-2 rounded-l-md"
          placeholder="Ask a follow-up question..."
        />
        <button onClick={handleSend} className="bg-blue-600 text-white px-4 rounded-r-md">Send</button>
      </div>
    </div>
  );
}
