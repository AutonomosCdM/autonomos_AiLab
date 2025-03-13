#!/bin/bash

# Simple deployment script for Slack bot to Google Compute Engine
# Usage: ./deploy.sh [instance-name] [zone]
# Example: ./deploy.sh slack-bot-instance us-central1-a

# Check if arguments are provided
if [ $# -lt 2 ]; then
    echo "Usage: ./deploy.sh [instance-name] [zone]"
    echo "Example: ./deploy.sh slack-bot-instance us-central1-a"
    exit 1
fi

INSTANCE_NAME=$1
ZONE=$2
PROJECT_ID=$(gcloud config get-value project)

echo "Deploying Slack bot to instance: $INSTANCE_NAME in zone: $ZONE"

# Create a temporary directory for deployment files
TEMP_DIR=$(mktemp -d)
echo "Created temporary directory: $TEMP_DIR"

# Copy all necessary files to the temporary directory
cp -r ./* $TEMP_DIR/
echo "Copied files to temporary directory"

# Create a setup script to run on the instance
cat > $TEMP_DIR/setup.sh << 'EOF'
#!/bin/bash

# Update system packages
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv

# Create a directory for the bot
mkdir -p ~/slack_bot

# Move files to the bot directory
mv ./* ~/slack_bot/

# Create a virtual environment
cd ~/slack_bot
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create a systemd service file
cat > slackbot.service << 'EOT'
[Unit]
Description=Slack Bot Service
After=network.target

[Service]
User=$USER
WorkingDirectory=$HOME/slack_bot
ExecStart=$HOME/slack_bot/venv/bin/python $HOME/slack_bot/app.py
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOT

# Install the service
sudo mv slackbot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable slackbot.service
sudo systemctl start slackbot.service

# Check service status
sudo systemctl status slackbot.service
EOF

# Make the setup script executable
chmod +x $TEMP_DIR/setup.sh
echo "Created setup script"

# Copy files to the instance
echo "Copying files to instance..."
gcloud compute scp --recurse $TEMP_DIR/* $INSTANCE_NAME:~/ --zone=$ZONE

# Execute the setup script on the instance
echo "Running setup script on instance..."
gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command="bash ~/setup.sh"

# Clean up
rm -rf $TEMP_DIR
echo "Deployment complete!"
