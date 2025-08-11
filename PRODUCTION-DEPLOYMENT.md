# Production Deployment Guide

## 🚀 Cybersecurity Dashboard - Production Deployment

This guide covers deploying the enhanced cybersecurity dashboard with scrollable improvements and safe forecasting to production.

### ✅ Pre-Deployment Checklist

**System Requirements:**
- Docker & Docker Compose installed
- Node.js 16+ for frontend builds
- SSL certificates for HTTPS
- Domain name configured
- Database setup (PostgreSQL recommended)

**Security Configuration:**
- [ ] Update `.env.production` with secure values
- [ ] Generate strong SECRET_KEY and JWT_SECRET_KEY
- [ ] Configure SSL certificates in `nginx/ssl/`
- [ ] Set up proper CORS origins
- [ ] Configure database with strong passwords

### 🛠 Deployment Methods

#### Method 1: Docker Compose (Recommended)

```bash
# Make deployment script executable
chmod +x deploy-production.sh

# Run production deployment
./deploy-production.sh
```

#### Method 2: Manual Docker

```bash
# Build production images
docker build -f Dockerfile.prod -t cybersecurity-dashboard:latest .

# Start with production compose
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

#### Method 3: Kubernetes

```bash
# Apply Kubernetes configuration
kubectl apply -f k8s-deployment.yaml

# Create secrets
kubectl create secret generic dashboard-secrets \
  --from-literal=database-url="postgresql://user:pass@host:5432/db" \
  --from-literal=secret-key="your-secret-key"
```

### 🔧 Configuration Files

**Key Production Files:**
- `.env.production` - Environment variables
- `docker-compose.prod.yml` - Production overrides
- `nginx/prod.conf` - Reverse proxy configuration
- `Dockerfile.prod` - Optimized production image
- `k8s-deployment.yaml` - Kubernetes deployment

### 🎯 Enhanced Features Deployed

**Dashboard Improvements:**
- ✅ Scrollable incidents section (max-height: 20rem)
- ✅ Scrollable threats feed (max-height: 24rem)
- ✅ Item counters showing data volume
- ✅ Sticky table headers during scroll
- ✅ Professional empty states
- ✅ Custom cyber-themed scrollbars

**Safe Forecasting System:**
- ✅ 3-layer fallback (ML → Statistical → Mock)
- ✅ Health monitoring endpoints
- ✅ Enhanced mock data with realistic probabilities
- ✅ Error handling that never breaks the app

### 📊 Monitoring & Health Checks

**Health Endpoints:**
- `GET /health` - Nginx health
- `GET /api/forecasting/health` - Forecasting service
- `GET /api/threats` - Threat data availability
- `GET /api/incidents` - Incident data availability

**Monitoring Stack:**
- Nginx access/error logs
- Application logs via Docker
- Health check probes
- Resource usage monitoring

### 🔐 Security Features

**Production Security:**
- HTTPS enforced with SSL certificates
- Security headers (HSTS, CSP, XSS protection)
- Rate limiting on API endpoints
- CORS properly configured
- Secrets managed via environment variables
- Container runs as non-root user

### 🚀 Post-Deployment Verification

**Test these endpoints after deployment:**

1. **Main Dashboard**: `https://your-domain.com/`
2. **API Health**: `https://your-domain.com/api/forecasting/health`
3. **Threat Feed**: `https://your-domain.com/api/threats`
4. **Incident Data**: `https://your-domain.com/api/incidents`
5. **Forecast API**: `https://your-domain.com/api/forecasting/predict`

**Expected Results:**
- Dashboard loads with scrollable sections
- Threat counters show "X Active Threats"  
- Incident counters show "X Total"
- Tables scroll smoothly with sticky headers
- Forecasting returns 1-3% realistic probabilities
- All APIs return proper JSON responses

### 📝 Production Logs

```bash
# View all service logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f nginx

# Kubernetes logs
kubectl logs -l app=cybersecurity-dashboard -f
```

### 🔄 Updates & Maintenance

**Rolling Updates:**
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
./deploy-production.sh

# Zero-downtime K8s update
kubectl set image deployment/cybersecurity-dashboard-backend backend=cybersecurity-dashboard:v2.0
```

### 🆘 Troubleshooting

**Common Issues:**
- SSL certificate problems → Check nginx/ssl/ directory
- Database connection → Verify DATABASE_URL in .env.production
- CORS errors → Update CORS_ORIGINS setting
- High memory usage → Adjust container limits

**Quick Fixes:**
```bash
# Restart services
docker-compose restart

# Check service health
curl -f https://your-domain.com/api/forecasting/health

# View container status
docker-compose ps
```

---

## 🎉 Production Ready!

Your enhanced cybersecurity dashboard is now production-ready with:
- Professional scrollable interface ✅
- Bulletproof forecasting system ✅
- Enterprise-grade security ✅  
- Scalable deployment options ✅
- Comprehensive monitoring ✅

**Access your dashboard at: `https://your-domain.com`** 🚀
