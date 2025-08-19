

import React, { useState, useEffect } from 'react';
import { getApiBaseUrl } from '../utils/environment';

export default function AISummary() {
  const [summary, setSummary] = useState('');
  const [systemData, setSystemData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const generateExecutiveSummary = async () => {
      const apiBaseUrl = getApiBaseUrl();
      
      try {
        // Fetch comprehensive system data
        const [threatsRes, agentsRes, auditRes, usersRes, tenantsRes] = await Promise.all([
          fetch(`${apiBaseUrl}/api/threats`).catch(() => null),
          fetch(`${apiBaseUrl}/api/agents`).catch(() => null),
          fetch(`${apiBaseUrl}/api/admin/audit-logs?limit=20`).catch(() => null),
          fetch(`${apiBaseUrl}/api/admin/users`).catch(() => null),
          fetch(`${apiBaseUrl}/api/admin/tenants`).catch(() => null)
        ]);

        const data = {
          threats: threatsRes?.ok ? await threatsRes.json() : { threats: [] },
          agents: agentsRes?.ok ? await agentsRes.json() : { agents: [] },
          audit: auditRes?.ok ? await auditRes.json() : { logs: [] },
          users: usersRes?.ok ? await usersRes.json() : { users: [] },
          tenants: tenantsRes?.ok ? await tenantsRes.json() : { tenants: [] }
        };

        setSystemData(data);

        // Generate AI-powered executive summary
        const executiveSummary = generateAISummary(data);
        setSummary(executiveSummary);

      } catch (err) {
        console.error('Failed to generate executive summary:', err);
        setError(err.message);
        // Fallback summary
        setSummary("System monitoring active. SOC platform operational with enhanced security posture monitoring.");
      } finally {
        setIsLoading(false);
      }
    };

    generateExecutiveSummary();
    
    // Refresh every 15 minutes
    const interval = setInterval(generateExecutiveSummary, 15 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const generateAISummary = (data) => {
    const now = new Date();
    const timeStr = now.toLocaleString();
    
    // Analyze the data
    const threatCount = data.threats?.threats?.length || 0;
    const activeAgents = data.agents?.agents?.filter(a => a.status === 'active')?.length || 0;
    const totalAgents = data.agents?.agents?.length || 0;
    const recentAuditEvents = data.audit?.logs?.length || 0;
    const userCount = data.users?.users?.length || 0;
    const tenantCount = data.tenants?.tenants?.length || 0;
    
    // Calculate security posture
    const agentCoverage = totalAgents > 0 ? (activeAgents / totalAgents * 100).toFixed(1) : 0;
    
    // Analyze recent activity
    const recentAuthEvents = data.audit?.logs?.filter(log => 
      log.action?.includes('auth') || log.action?.includes('login')
    )?.length || 0;
    
    const recentUserManagement = data.audit?.logs?.filter(log => 
      log.action?.includes('user') || log.action?.includes('create')
    )?.length || 0;

    // Generate contextual summary
    let summary = `🤖 **AI Security Analysis - ${timeStr}**\n\n`;
    
    // Overall status
    if (activeAgents === totalAgents && totalAgents > 0) {
      summary += `**System Status: OPTIMAL** - All ${totalAgents} deployed agents are active and monitoring. `;
    } else if (activeAgents > 0) {
      summary += `**System Status: OPERATIONAL** - ${activeAgents}/${totalAgents} agents active (${agentCoverage}% coverage). `;
    } else {
      summary += `**System Status: INITIALIZING** - Agent deployment in progress. `;
    }

    // Threat landscape
    if (threatCount > 0) {
      summary += `Currently tracking ${threatCount} security events across the environment. `;
    }

    // Multi-tenant operations
    if (tenantCount > 1) {
      summary += `Managing security operations across ${tenantCount} tenant environments with ${userCount} authorized users. `;
    } else if (userCount > 1) {
      summary += `Supporting ${userCount} security analysts and administrators. `;
    }

    // Recent activity analysis
    if (recentAuditEvents > 10) {
      summary += `**High Activity Period** - ${recentAuditEvents} administrative actions logged in recent period. `;
    } else if (recentAuditEvents > 0) {
      summary += `Normal operational activity with ${recentAuditEvents} recent administrative actions. `;
    }

    // Authentication security
    if (recentAuthEvents > 5) {
      summary += `⚠️ **Increased Authentication Activity** - ${recentAuthEvents} recent authentication events require monitoring. `;
    } else if (recentAuthEvents > 0) {
      summary += `Authentication systems stable with ${recentAuthEvents} recent login events. `;
    }

    // Recommendations
    summary += `\n\n**AI Recommendations:** `;
    
    if (activeAgents < totalAgents) {
      summary += `Deploy remaining ${totalAgents - activeAgents} agents for complete coverage. `;
    }
    
    if (threatCount === 0) {
      summary += `Continue proactive monitoring and threat hunting activities. `;
    } else {
      summary += `Review and correlate current threat indicators for pattern analysis. `;
    }
    
    if (recentUserManagement > 3) {
      summary += `Recent user management changes detected - verify access controls. `;
    }

    summary += `Maintain regular security posture assessments and ensure all critical systems remain under active monitoring.`;

    return summary;
  };

  const renderContent = () => {
    if (isLoading) {
      return (
        <div className="flex items-center space-x-2">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-sky-400"></div>
          <span className="text-slate-400">AI analyzing security posture...</span>
        </div>
      );
    }
    if (error) {
      return (
        <div className="text-red-400 bg-red-900/20 p-3 rounded border border-red-500/30">
          <p>⚠️ AI Analysis Error: {error}</p>
          <p className="text-sm mt-1">Using fallback analysis mode</p>
        </div>
      );
    }
    return (
      <div className="prose prose-invert max-w-none">
        <div 
          className="text-slate-300 leading-relaxed whitespace-pre-line bg-slate-900/30 p-4 rounded-lg border border-slate-700/50"
          dangerouslySetInnerHTML={{ 
            __html: summary.replace(/\*\*(.*?)\*\*/g, '<strong class="text-sky-400">$1</strong>')
                          .replace(/⚠️/g, '<span class="text-yellow-400">⚠️</span>')
                          .replace(/🤖/g, '<span class="text-purple-400">🤖</span>')
          }}
        />
        {systemData && (
          <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
            <div className="bg-slate-800/50 p-2 rounded">
              <div className="text-slate-400">Active Agents</div>
              <div className="text-sky-400 font-bold">
                {systemData.agents?.agents?.filter(a => a.status === 'active')?.length || 0}
              </div>
            </div>
            <div className="bg-slate-800/50 p-2 rounded">
              <div className="text-slate-400">Recent Events</div>
              <div className="text-sky-400 font-bold">
                {systemData.audit?.logs?.length || 0}
              </div>
            </div>
            <div className="bg-slate-800/50 p-2 rounded">
              <div className="text-slate-400">Users</div>
              <div className="text-sky-400 font-bold">
                {systemData.users?.users?.length || 0}
              </div>
            </div>
            <div className="bg-slate-800/50 p-2 rounded">
              <div className="text-slate-400">Tenants</div>
              <div className="text-sky-400 font-bold">
                {systemData.tenants?.tenants?.length || 0}
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-transparent bg-clip-text bg-gradient-to-r from-sky-400 to-blue-400 flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mr-2 text-sky-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m12.728 0l.707-.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
          🤖 AI-Generated Executive Summary
        </h2>
        <div className="text-xs text-slate-500">
          Auto-refreshes every 15 minutes
        </div>
      </div>
      {renderContent()}
    </div>
  );
}
