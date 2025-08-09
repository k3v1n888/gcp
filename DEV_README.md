# CyberDB AI Platform - Development Setup

## 🚀 Quick Start for UTM VM

### Prerequisites
- **UTM VM**: Ubuntu 24.04 LTS
- **Resources**: 4GB RAM, 30-40GB disk space
- **CPU**: 2-3 cores allocated to VM

### One-Click Installation
```bash
# Clone the repository
git clone https://github.com/k3v1n888/gcp.git
cd gcp

# Run the quick start script
chmod +x quick-start.sh
./quick-start.sh
```

### Manual Installation
```bash
# Make setup script executable
chmod +x setup-dev-environment.sh

# Run the full setup
./setup-dev-environment.sh
```

## 🏗️ Architecture Overview

### Lightweight Development Stack
- **Frontend**: React 18 + Tailwind CSS (Development server)
- **Backend**: FastAPI + SQLAlchemy (with hot reload)
- **Database**: PostgreSQL 15 (optimized for low memory)
- **AI Models**: CPU-only PyTorch models
- **Caching**: Redis (memory-limited)
- **Monitoring**: Built-in system monitoring

### Directory Structure
```
cyberdb-ai/
├── backend/                 # FastAPI backend
│   ├── agents_dev.py       # Lightweight AI agents
│   ├── requirements-dev.txt # Development dependencies
│   └── ...
├── frontend/               # React frontend
├── models/                 # AI models and cache
├── docker-compose.dev.yml  # Development services
├── .env.development       # Development configuration
├── start-dev.sh           # Start development environment
├── stop-dev.sh            # Stop development environment
└── monitor.sh             # System monitoring
```

## 🔧 Development Workflow

### Starting Development Environment
```bash
# Start all services
./start-dev.sh

# Or start individual components:
# 1. Start database services
docker-compose -f docker-compose.dev.yml up -d

# 2. Start backend (in venv)
source venv/bin/activate
cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000 &

# 3. Start frontend
cd frontend && npm start &
```

### Access Points
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database**: localhost:5432 (postgres/password)

### Stopping Environment
```bash
./stop-dev.sh
```

## 🧠 AI Models & ML Pipeline

### Lightweight AI Setup
The development environment uses CPU-only models optimized for resource efficiency:

```python
# Model Architecture (agents_dev.py)
SimpleThreatModel:
├── Linear(10 → 32)
├── ReLU + Dropout(0.2)
├── Linear(32 → 16)  
├── ReLU
└── Linear(16 → 1) → Sigmoid
```

### AI Features Available
- **Threat Detection**: Real-time threat scoring
- **SHAP Explanations**: Feature importance analysis
- **Multi-Agent System**: SIEM, XDR, ASM, Network, Endpoint, Email
- **Risk Assessment**: HIGH/MEDIUM/LOW categorization
- **Recommendations**: Automated security recommendations

### Model Management
```bash
# Download/setup models
./download-models.sh

# Check model status
curl http://localhost:8000/api/agents/status

# Test predictions
curl http://localhost:8000/api/agents/threats
```

## 🔍 Development Features

### Hot Reload Enabled
- **Backend**: uvicorn auto-reloads on code changes
- **Frontend**: React dev server with instant refresh
- **Database**: Persistent data across restarts

### Development Tools
```bash
# Monitor system resources
./monitor.sh

# View logs in real-time
tail -f ~/.pm2/logs/backend-out.log

# Database management
PGPASSWORD=password psql -h localhost -U postgres -d cyberdb

# Check Docker services
docker ps
docker stats
```

### VS Code Integration
The setup includes VS Code configuration:
- Python interpreter: `./venv/bin/python`
- Debugging configuration for FastAPI
- Task definitions for common operations
- Recommended extensions

## 🔧 Configuration

### Environment Variables
Key development settings in `.env.development`:
```bash
# Core settings
DEBUG=true
USE_CUDA=false
DATABASE_URL=postgresql://postgres:password@localhost:5432/cyberdb

# Performance optimization
WORKER_PROCESSES=2
MAX_REQUESTS=1000
INFERENCE_THREADS=2

# Feature flags
ENABLE_SHAP_EXPLANATIONS=true
ENABLE_REAL_TIME_PREDICTIONS=true
```

### Resource Optimization
The development environment is optimized for UTM VMs:
- **PostgreSQL**: 128MB shared_buffers, 256MB cache
- **Redis**: 64MB memory limit
- **PyTorch**: CPU-only inference
- **Python**: Optimized bytecode, no cache files

## 🚀 Deployment Workflow

### Local Testing
```bash
# Test with Docker Compose (production-like)
docker-compose up --build

# Run tests
cd backend && python -m pytest
cd frontend && npm test
```

### Production Deployment
```bash
# Commit changes
git add .
git commit -m "Feature: Description"
git push origin main

# Your existing GCP deployment pipeline will handle the rest
```

## 🔍 Monitoring & Debugging

### System Monitoring
```bash
# Overall system status
./monitor.sh

# Resource usage
htop
docker stats

# Application logs
journalctl -f -u cyberdb-dev  # If installed as service
```

### Database Operations
```bash
# Connect to database
PGPASSWORD=password psql -h localhost -U postgres -d cyberdb

# Common queries
SELECT * FROM threat_logs ORDER BY timestamp DESC LIMIT 10;
SELECT COUNT(*) FROM users;

# Reset database
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d
```

### API Testing
```bash
# Health check
curl http://localhost:8000/health

# Test threat prediction
curl -X GET "http://localhost:8000/api/agents/threats" \
     -H "accept: application/json"

# Check agent status
curl -X GET "http://localhost:8000/api/agents/status" \
     -H "accept: application/json"
```

## 🐛 Troubleshooting

### Common Issues

#### Port Conflicts
```bash
# Check what's using ports
sudo lsof -i :3000
sudo lsof -i :8000
sudo lsof -i :5432

# Change ports in docker-compose.dev.yml if needed
```

#### Database Connection Issues
```bash
# Restart PostgreSQL
docker-compose -f docker-compose.dev.yml restart db

# Check connection
PGPASSWORD=password psql -h localhost -U postgres -d cyberdb -c "SELECT 1;"
```

#### Memory Issues
```bash
# Check memory usage
free -h
docker stats

# Restart with memory cleanup
./stop-dev.sh
sudo sync && sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'
./start-dev.sh
```

#### Python Environment Issues
```bash
# Recreate virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r backend/requirements-dev.txt
```

### Performance Optimization

#### For Low-Memory Systems (< 4GB)
```bash
# Edit docker-compose.dev.yml
# Reduce PostgreSQL memory:
# - shared_buffers=64MB
# - effective_cache_size=128MB
# - work_mem=2MB

# Reduce Redis memory:
# - maxmemory 32mb
```

#### For Slow Disk Systems
```bash
# Enable Docker BuildKit for faster builds
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Use volume caching
# Add :cached to volume mounts in docker-compose.dev.yml
```

## 📚 API Reference

### Key Endpoints
- `GET /api/agents/threats` - Get threat predictions
- `GET /api/agents/status` - Check agent status
- `POST /api/agents/retrain` - Retrain models (mock)
- `GET /docs` - Interactive API documentation
- `GET /health` - Health check

### WebSocket Endpoints
- `/ws/threats` - Real-time threat updates
- `/ws/incidents` - Incident notifications

## 🤝 Contributing

### Development Guidelines
1. **Code Style**: Use Black formatter for Python, Prettier for JavaScript
2. **Testing**: Write tests for new features
3. **Documentation**: Update README for significant changes
4. **Environment**: Test in the UTM VM setup before deploying

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and test locally
./start-dev.sh
# Test your changes

# Commit and push
git add .
git commit -m "feat: description of changes"
git push origin feature/new-feature

# Create pull request for review
```

## 📞 Support

### Quick Commands Reference
```bash
# Start environment
./start-dev.sh

# Stop environment  
./stop-dev.sh

# Monitor system
./monitor.sh

# Reset everything
./stop-dev.sh && docker system prune -f && ./start-dev.sh

# Update dependencies
source venv/bin/activate && pip install -r backend/requirements-dev.txt
cd frontend && npm install
```

### Getting Help
1. Check logs: `./monitor.sh`
2. Review configuration: `.env.development`
3. Test connectivity: API endpoints at `http://localhost:8000/docs`
4. Database issues: Check `docker-compose -f docker-compose.dev.yml logs db`

---

**Happy coding! 🚀** 

Your lightweight development environment is optimized for UTM VM usage while maintaining full feature compatibility with your production GCP deployment.
