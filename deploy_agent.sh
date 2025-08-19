#!/bin/bash
# Universal SOC Agent Deployment Script
# Copyright (c) 2025 Kevin Zachary

set -e

# Configuration
SOC_SERVER_URL="${SOC_SERVER_URL:-https://localhost:8001}"
API_KEY="${API_KEY:-}"
TENANT_ID="${TENANT_ID:-default}"
INSTALL_DIR="/opt/soc-agent"
CONFIG_DIR="/etc/soc-agent"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root (use sudo)"
    fi
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        if [ -f /etc/debian_version ]; then
            DISTRO="debian"
        elif [ -f /etc/redhat-release ]; then
            DISTRO="redhat"
        else
            DISTRO="unknown"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        DISTRO="macos"
    else
        error "Unsupported operating system: $OSTYPE"
    fi
    
    log "Detected OS: $OS ($DISTRO)"
}

# Install Python dependencies
install_dependencies() {
    log "Installing dependencies..."
    
    case $DISTRO in
        "debian")
            apt-get update
            apt-get install -y python3 python3-pip curl wget
            ;;
        "redhat")
            yum install -y python3 python3-pip curl wget
            ;;
        "macos")
            # Check if homebrew is installed
            if ! command -v brew &> /dev/null; then
                warning "Homebrew not found. Installing..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            brew install python3
            ;;
    esac
    
    # Install Python packages
    pip3 install requests configparser psutil
    success "Dependencies installed"
}

# Download agent
download_agent() {
    log "Downloading SOC agent..."
    
    # Create directories
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$INSTALL_DIR/logs"
    
    # In a real deployment, this would download from a secure server
    # For now, we'll copy from the current directory
    if [ -f "agent/soc_agent.py" ]; then
        cp agent/soc_agent.py "$INSTALL_DIR/"
        chmod +x "$INSTALL_DIR/soc_agent.py"
        success "Agent downloaded"
    else
        error "Agent file not found. Please ensure soc_agent.py is available."
    fi
}

# Create configuration
create_config() {
    log "Creating agent configuration..."
    
    cat > "$CONFIG_DIR/soc_agent.conf" << EOF
[server]
endpoint = $SOC_SERVER_URL
api_key = $API_KEY
tenant_id = $TENANT_ID
verify_ssl = false

[agent]
name = soc-agent-$(hostname)
environment = production
collection_interval = 60
heartbeat_interval = 300

[collectors]
system_logs = true
security_logs = true
network_events = true
process_events = true
file_events = false

[logs]
level = INFO
file = $INSTALL_DIR/logs/soc_agent.log
max_size = 10MB
EOF
    
    chmod 600 "$CONFIG_DIR/soc_agent.conf"
    success "Configuration created at $CONFIG_DIR/soc_agent.conf"
}

# Create user
create_user() {
    log "Creating SOC agent user..."
    
    if ! id "socagent" &>/dev/null; then
        case $OS in
            "linux")
                useradd -r -s /bin/false -d "$INSTALL_DIR" socagent
                ;;
            "macos")
                # Create user on macOS
                dscl . -create /Users/socagent
                dscl . -create /Users/socagent UserShell /bin/false
                dscl . -create /Users/socagent RealName "SOC Agent"
                dscl . -create /Users/socagent UniqueID 501
                dscl . -create /Users/socagent PrimaryGroupID 20
                dscl . -create /Users/socagent NFSHomeDirectory "$INSTALL_DIR"
                ;;
        esac
        success "Created socagent user"
    else
        success "socagent user already exists"
    fi
    
    # Set permissions
    chown -R socagent:socagent "$INSTALL_DIR" 2>/dev/null || chown -R socagent:staff "$INSTALL_DIR"
    chown socagent:socagent "$CONFIG_DIR/soc_agent.conf" 2>/dev/null || chown socagent:staff "$CONFIG_DIR/soc_agent.conf"
}

# Create systemd service (Linux)
create_systemd_service() {
    if [[ "$OS" == "linux" ]] && command -v systemctl &> /dev/null; then
        log "Creating systemd service..."
        
        cat > /etc/systemd/system/soc-agent.service << EOF
[Unit]
Description=SOC Data Collector Agent
After=network.target
Wants=network.target

[Service]
Type=simple
User=socagent
Group=socagent
ExecStart=/usr/bin/python3 $INSTALL_DIR/soc_agent.py --config $CONFIG_DIR/soc_agent.conf --daemon
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
        
        systemctl daemon-reload
        systemctl enable soc-agent
        success "Systemd service created and enabled"
    fi
}

# Create launchd service (macOS)
create_launchd_service() {
    if [[ "$OS" == "macos" ]]; then
        log "Creating launchd service..."
        
        cat > /Library/LaunchDaemons/com.socagent.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.socagent</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>$INSTALL_DIR/soc_agent.py</string>
        <string>--config</string>
        <string>$CONFIG_DIR/soc_agent.conf</string>
        <string>--daemon</string>
    </array>
    <key>UserName</key>
    <string>socagent</string>
    <key>KeepAlive</key>
    <true/>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$INSTALL_DIR/logs/stdout.log</string>
    <key>StandardErrorPath</key>
    <string>$INSTALL_DIR/logs/stderr.log</string>
</dict>
</plist>
EOF
        
        launchctl load /Library/LaunchDaemons/com.socagent.plist
        success "Launchd service created and loaded"
    fi
}

# Test connection
test_connection() {
    log "Testing connection to SOC server..."
    
    if sudo -u socagent python3 "$INSTALL_DIR/soc_agent.py" --config "$CONFIG_DIR/soc_agent.conf" --test-connection; then
        success "Connection test successful"
        return 0
    else
        warning "Connection test failed. Please check configuration."
        return 1
    fi
}

# Main installation function
main() {
    echo "🚀 SOC Agent Universal Installer"
    echo "================================"
    
    # Get configuration if not provided
    if [ -z "$API_KEY" ]; then
        read -p "Enter SOC Server API Key: " API_KEY
    fi
    
    if [ -z "$SOC_SERVER_URL" ]; then
        read -p "Enter SOC Server URL [https://localhost:8001]: " SOC_SERVER_URL
        SOC_SERVER_URL=${SOC_SERVER_URL:-https://localhost:8001}
    fi
    
    # Run installation steps
    check_root
    detect_os
    install_dependencies
    download_agent
    create_config
    create_user
    create_systemd_service
    create_launchd_service
    
    echo ""
    echo "🎉 Installation completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Edit configuration: $CONFIG_DIR/soc_agent.conf"
    echo "2. Test connection: sudo -u socagent python3 $INSTALL_DIR/soc_agent.py --config $CONFIG_DIR/soc_agent.conf --test-connection"
    
    if [[ "$OS" == "linux" ]] && command -v systemctl &> /dev/null; then
        echo "3. Start service: systemctl start soc-agent"
        echo "4. Check status: systemctl status soc-agent"
        echo "5. View logs: journalctl -u soc-agent -f"
    elif [[ "$OS" == "macos" ]]; then
        echo "3. Service will start automatically"
        echo "4. View logs: tail -f $INSTALL_DIR/logs/*.log"
    fi
    
    echo ""
    echo "Configuration file: $CONFIG_DIR/soc_agent.conf"
    echo "Log file: $INSTALL_DIR/logs/soc_agent.log"
    
    # Test connection
    test_connection
}

# Run main function
main "$@"
