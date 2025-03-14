#!/bin/bash

# Enhanced deployment script for Slack bot to Google Compute Engine
# Usage: ./deploy.sh [instance-name] [zone]
# Example: ./deploy.sh slack-bot-instance us-central1-a

# Strict error handling
set -euo pipefail

# Logging function
log() {
    local log_file="deployment_$(date +'%Y%m%d').log"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$log_file"
}

# Validate input
validate_input() {
    if [ $# -lt 2 ]; then
        log "ERROR: Insufficient arguments"
        echo "Usage: ./deploy.sh [instance-name] [zone]"
        echo "Example: ./deploy.sh slack-bot-instance us-central1-a"
        exit 1
    fi
}

# Pre-deployment checks
pre_deployment_checks() {
    log "Running pre-deployment checks..."
    
    # Check gcloud configuration
    if ! gcloud config get-value project > /dev/null 2>&1; then
        log "ERROR: No active Google Cloud project configured"
        exit 1
    fi

    # Check required files with more flexible search
    local required_files=("requirements.txt" "app.py" ".env")
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ] && [ ! -f "slack_bot/$file" ]; then
            log "ERROR: Required file $file is missing"
            exit 1
        fi
    done
}

# Main deployment function
deploy_slack_bot() {
    local INSTANCE_NAME="$1"
    local ZONE="$2"
    local PROJECT_ID
    PROJECT_ID=$(gcloud config get-value project)
    local TEMP_DIR
    TEMP_DIR=$(mktemp -d)

    log "Starting deployment for Slack bot"
    log "Instance: $INSTANCE_NAME, Zone: $ZONE, Project: $PROJECT_ID"

    # Secure file copy with additional checks
    log "Preparing deployment files..."
    cp -r ./* "$TEMP_DIR"
    chmod 600 "$TEMP_DIR/.env"  # Restrict .env file permissions

    # Enhanced setup script with additional security
    cat > "$TEMP_DIR/secure_setup.sh" << 'EOF'
#!/bin/bash
set -euo pipefail

# Secure system update
sudo apt-get update -q
sudo apt-get upgrade -yq
sudo apt-get install -yq --no-install-recommends python3 python3-pip python3-venv

# Create bot directory with restricted permissions
mkdir -p ~/slack_bot
chmod 750 ~/slack_bot

# Move and secure files
mv ./* ~/slack_bot/
cd ~/slack_bot
chmod 600 .env  # Restrict .env file permissions

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Secure dependency installation
pip install --no-cache-dir -r requirements.txt

# Create systemd service with enhanced security
cat > slackbot.service << 'EOT'
[Unit]
Description=Secure Slack Bot Service
After=network.target
StartLimitIntervalSec=500
StartLimitBurst=5

[Service]
User=$USER
Group=$USER
WorkingDirectory=$HOME/slack_bot
ExecStart=$HOME/slack_bot/venv/bin/python $HOME/slack_bot/app.py
Restart=on-failure
RestartSec=5s
PrivateTmp=true
ProtectSystem=full
NoNewPrivileges=true
ProtectControlGroups=true
ProtectKernelModules=true
ProtectKernelTunables=true
RestrictRealtime=true
RestrictNamespaces=true
SystemCallArchitectures=native
MemoryDenyWriteExecute=true

[Install]
WantedBy=multi-user.target
EOT

# Secure service installation
sudo mv slackbot.service /etc/systemd/system/
sudo chown root:root /etc/systemd/system/slackbot.service
sudo chmod 644 /etc/systemd/system/slackbot.service
sudo systemctl daemon-reload
sudo systemctl enable slackbot.service
sudo systemctl start slackbot.service
EOF

    # Make setup script executable
    chmod +x "$TEMP_DIR/secure_setup.sh"

    # Deployment execution with logging
    log "Copying files to instance..."
    gcloud compute scp --recurse "$TEMP_DIR"/* "$INSTANCE_NAME":~/ --zone="$ZONE"

    log "Executing secure setup script..."
    gcloud compute ssh "$INSTANCE_NAME" --zone="$ZONE" --command="bash ~/secure_setup.sh"

    # Clean up
    rm -rf "$TEMP_DIR"
    log "Deployment completed successfully"
}

# Main script execution
main() {
    validate_input "$@"
    pre_deployment_checks
    deploy_slack_bot "$@"
}

# Run the main function
main "$@"
