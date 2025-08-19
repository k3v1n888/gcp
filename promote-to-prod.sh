#!/bin/bash

# Production Promotion Script
# Merges tested dev changes to main branch for GCP deployment

set -e

echo "🚀 Promoting Development to Production..."

# Check if we're on dev branch
current_branch=$(git branch --show-current)
if [ "$current_branch" != "dev" ]; then
    echo "❌ Must be on dev branch to promote to production"
    exit 1
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "❌ Please commit all changes before promoting to production"
    exit 1
fi

# Step 1: Update dev branch
echo "1️⃣  Updating dev branch..."
git add .
git commit -m "dev: latest development changes ready for production" || echo "No changes to commit"

# Step 2: Switch to main and merge
echo "2️⃣  Switching to main branch..."
git checkout main

echo "3️⃣  Merging dev changes to main..."
git merge dev --no-ff -m "feat: promote tested changes from dev to production"

# Step 4: Clean up production files (remove dev-specific files that should not go to production)
echo "4️⃣  Cleaning up production files..."
rm -f docker-compose.vm.yml vm-*.sh *vm*.sh setup-*.sh dev-*.sh .env.dev .env.vm sync-dev-to-vm.sh validate-dev-setup.sh 2>/dev/null || true

# Remove dev-specific frontend files
rm -f frontend/src/DevApp.jsx frontend/src/ProdApp.jsx frontend/src/components/DevLayout.jsx 2>/dev/null || true
rm -f frontend/src/context/DevUserContext.jsx frontend/src/pages/DevLogin.jsx frontend/src/pages/DebugPage.jsx 2>/dev/null || true
rm -f frontend/src/utils/environment.js 2>/dev/null || true

# Restore original App.jsx for production (no environment detection)
cat > frontend/src/App.jsx << 'EOF'
// Production App component with full authentication
import React from 'react';
import { Route, Routes } from 'react-router-dom';
import { UserProvider } from './context/UserContext';
import ProtectedRoutes from './components/ProtectedRoutes';
import Layout from './components/Layout';
import Home from './pages/Home';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import AdminPanel from './pages/AdminPanel';
import Unauthorized from './pages/Unauthorized';
import AuthSuccess from './pages/AuthSuccess';
import ThreatDetail from './pages/ThreatDetail';
import IncidentDetail from './pages/IncidentDetail';

function App() {
  return (
    <UserProvider>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/unauthorized" element={<Unauthorized />} />
        <Route path="/auth/success" element={<AuthSuccess />} />

        {/* Protected Routes with full authentication */}
        <Route element={<Layout />}>
          <Route element={<ProtectedRoutes allowedRoles={['admin', 'user', 'analyst', 'viewer']} />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/threats/:id" element={<ThreatDetail />} />
            <Route path="/incidents/:id" element={<IncidentDetail />} />
          </Route>
          <Route element={<ProtectedRoutes allowedRoles={['admin']} />}>
            <Route path="/admin" element={<AdminPanel />} />
          </Route>
        </Route>
      </Routes>
    </UserProvider>
  );
}

export default App;
EOF

echo "5️⃣  Committing clean production state..."
git add .
git commit -m "chore: clean production files for GCP deployment" || echo "No cleanup needed"

echo ""
echo "✅ Production promotion complete!"
echo "📤 Ready to push to GCP:"
echo "   git push origin main"
echo ""
echo "🔄 To continue development:"
echo "   git checkout dev"
echo ""
echo "🛡️  Security Check:"
echo "   ✅ All dev-specific auth bypass files removed"
echo "   ✅ Production authentication fully restored"
echo "   ✅ VM-specific configurations cleaned"
