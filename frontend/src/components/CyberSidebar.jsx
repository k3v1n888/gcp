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

import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  CpuChipIcon,
  ShieldCheckIcon,
  ExclamationTriangleIcon,
  DocumentMagnifyingGlassIcon,
  Cog6ToothIcon,
  ChartBarIcon,
  ServerIcon,
  BoltIcon,
  CircleStackIcon,
  UserGroupIcon,
  EyeIcon,
  CommandLineIcon,
  BeakerIcon,
  BuildingOfficeIcon
} from '@heroicons/react/24/outline';

const CyberSidebar = ({ isCollapsed, onToggle }) => {
  const location = useLocation();
  const [systemStats, setSystemStats] = useState({
    threatsActive: 0,
    aiModelsActive: 0,
    connectorsOnline: 0
  });

  useEffect(() => {
    fetchSystemStats();
  }, []);

  const fetchSystemStats = async () => {
    try {
      // Use port 8000 for health endpoints (ingest service) as it has system health monitoring
      const response = await fetch(`${process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8000'}/api/admin/health/system`);
      const data = await response.json();
      setSystemStats({
        threatsActive: data.active_threats || 0,
        aiModelsActive: data.ai_models_active || 3,
        connectorsOnline: data.connectors_online || 4
      });
    } catch (error) {
      console.error('Failed to fetch system stats:', error);
    }
  };

  const navigationItems = [
    {
      category: 'Multi-Tenant Operations',
      items: [
        { name: 'Multi-Tenant Dashboard', href: '/multi-tenant', icon: BuildingOfficeIcon, badge: null, highlight: true }
      ]
    },
    {
      category: 'Intelligence Operations',
      items: [
        { name: 'Threat Dashboard', href: '/threats', icon: ExclamationTriangleIcon, badge: systemStats.threatsActive },
        { name: 'Security Incidents', href: '/incidents', icon: ShieldCheckIcon },
        { name: 'Threat Intelligence', href: '/threat-intel', icon: EyeIcon },
        { name: 'Forensic Analysis', href: '/forensics', icon: DocumentMagnifyingGlassIcon }
      ]
    },
    {
      category: 'AI Command Center',
      items: [
        { name: 'AI Model Management', href: '/ai-models', icon: CpuChipIcon, badge: systemStats.aiModelsActive },
        { name: 'Response Orchestrator', href: '/ai-responses', icon: BoltIcon },
        { name: 'Sentient AI Analytics', href: '/ai-analytics', icon: BeakerIcon },
        { name: 'XAI Explanations', href: '/ai-explanations', icon: ChartBarIcon }
      ]
    },
    {
      category: 'Data Operations',
      items: [
        { name: 'Data Connectors', href: '/data-connectors', icon: CircleStackIcon, badge: systemStats.connectorsOnline },
        { name: 'Log Analysis', href: '/logs', icon: DocumentMagnifyingGlassIcon },
        { name: 'Data Pipeline', href: '/data-pipeline', icon: ServerIcon },
        { name: 'Intelligence Feeds', href: '/intel-feeds', icon: CommandLineIcon }
      ]
    },
    {
      category: 'System Control',
      items: [
        { name: 'Admin Panel', href: '/admin', icon: Cog6ToothIcon },
        { name: 'User Management', href: '/users', icon: UserGroupIcon },
        { name: 'System Health', href: '/health', icon: ServerIcon },
        { name: 'Security Metrics', href: '/metrics', icon: ChartBarIcon }
      ]
    }
  ];

  const isActive = (href) => {
    if (href === '/') return location.pathname === '/';
    return location.pathname.startsWith(href);
  };

  return (
    <div className={`cyber-sidebar ${isCollapsed ? 'collapsed' : 'expanded'} bg-slate-900 border-r border-slate-700 transition-all duration-300 ease-in-out`}>
      <div className="flex flex-col h-full">
        {/* Header */}
        <div className="p-4 border-b border-slate-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <CpuChipIcon className="h-5 w-5 text-white" />
              </div>
              {!isCollapsed && (
                <div>
                  <h1 className="text-lg font-bold text-white">Sentient AI</h1>
                  <p className="text-xs text-slate-400">Security Operations Center</p>
                </div>
              )}
            </div>
            <button
              onClick={onToggle}
              className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors"
            >
              <CommandLineIcon className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* System Status Strip */}
        {!isCollapsed && (
          <div className="p-4 border-b border-slate-700 bg-slate-850">
            <div className="grid grid-cols-3 gap-2 text-xs">
              <div className="text-center">
                <div className="text-red-400 font-bold">{systemStats.threatsActive}</div>
                <div className="text-slate-500">Threats</div>
              </div>
              <div className="text-center">
                <div className="text-green-400 font-bold">{systemStats.aiModelsActive}</div>
                <div className="text-slate-500">AI Models</div>
              </div>
              <div className="text-center">
                <div className="text-blue-400 font-bold">{systemStats.connectorsOnline}</div>
                <div className="text-slate-500">Connectors</div>
              </div>
            </div>
          </div>
        )}

        {/* Navigation */}
        <div className="flex-1 overflow-y-auto p-4">
          <nav className="space-y-6">
            {navigationItems.map((category, categoryIndex) => (
              <div key={categoryIndex}>
                {!isCollapsed && (
                  <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
                    {category.category}
                  </h3>
                )}
                <ul className="space-y-1">
                  {category.items.map((item, itemIndex) => {
                    const Icon = item.icon;
                    const active = isActive(item.href);
                    const isHighlighted = item.highlight;
                    
                    return (
                      <li key={itemIndex}>
                        <Link
                          to={item.href}
                          className={`
                            flex items-center px-3 py-2 rounded-lg transition-all duration-200 group
                            ${active 
                              ? (isHighlighted ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-lg shadow-purple-500/20' : 'bg-blue-600 text-white shadow-lg shadow-blue-500/20')
                              : (isHighlighted ? 'text-slate-300 hover:bg-gradient-to-r hover:from-purple-800 hover:to-blue-800 hover:text-white border border-purple-500/30' : 'text-slate-300 hover:bg-slate-800 hover:text-white')
                            }
                          `}
                        >
                          <Icon className={`
                            h-5 w-5 flex-shrink-0 transition-colors
                            ${active ? 'text-white' : (isHighlighted ? 'text-purple-400 group-hover:text-white' : 'text-slate-400 group-hover:text-white')}
                          `} />
                          
                          {!isCollapsed && (
                            <>
                              <span className="ml-3 font-medium truncate">{item.name}</span>
                              {item.badge !== undefined && item.badge > 0 && (
                                <span className={`
                                  ml-auto px-2 py-1 text-xs rounded-full font-bold
                                  ${active 
                                    ? 'bg-white text-blue-600' 
                                    : 'bg-red-500 text-white'
                                  }
                                `}>
                                  {item.badge}
                                </span>
                              )}
                            </>
                          )}
                        </Link>
                      </li>
                    );
                  })}
                </ul>
              </div>
            ))}
          </nav>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-700">
          <div className="flex items-center justify-between text-xs text-slate-500">
            {!isCollapsed && (
              <>
                <span>v2.1.0</span>
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                  <span>Online</span>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CyberSidebar;
