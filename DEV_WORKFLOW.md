# 🚀 Development Workflow Guide

## Overview
This project uses a **dual-branch development workflow** to maintain clean separation between development and production environments.

## 🏗️ Branch Structure

```
main branch (Production - GCP)
├── 🌟 Clean production files only
├── 🐳 docker-compose.yml (GCP production)
├── 📦 Dockerfile (multi-stage production)
└── ❌ No dev/VM-specific files

dev branch (Development - VM)
├── 🔧 All development files
├── 🐳 docker-compose.vm.yml (VM development)
├── 🛠️ VM setup scripts
├── ⚙️ Dev-specific configurations
└── 🤖 Local AI models and dev tools
```

## 🔄 Development Workflow

### Step 1: Setup (One-time)
```bash
# Run the setup script to create the workflow
./setup-dev-workflow.sh
```

### Step 2: Daily Development
```bash
# 1. Work on dev branch (automatically switched by setup)
git checkout dev

# 2. Make your changes
# Edit code, update configs, etc.

# 3. Test locally on VM
./deploy-dev.sh

# 4. Access your app
# Frontend: http://192.168.64.13:3000
# Backend: http://192.168.64.13:8000
```

### Step 3: Deploy to Production
```bash
# 1. When satisfied with testing
./promote-to-prod.sh

# 2. Push to GCP
git push origin main

# 3. Continue development
git checkout dev
```

## 🛠️ Available Scripts

### `setup-dev-workflow.sh`
- **Purpose**: One-time setup of the development workflow
- **Creates**: Branch structure, sync scripts, environment files
- **Usage**: `./setup-dev-workflow.sh`

### `sync-dev-to-vm.sh`
- **Purpose**: Sync development changes to VM
- **Features**: Excludes unnecessary files, fast rsync, optional frontend restart
- **Usage**: 
  - Basic sync: `./sync-dev-to-vm.sh`
  - With frontend restart: `./sync-dev-to-vm.sh --restart-frontend`

### `sync-frontend.sh`
- **Purpose**: Quick frontend-only updates with automatic restart
- **Features**: Fast sync + automatic frontend container restart
- **Usage**: `./sync-frontend.sh`

### `deploy-dev.sh`
- **Purpose**: Full development deployment pipeline
- **Actions**: Sync to VM → Build containers → Start services → Restart frontend
- **Features**: Includes automatic frontend restart to clear React cache
- **Usage**: `./deploy-dev.sh`

### `promote-to-prod.sh`
- **Purpose**: Merge tested dev changes to main for GCP
- **Actions**: Clean dev files → Merge to main → Prepare for GCP
- **Usage**: `./promote-to-prod.sh`

## 📁 File Organization

### Development Files (dev branch only)
```
docker-compose.vm.yml     # VM development containers
.env.dev                  # Development environment variables
vm-*.sh                   # VM setup scripts
setup-*.sh               # Development setup scripts
dev-*.sh                 # Development utilities
models/                   # Local AI models
*.sqlite                  # Development databases
```

### Production Files (main branch)
```
docker-compose.yml        # GCP production containers
Dockerfile               # Multi-stage production build
nginx/                   # Production web server config
backend/requirements.txt  # Production dependencies
frontend/package.json     # Production frontend deps
```

## 🔧 Environment Variables

### Development (.env.dev)
```bash
DEV_MODE=true
DATABASE_URL=postgresql://user:password@localhost:5432/cyberdb
REDIS_URL=redis://localhost:6379
AI_SERVICE_URL=http://localhost:8001
VM_IP=192.168.64.13
REACT_APP_API_BASE_URL=http://192.168.64.13:8000
```

### Production (GCP environment)
```bash
DATABASE_URL=${CLOUD_SQL_CONNECTION}
REDIS_URL=${REDIS_INSTANCE_URL}
AI_SERVICE_URL=${AI_SERVICE_ENDPOINT}
```

## 🚨 Important Notes

### ✅ DO's
- Always work on the `dev` branch for development
- Test changes on VM before promoting to production
- Use `deploy-dev.sh` for development testing
- Use `promote-to-prod.sh` to merge to main
- Keep development and production files separated

### ❌ DON'Ts
- Don't commit VM-specific files to main branch
- Don't push directly to main without testing on dev
- Don't mix development and production configurations
- Don't skip the VM testing step

## 🔍 Troubleshooting

### VM Connection Issues
```bash
# Test VM connection
ssh kevin@192.168.64.13

# Check VM services
ssh kevin@192.168.64.13 "docker ps"
```

### Frontend Cache Issues
The deployment scripts now automatically restart the frontend container to prevent React development server caching issues:

```bash
# If you notice stale React components, use:
./sync-frontend.sh              # Quick frontend restart
./sync-dev-to-vm.sh --restart-frontend  # Sync + restart
./deploy-dev.sh                 # Full deployment (includes restart)
```

### Sync Issues
```bash
# Manual sync
rsync -av --progress --exclude-from='.gitignore' ./ kevin@192.168.64.13:/mnt/shared/ssai-project/
```

### Git Issues
```bash
# Reset to clean state
git checkout dev
git status

# View branch structure
git branch -a
```

## 📊 Workflow Summary

```
Development Cycle:
dev branch → VM testing → main branch → GCP deployment

┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌─────────────┐
│   Code on   │ →  │   Test on    │ →  │  Promote    │ →  │  Deploy     │
│ dev branch  │    │     VM       │    │  to main    │    │   to GCP    │
└─────────────┘    └──────────────┘    └─────────────┘    └─────────────┘
```

## 🎯 Benefits

- **🔒 Clean Production**: Main branch only contains production-ready files
- **🧪 Safe Testing**: All changes tested on VM before production
- **🚀 Fast Deployment**: Automated sync and deployment scripts
- **📝 Clear Separation**: Development and production configurations isolated
- **🔄 Easy Rollback**: Git history maintains clean separation
