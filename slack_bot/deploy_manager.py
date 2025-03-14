#!/usr/bin/env python3
import os
import sys
import subprocess
import logging
from typing import Dict, Any
import yaml
import argparse

class DeploymentManager:
    def __init__(self, config_path: str = 'deployment_config.yaml'):
        """
        Initialize deployment manager with configuration
        """
        self.logger = self._setup_logging()
        self.config = self._load_config(config_path)
        
    def _setup_logging(self) -> logging.Logger:
        """
        Configure comprehensive logging
        """
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('deployment.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        return logging.getLogger('DeploymentManager')

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load deployment configuration
        """
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config or {}
        except FileNotFoundError:
            self.logger.warning(f"Configuration file {config_path} not found. Using default settings.")
            return {
                'cloud_provider': 'google_compute_engine',
                'instance_type': 'e2-micro',
                'region': 'southamerica-west1-a',
                'security_groups': ['http-server', 'https-server']
            }

    def validate_environment(self) -> bool:
        """
        Validate deployment environment
        """
        required_tools = ['gcloud', 'python3', 'pip']
        for tool in required_tools:
            if not self._check_tool_installed(tool):
                self.logger.error(f"{tool} is not installed")
                return False
        return True

    def _check_tool_installed(self, tool: str) -> bool:
        """
        Check if a tool is installed
        """
        try:
            subprocess.run(['which', tool], 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE, 
                           check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def validate_instance_name(self, instance_name: str) -> str:
        """
        Validate and sanitize instance name according to GCP requirements
        """
        # Convert to lowercase
        sanitized_name = instance_name.lower()
        
        # Replace invalid characters
        sanitized_name = ''.join(c if c.isalnum() or c == '-' else '-' for c in sanitized_name)
        
        # Ensure starts with a letter
        if not sanitized_name[0].isalpha():
            sanitized_name = 'instance-' + sanitized_name
        
        # Truncate to 63 characters
        sanitized_name = sanitized_name[:63]
        
        # Ensure ends with alphanumeric character
        sanitized_name = sanitized_name.rstrip('-')
        
        return sanitized_name

    def create_instance(self, instance_name: str) -> bool:
        """
        Create cloud compute instance
        """
        # Validate and sanitize instance name
        sanitized_name = self.validate_instance_name(instance_name)
        
        try:
            # First, check if instance already exists
            check_cmd = [
                'gcloud', 'compute', 'instances', 'describe', sanitized_name,
                f'--zone={self.config.get("region", "southamerica-west1-a")}'
            ]
            
            check_result = subprocess.run(check_cmd, 
                                          capture_output=True, 
                                          text=True)
            
            if check_result.returncode == 0:
                self.logger.info(f"Instance {sanitized_name} already exists. Skipping creation.")
                return True
            
            # If instance doesn't exist, create it
            create_cmd = [
                'gcloud', 'compute', 'instances', 'create', sanitized_name,
                f'--machine-type={self.config.get("instance_type", "e2-micro")}',
                f'--zone={self.config.get("region", "southamerica-west1-a")}',
                '--network-interface=network-tier=STANDARD,subnet=default',
                '--maintenance-policy=MIGRATE',
                '--provisioning-model=STANDARD',
                '--service-account=default',
                '--scopes=https://www.googleapis.com/auth/cloud-platform',
                '--image-family=debian-11',
                '--image-project=debian-cloud',
                '--boot-disk-size=10GB',
                '--boot-disk-type=pd-balanced',
                '--tags=' + ','.join(self.config.get('security_groups', ['http-server', 'https-server']))
            ]

            result = subprocess.run(create_cmd, 
                                    capture_output=True, 
                                    text=True, 
                                    check=True)
            self.logger.info(f"Instance {sanitized_name} created successfully")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Instance creation failed: {e.stderr}")
            return False

    def deploy_application(self, instance_name: str) -> bool:
        """
        Deploy application to created instance
        """
        try:
            # Copy deployment files
            copy_cmd = [
                'gcloud', 'compute', 'scp', 
                '--recurse', 'slack_bot', 
                f'{instance_name}:~/slack_bot',
                f'--zone={self.config.get("region", "southamerica-west1-a")}'
            ]
            subprocess.run(copy_cmd, check=True)

            # Remote setup and deployment
            # Create a separate script for service setup
            service_script = """#!/bin/bash
set -e
set -x

# Update and install dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv

# Setup virtual environment
python3 -m venv ~/slack_bot/venv
. ~/slack_bot/venv/bin/activate
pip install -r ~/slack_bot/requirements.txt

# Create .env file with required tokens
cat > ~/slack_bot/.env << EOF
# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
SLACK_CHANNEL=your-default-channel

# Other configurations
LOG_LEVEL=INFO
DEFAULT_PERSONALITY=default
EOF

# Create service file
mkdir -p ~/slack_bot
cat > ~/slack_bot/slackbot.service << EOF
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
EOF

# Install and start service
sudo mkdir -p /etc/systemd/system
sudo cp ~/slack_bot/slackbot.service /etc/systemd/system/slackbot.service
sudo chmod 644 /etc/systemd/system/slackbot.service
sudo systemctl daemon-reload
sudo systemctl enable slackbot.service
sudo systemctl start slackbot.service
sudo systemctl status slackbot.service || echo "Service start failed"
"""

            # First, create the setup script on the remote machine
            script_cmd = [
                'gcloud', 'compute', 'ssh', instance_name,
                f'--zone={self.config.get("region", "southamerica-west1-a")}',
                '--command', f'echo \'{service_script}\' > ~/setup_service.sh && chmod +x ~/setup_service.sh'
            ]
            subprocess.run(script_cmd, check=True)
            
            # Then execute the script
            setup_cmd = [
                'gcloud', 'compute', 'ssh', instance_name,
                f'--zone={self.config.get("region", "southamerica-west1-a")}',
                '--command', './setup_service.sh'
            ]
            subprocess.run(setup_cmd, check=True)

            self.logger.info(f"Application deployed to {instance_name}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Deployment failed: {e}")
            return False

    def main(self, instance_name: str):
        """
        Main deployment workflow
        """
        self.logger.info("Starting deployment process")
        
        if not self.validate_environment():
            self.logger.error("Environment validation failed")
            sys.exit(1)

        if not self.create_instance(instance_name):
            self.logger.error("Instance creation failed")
            sys.exit(1)

        if not self.deploy_application(instance_name):
            self.logger.error("Application deployment failed")
            sys.exit(1)

        self.logger.info("Deployment completed successfully")

def cli():
    """
    Command-line interface for deployment manager
    """
    parser = argparse.ArgumentParser(description='Slack Bot Deployment Manager')
    parser.add_argument('instance_name', help='Name of the cloud instance')
    parser.add_argument('--config', default='deployment_config.yaml', 
                        help='Path to deployment configuration file')
    
    args = parser.parse_args()
    
    deployment_manager = DeploymentManager(args.config)
    deployment_manager.main(args.instance_name)

if __name__ == '__main__':
    cli()
