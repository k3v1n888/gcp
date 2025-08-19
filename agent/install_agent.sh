# SOC Agent Installer Script
# Universal installer for cloud and on-premises environments

function log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

function check_requirements() {
    log "Checking system requirements..."
    
    # Check if Python 3.7+ is available
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        log "Python version: $PYTHON_VERSION"
        
        # Check if version is 3.7 or higher
        if python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3,7) else 1)'; then
            log "✅ Python version is compatible"
        else
            log "❌ Python 3.7+ required, found $PYTHON_VERSION"
            exit 1
        fi
    else
        log "❌ Python 3 not found. Please install Python 3.7+ first."
        exit 1
    fi
    
    # Check for pip
    if ! command -v pip3 &> /dev/null; then
        log "❌ pip3 not found. Please install pip3 first."
        exit 1
    fi
    
    log "✅ All requirements met"
}

function install_dependencies() {
    log "Installing Python dependencies..."
    
    pip3 install --user requests configparser
    
    if [ $? -eq 0 ]; then
        log "✅ Dependencies installed successfully"
    else
        log "❌ Failed to install dependencies"
        exit 1
    fi
}

function create_agent_user() {
    log "Creating SOC agent user..."
    
    # Create a dedicated user for the agent (Linux/macOS)
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if ! id "socagent" &>/dev/null; then
            sudo useradd -r -s /bin/false -d /opt/soc-agent socagent
            log "✅ Created socagent user"
        else
            log "ℹ️  socagent user already exists"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        if ! id "socagent" &>/dev/null; then
            sudo dscl . -create /Users/socagent
            sudo dscl . -create /Users/socagent UserShell /bin/false
            sudo dscl . -create /Users/socagent RealName "SOC Agent"
            sudo dscl . -create /Users/socagent UniqueID 501
            sudo dscl . -create /Users/socagent PrimaryGroupID 20
            sudo dscl . -create /Users/socagent NFSHomeDirectory /opt/soc-agent
            log "✅ Created socagent user"
        else
            log "ℹ️  socagent user already exists"
        fi
    fi
}

function setup_directories() {
    log "Setting up directories..."
    
    # Create installation directory
    sudo mkdir -p /opt/soc-agent
    sudo mkdir -p /opt/soc-agent/logs
    sudo mkdir -p /etc/soc-agent
    
    # Set permissions
    sudo chown -R socagent:socagent /opt/soc-agent 2>/dev/null || sudo chown -R socagent:staff /opt/soc-agent
    sudo chmod 755 /opt/soc-agent
    sudo chmod 755 /opt/soc-agent/logs
    
    log "✅ Directories created"
}

function install_agent() {
    log "Installing SOC agent..."
    
    # Copy agent script
    sudo cp soc_agent.py /opt/soc-agent/
    sudo chmod +x /opt/soc-agent/soc_agent.py
    sudo chown socagent:socagent /opt/soc-agent/soc_agent.py 2>/dev/null || sudo chown socagent:staff /opt/soc-agent/soc_agent.py
    
    log "✅ Agent installed"
}

function create_config() {
    log "Creating configuration file..."
    
    # Create default configuration
    cat > /tmp/soc_agent.conf << 'EOF'
[server]
endpoint = https://your-soc-server.com:8001
api_key = your-api-key-here
tenant_id = default
verify_ssl = true

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
file = /opt/soc-agent/logs/soc_agent.log
max_size = 10MB
EOF
    
    sudo mv /tmp/soc_agent.conf /etc/soc-agent/
    sudo chown socagent:socagent /etc/soc-agent/soc_agent.conf 2>/dev/null || sudo chown socagent:staff /etc/soc-agent/soc_agent.conf
    sudo chmod 600 /etc/soc-agent/soc_agent.conf
    
    log "✅ Configuration file created at /etc/soc-agent/soc_agent.conf"
    log "⚠️  Please edit the configuration file to set your SOC server details"
}

function create_systemd_service() {
    if [[ "$OSTYPE" == "linux-gnu"* ]] && command -v systemctl &> /dev/null; then
        log "Creating systemd service..."
        
        cat > /tmp/soc-agent.service << 'EOF'
[Unit]
Description=SOC Data Collector Agent
After=network.target
Wants=network.target

[Service]
Type=simple
User=socagent
Group=socagent
ExecStart=/usr/bin/python3 /opt/soc-agent/soc_agent.py --config /etc/soc-agent/soc_agent.conf --daemon
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
        
        sudo mv /tmp/soc-agent.service /etc/systemd/system/
        sudo systemctl daemon-reload
        sudo systemctl enable soc-agent
        
        log "✅ Systemd service created and enabled"
        log "Use 'sudo systemctl start soc-agent' to start the service"
    fi
}

function create_launchd_service() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        log "Creating launchd service..."
        
        cat > /tmp/com.socagent.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.socagent</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/opt/soc-agent/soc_agent.py</string>
        <string>--config</string>
        <string>/etc/soc-agent/soc_agent.conf</string>
        <string>--daemon</string>
    </array>
    <key>UserName</key>
    <string>socagent</string>
    <key>KeepAlive</key>
    <true/>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/opt/soc-agent/logs/stdout.log</string>
    <key>StandardErrorPath</key>
    <string>/opt/soc-agent/logs/stderr.log</string>
</dict>
</plist>
EOF
        
        sudo mv /tmp/com.socagent.plist /Library/LaunchDaemons/
        sudo launchctl load /Library/LaunchDaemons/com.socagent.plist
        
        log "✅ Launchd service created and loaded"
    fi
}

function main() {
    log "🚀 Starting SOC Agent installation..."
    
    check_requirements
    install_dependencies
    create_agent_user
    setup_directories
    install_agent
    create_config
    
    # Create appropriate service based on OS
    create_systemd_service
    create_launchd_service
    
    log "🎉 SOC Agent installation completed successfully!"
    log ""
    log "Next steps:"
    log "1. Edit /etc/soc-agent/soc_agent.conf with your SOC server details"
    log "2. Test connection: sudo -u socagent python3 /opt/soc-agent/soc_agent.py --config /etc/soc-agent/soc_agent.conf --test-connection"
    
    if [[ "$OSTYPE" == "linux-gnu"* ]] && command -v systemctl &> /dev/null; then
        log "3. Start the service: sudo systemctl start soc-agent"
        log "4. Check status: sudo systemctl status soc-agent"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        log "3. Service will start automatically on next boot"
        log "4. Check logs: tail -f /opt/soc-agent/logs/*.log"
    fi
}

# Run the installer
main
