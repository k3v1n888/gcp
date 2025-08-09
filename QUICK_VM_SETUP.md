# 🎯 Complete Development Setup Guide

## 🚀 Phase 1: Copy AI Models (Run on Mac)

```bash
# Make the copy script executable and run it
chmod +x copy-ai-models.sh
./copy-ai-models.sh
```

## 🛠️ Phase 2: Setup Local AI Service (Run on VM)

```bash
# SSH to your VM
ssh kevin@192.168.64.13

# Setup the local AI service
cd /mnt/shared/ssai-project
chmod +x setup-local-ai.sh
./setup-local-ai.sh
```

## ⚡ Phase 3: Start Development Environment

### Method A: All-in-One Start (Recommended)
```bash
# Make scripts executable
chmod +x dev-start-backend.sh dev-start-frontend.sh start-ai-service.sh

# Start everything together
./dev-start-backend.sh
```

### Method B: Manual Start (for debugging)
```bash
# Terminal 1: AI service
./start-ai-service.sh

# Terminal 2: Backend
export DEV_MODE=true
source venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 3: Frontend
./dev-start-frontend.sh
```

## 🌐 Your Development URLs

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://192.168.64.13:3000 | Main application |
| **Backend API** | http://192.168.64.13:8000 | REST API |
| **API Docs** | http://192.168.64.13:8000/docs | Interactive API documentation |
| **AI Service** | http://192.168.64.13:8001 | Local AI predictions |
| **AI Debug** | http://192.168.64.13:8001/debug | AI service status |

## 🔐 Authentication (No Google OAuth Needed!)

✅ **Development mode automatically:**
- Creates a "Developer" user with admin privileges
- Bypasses Google OAuth completely
- Just visit http://192.168.64.13:3000 and click login

## 🤖 Local AI System

Your development environment now has **THREE layers of AI**:

1. **🎯 Local ML Model** (fastest)
   - Simple scikit-learn model
   - Instant predictions
   - No network dependencies

2. **🚀 Local AI Service** (your production models)
   - Flask service running your actual models
   - Same API as production
   - Uses your trained joblib files

3. **🛡️ Fallback System** (most reliable)
   - Simple rule-based predictions
   - Always works as backup

### Testing AI Predictions
```bash
# Test the local AI service
curl -X POST http://192.168.64.13:8001/predict \
  -H "Content-Type: application/json" \
  -d '{
    "technique_id": "T1190",
    "asset_type": "server", 
    "cvss_score": 7.5,
    "criticality_score": 0.8
  }'

# Test through main backend
curl -X POST http://192.168.64.13:8000/api/threats \
  -H "Content-Type: application/json" \
  -d '{
    "ip": "192.168.1.100",
    "threat": "SQL injection attempt",
    "source": "external"
  }'
```

## 📁 Complete Project Structure

```
/mnt/shared/ssai-project/
├── 🎯 backend/                 # FastAPI main application
│   ├── ml/
│   │   ├── prediction.py      # Enhanced with local AI
│   │   └── local_prediction.py # Local ML model
│   ├── auth/
│   │   └── auth.py           # Dev mode authentication
│   └── ...
├── ⚛️ frontend/                # React application
├── 🤖 ai-service/              # Local AI prediction service
│   ├── main.py               # Flask AI service (your code!)
│   ├── models/               # Your AI model files
│   │   ├── model.joblib
│   │   ├── preprocessor.joblib
│   │   └── ...
│   ├── venv/                # AI service Python environment
│   └── requirements.txt
├── 🐍 venv/                    # Main backend environment
├── 🔧 .env.dev                 # Development configuration
├── 📜 dev-start-*.sh           # Startup scripts
└── 📚 QUICK_VM_SETUP.md        # This file
```

## 🔄 Perfect Development Workflow

1. **💻 Edit in VS Code** on your Mac
   - Files sync instantly via shared folder
   - Full IntelliSense and debugging support

2. **🔥 Hot Reload Everything**
   - Backend: Auto-reloads on Python changes
   - Frontend: Hot reloads on React changes
   - AI Service: Restart manually when needed

3. **🧪 Test Locally**
   - Full application runs on VM
   - Use real AI models or fallbacks
   - Complete database and Redis

4. **📤 Deploy When Ready**
   - Commit and push from VS Code
   - Automatic GCP deployment via existing pipeline

## 🔍 Debugging & Monitoring

### Health Checks
```bash
curl http://192.168.64.13:8000/        # Backend ✓
curl http://192.168.64.13:8001/        # AI Service ✓
curl http://192.168.64.13:3000/        # Frontend (in browser)
```

### Service Logs
```bash
# Watch backend logs
tail -f logs/backend.log

# Watch AI service logs  
tail -f logs/ai-service.log

# Database logs
docker logs shared_db_1

# All services status
docker ps -a
```

### Development Environment Variables
```bash
# Automatically set by dev scripts:
DEV_MODE=true
DATABASE_URL=postgresql://user:password@localhost:5432/cyberdb
FRONTEND_URL=http://192.168.64.13:3000
```

## 🚀 Production vs Development

| Feature | Development | Production |
|---------|-------------|------------|
| **Authentication** | Dev user (no OAuth) | Google OAuth |
| **AI Models** | Local files + fallback | GCP AI service |
| **Database** | Docker PostgreSQL | Cloud SQL |
| **Frontend** | React dev server | Production build |
| **SSL** | HTTP only | HTTPS + certificates |
| **Scaling** | Single VM | Auto-scaling containers |

## 💡 Pro Tips

### 🎯 **VS Code Integration**
- Install Python and React extensions
- Files sync instantly to VM
- Use integrated terminal for Git operations

### 🔥 **Fast Iteration**
- Keep VS Code open on Mac for editing  
- Keep terminal open on VM for logs
- Changes appear instantly in browser

### 🤖 **AI Model Development**
- Replace files in `ai-service/models/` 
- Restart AI service: `./start-ai-service.sh`
- Test immediately with curl commands

### 🐛 **Debugging**
- Use browser dev tools for frontend
- Check terminal output for backend errors  
- AI service has detailed logging

### 📊 **Performance**
- Local AI is much faster than remote calls
- Database queries are optimized for development
- Hot reload keeps sessions active

## 🆘 Troubleshooting

### "AI Service Not Responding"
```bash
# Check if AI service is running
curl http://192.168.64.13:8001/debug

# Restart AI service
cd /mnt/shared/ssai-project/ai-service
source venv/bin/activate  
python main.py
```

### "Authentication Failed"
```bash
# Ensure DEV_MODE is set
export DEV_MODE=true

# Clear browser cookies and try again
# Visit: http://192.168.64.13:3000
```

### "Database Connection Error"
```bash
# Check Docker containers
docker ps | grep postgres

# Restart database
docker-compose -f docker-compose.dev.yml restart db
```

### "Models Not Found"
```bash
# Check if AI models were copied
ls -la /mnt/shared/ssai-project/ai-service/models/

# Copy from your Mac again
./copy-ai-models.sh
```

---

## 🎉 You're All Set!

Your development environment provides:
- ✅ **Full local development** with real AI models
- ✅ **No authentication complexity** (dev mode)
- ✅ **Instant file synchronization** (VS Code + shared folder)
- ✅ **Production-like testing** (same APIs and databases)
- ✅ **Seamless deployment** (existing GCP pipeline)

**Happy coding!** 🚀
code .

# 2. Quick development cycle
./dev-workflow/quick.sh dev         # Sync + restart + check status

# 3. View logs if needed
./dev-workflow/sync-to-vm.sh logs

# 4. Run tests
./dev-workflow/sync-to-vm.sh test

# 5. When ready, commit and push
./dev-workflow/sync-to-vm.sh git
```

## If You Need Help:

1. **Test shared folder**: `./dev-workflow/test-shared-folder.sh all`
2. **Check VM network**: On VM run `ip addr show`  
3. **Manual mount**: On VM run `sudo mount -t 9p -o trans=virtio,version=9p2000.L,rw,_netdev ssai-vm-dev /mnt/shared`

## Alternative: Manual Step-by-Step Commands

If you prefer to run commands manually instead of the script:

### On Your VM:
```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install dependencies
sudo apt install -y curl wget git vim htop tree rsync unzip build-essential python3 python3-pip python3-venv nodejs npm docker.io docker-compose bc

# 3. Add user to docker group  
sudo usermod -aG docker $USER

# 4. Mount shared folder
sudo mkdir -p /mnt/shared
sudo mount -t 9p -o trans=virtio,version=9p2000.L,rw,_netdev ssai-vm-dev /mnt/shared

# 5. Create symlink
ln -sf /mnt/shared ~/shared

# 6. Restart or run: newgrp docker
```

The automated script does all this plus creates management tools for you!

---

**Ready?** Just copy the `vm-complete-setup.sh` to your VM and run it! 🚀
