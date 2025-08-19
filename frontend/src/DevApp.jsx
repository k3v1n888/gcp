// Development-specific App component with auth bypass
import React from 'react';
import { Route, Routes, Link } from 'react-router-dom';
import { DevUserProvider } from './context/DevUserContext';

// Import components
import Dashboard from './pages/Dashboard';
import AdminPanel from './pages/AdminPanel';
import ThreatDetail from './pages/ThreatDetail';
import IncidentDetail from './pages/IncidentDetail';
import DebugPage from './pages/DebugPage';
import DataConnectorManager from './pages/DataConnectorManager';
import AIModelDashboard from './components/AIModelDashboard';
import MultiTenantDashboard from './components/MultiTenantDashboard';

// Simple dev layout without complex dependencies
const SimpleDevLayout = ({ children }) => (
  <div className="flex h-screen bg-slate-900 text-slate-200">
    <div className="w-64 bg-gray-900 flex flex-col">
      <div className="p-4 border-b border-slate-700">
        <h1 className="text-xl font-bold text-sky-400">Sentient AI</h1>
        <p className="text-xs text-yellow-400 mt-1">🔧 Development Mode</p>
      </div>
      <nav className="flex-grow p-2">
        <Link to="/multi-tenant" className="block py-2.5 px-4 rounded hover:bg-slate-800 mb-2 text-purple-400">🏢 Multi-Tenant</Link>
        <Link to="/dashboard" className="block py-2.5 px-4 rounded hover:bg-slate-800 mb-2">Dashboard</Link>
        <Link to="/ai-models" className="block py-2.5 px-4 rounded hover:bg-slate-800 mb-2 text-blue-400">🤖 AI Models</Link>
        <Link to="/connectors" className="block py-2.5 px-4 rounded hover:bg-slate-800 mb-2">🔌 Data Connectors</Link>
        <Link to="/admin" className="block py-2.5 px-4 rounded hover:bg-slate-800 mb-2">Admin Panel</Link>
        <Link to="/debug" className="block py-2.5 px-4 rounded hover:bg-slate-800">Debug</Link>
      </nav>
    </div>
    <div className="flex-1 overflow-auto">
      {children}
    </div>
  </div>
);

function DevApp() {
  console.log('🔧 DevApp rendering...');
  
  return (
    <DevUserProvider>
      <Routes>
        <Route path="/" element={<SimpleDevLayout><Dashboard /></SimpleDevLayout>} />
        <Route path="/debug" element={<SimpleDevLayout><DebugPage /></SimpleDevLayout>} />
        <Route path="/dashboard" element={<SimpleDevLayout><Dashboard /></SimpleDevLayout>} />
        <Route path="/multi-tenant" element={<SimpleDevLayout><MultiTenantDashboard /></SimpleDevLayout>} />
        <Route path="/ai-models" element={<SimpleDevLayout><AIModelDashboard /></SimpleDevLayout>} />
        <Route path="/connectors" element={<SimpleDevLayout><DataConnectorManager /></SimpleDevLayout>} />
        <Route path="/admin" element={<SimpleDevLayout><AdminPanel /></SimpleDevLayout>} />
        <Route path="/threats/:id" element={<SimpleDevLayout><ThreatDetail /></SimpleDevLayout>} />
        <Route path="/incidents/:id" element={<SimpleDevLayout><IncidentDetail /></SimpleDevLayout>} />
      </Routes>
    </DevUserProvider>
  );
}

export default DevApp;
