#!/bin/bash
# Copyright (c) 2025 Kevin Zachary
# All rights reserved.
#
# This software and associated documentation files (the "Software") are the 
# exclusive property of Kevin Zachary. Unauthorized copying, distribution, 
# modification, or use of this software is strictly prohibited.
#
# For licensing inquiries, contact: kevin@zachary.com

#!/bin/bash
# Author: Kevin Zachary
# Copyright: Sentient Spire


# CXyber AI SOC - Theme & UI Contrast Fix Script
# Addresses white background and visibility issues

echo "🎨 CXyber AI SOC - Theme & UI Contrast Fix"
echo "=========================================="

# Create a comprehensive CSS override file for better contrast
cat > /Users/kevinzachary/Downloads/VS-GCP-QAI/gcp/frontend/src/styles/theme-fixes.css << 'EOF'
/* CXyber AI SOC - Theme Contrast Fixes */

/* Global dark theme enforcement */
* {
  color-scheme: dark;
}

/* Ensure all backgrounds are dark */
body, html, #root {
  background: #0f172a !important;
  color: #e2e8f0 !important;
}

/* Fix white backgrounds in AI models and health check interfaces */
.bg-white {
  background: #1e293b !important;
  color: #e2e8f0 !important;
}

/* Card components with proper dark theme */
.card, .widget-card {
  background: #1e293b !important;
  border: 1px solid #334155 !important;
  color: #e2e8f0 !important;
}

/* Button fixes for better visibility */
.btn-primary {
  background: #3b82f6 !important;
  border-color: #3b82f6 !important;
  color: white !important;
}

.btn-secondary {
  background: #64748b !important;
  border-color: #64748b !important;
  color: white !important;
}

.btn-outline {
  background: transparent !important;
  border: 1px solid #64748b !important;
  color: #e2e8f0 !important;
}

.btn-outline:hover {
  background: #64748b !important;
  color: white !important;
}

/* Input field fixes */
input, textarea, select {
  background: #334155 !important;
  border: 1px solid #475569 !important;
  color: #e2e8f0 !important;
}

input:focus, textarea:focus, select:focus {
  background: #475569 !important;
  border-color: #3b82f6 !important;
  outline: none !important;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3) !important;
}

/* Table fixes */
table {
  background: #1e293b !important;
  color: #e2e8f0 !important;
}

th {
  background: #334155 !important;
  color: #f1f5f9 !important;
  border-bottom: 2px solid #475569 !important;
}

td {
  border-bottom: 1px solid #334155 !important;
  color: #e2e8f0 !important;
}

tr:hover {
  background: #334155 !important;
}

/* Modal and dropdown fixes */
.modal, .dropdown-menu, .popover {
  background: #1e293b !important;
  border: 1px solid #334155 !important;
  color: #e2e8f0 !important;
}

.modal-header, .modal-footer {
  border-color: #334155 !important;
}

/* Alert fixes */
.alert {
  background: #1e293b !important;
  border: 1px solid #334155 !important;
  color: #e2e8f0 !important;
}

.alert-success {
  background: #064e3b !important;
  border-color: #065f46 !important;
  color: #a7f3d0 !important;
}

.alert-warning {
  background: #78350f !important;
  border-color: #92400e !important;
  color: #fde68a !important;
}

.alert-danger {
  background: #7f1d1d !important;
  border-color: #991b1b !important;
  color: #fca5a5 !important;
}

.alert-info {
  background: #1e3a8a !important;
  border-color: #1d4ed8 !important;
  color: #bfdbfe !important;
}

/* Badge fixes */
.badge {
  background: #374151 !important;
  color: #f9fafb !important;
}

.badge-success {
  background: #059669 !important;
}

.badge-warning {
  background: #d97706 !important;
}

.badge-danger {
  background: #dc2626 !important;
}

.badge-info {
  background: #2563eb !important;
}

/* Progress bar fixes */
.progress {
  background: #374151 !important;
}

.progress-bar {
  background: #3b82f6 !important;
}

/* Tooltip fixes */
.tooltip {
  background: #1f2937 !important;
  color: #f9fafb !important;
  border: 1px solid #374151 !important;
}

/* Code and pre fixes */
code, pre {
  background: #1f2937 !important;
  color: #f9fafb !important;
  border: 1px solid #374151 !important;
}

/* Navigation fixes */
.nav, .navbar {
  background: #1e293b !important;
  border-color: #334155 !important;
}

.nav-link {
  color: #e2e8f0 !important;
}

.nav-link:hover, .nav-link.active {
  color: #60a5fa !important;
  background: #334155 !important;
}

/* Form control fixes */
.form-control {
  background: #334155 !important;
  border: 1px solid #475569 !important;
  color: #e2e8f0 !important;
}

.form-control:focus {
  background: #475569 !important;
  border-color: #3b82f6 !important;
  box-shadow: 0 0 0 0.2rem rgba(59, 130, 246, 0.25) !important;
}

/* Sidebar fixes */
.sidebar {
  background: #1e293b !important;
  border-color: #334155 !important;
}

/* List group fixes */
.list-group-item {
  background: #1e293b !important;
  border-color: #334155 !important;
  color: #e2e8f0 !important;
}

.list-group-item:hover {
  background: #334155 !important;
}

/* Tab fixes */
.tab-content {
  background: #1e293b !important;
}

.tab-pane {
  color: #e2e8f0 !important;
}

/* Accordion fixes */
.accordion-item {
  background: #1e293b !important;
  border-color: #334155 !important;
}

.accordion-button {
  background: #334155 !important;
  color: #e2e8f0 !important;
  border-color: #334155 !important;
}

.accordion-button:not(.collapsed) {
  background: #475569 !important;
  color: #f1f5f9 !important;
}

/* Pagination fixes */
.page-link {
  background: #1e293b !important;
  border-color: #334155 !important;
  color: #e2e8f0 !important;
}

.page-link:hover {
  background: #334155 !important;
  border-color: #475569 !important;
  color: #f1f5f9 !important;
}

.page-item.active .page-link {
  background: #3b82f6 !important;
  border-color: #3b82f6 !important;
}

/* Scrollbar fixes */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #1e293b;
}

::-webkit-scrollbar-thumb {
  background: #475569;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #64748b;
}

/* Override any remaining white backgrounds */
div[style*="background: white"],
div[style*="background-color: white"],
div[class*="bg-white"],
.white-bg,
.light-theme {
  background: #1e293b !important;
  color: #e2e8f0 !important;
}

/* Ensure text visibility */
.text-dark {
  color: #e2e8f0 !important;
}

.text-muted {
  color: #94a3b8 !important;
}

/* Chart and graph fixes */
.chart-container, .graph-container {
  background: #1e293b !important;
}

/* AI Model specific fixes */
.ai-model-card, .model-performance-card {
  background: #1e293b !important;
  border: 1px solid #334155 !important;
  color: #e2e8f0 !important;
}

/* Health check interface fixes */
.health-status-card, .system-metrics-card {
  background: #1e293b !important;
  border: 1px solid #334155 !important;
  color: #e2e8f0 !important;
}

/* Data connector fixes */
.connector-status-card {
  background: #1e293b !important;
  border: 1px solid #334155 !important;
  color: #e2e8f0 !important;
}

/* Response orchestrator fixes */
.orchestrator-card, .response-suggestion-card {
  background: #1e293b !important;
  border: 1px solid #334155 !important;
  color: #e2e8f0 !important;
}

/* Loading spinner fixes */
.spinner, .loading {
  color: #3b82f6 !important;
}

/* Icon fixes */
.icon {
  color: #94a3b8 !important;
}

.icon-success {
  color: #10b981 !important;
}

.icon-warning {
  color: #f59e0b !important;
}

.icon-danger {
  color: #ef4444 !important;
}

.icon-info {
  color: #3b82f6 !important;
}
EOF

echo "✅ Created comprehensive theme fixes CSS file"

# Update the main CSS file to import our fixes
if ! grep -q "theme-fixes.css" /Users/kevinzachary/Downloads/VS-GCP-QAI/gcp/frontend/src/index.css; then
    echo '@import "./styles/theme-fixes.css";' >> /Users/kevinzachary/Downloads/VS-GCP-QAI/gcp/frontend/src/index.css
    echo "✅ Added theme fixes import to main CSS"
fi

# Create directory for styles if it doesn't exist
mkdir -p /Users/kevinzachary/Downloads/VS-GCP-QAI/gcp/frontend/src/styles

echo "✅ Theme contrast fixes applied!"
echo ""
echo "🎨 Theme Fixes Summary:"
echo "- ✅ Fixed white background issues"
echo "- ✅ Improved text contrast and visibility"
echo "- ✅ Enhanced button and input styling"
echo "- ✅ Fixed AI model interface contrast"
echo "- ✅ Improved health check interface visibility"
echo "- ✅ Enhanced data connector styling"
echo "- ✅ Fixed modal and dropdown contrast"
echo "- ✅ Improved table and form styling"
echo ""
echo "📋 To apply changes:"
echo "1. Restart the frontend development server"
echo "2. Clear browser cache for immediate effect"
echo "3. Test all components for improved visibility"
