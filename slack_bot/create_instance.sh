#!/bin/bash

# Script to create a Google Compute Engine e2-micro instance for the Slack bot
# Usage: ./create_instance.sh [instance-name] [zone]
# Example: ./create_instance.sh slack-bot-instance us-central1-a

# Check if arguments are provided
if [ $# -lt 2 ]; then
    echo "Usage: ./create_instance.sh [instance-name] [zone]"
    echo "Example: ./create_instance.sh slack-bot-instance us-central1-a"
    exit 1
fi

INSTANCE_NAME=$1
ZONE=$2
PROJECT_ID=$(gcloud config get-value project)

echo "Creating instance: $INSTANCE_NAME in zone: $ZONE"

# Create the instance
gcloud compute instances create $INSTANCE_NAME \
    --project=$PROJECT_ID \
    --zone=$ZONE \
    --machine-type=e2-micro \
    --network-interface=network-tier=STANDARD,subnet=default \
    --maintenance-policy=MIGRATE \
    --provisioning-model=STANDARD \
    --service-account=default \
    --scopes=https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/trace.append \
    --create-disk=auto-delete=yes,boot=yes,device-name=$INSTANCE_NAME,image=projects/debian-cloud/global/images/debian-11-bullseye-v20240213,mode=rw,size=10,type=projects/$PROJECT_ID/zones/$ZONE/diskTypes/pd-balanced \
    --no-shielded-secure-boot \
    --shielded-vtpm \
    --shielded-integrity-monitoring \
    --reservation-affinity=any \
    --tags=http-server,https-server

# Allow HTTP and HTTPS traffic
gcloud compute firewall-rules create allow-http \
    --direction=INGRESS \
    --priority=1000 \
    --network=default \
    --action=ALLOW \
    --rules=tcp:80 \
    --source-ranges=0.0.0.0/0 \
    --target-tags=http-server

gcloud compute firewall-rules create allow-https \
    --direction=INGRESS \
    --priority=1000 \
    --network=default \
    --action=ALLOW \
    --rules=tcp:443 \
    --source-ranges=0.0.0.0/0 \
    --target-tags=https-server

echo "Instance created successfully!"
echo "You can now deploy the Slack bot using: ./deploy.sh $INSTANCE_NAME $ZONE"
