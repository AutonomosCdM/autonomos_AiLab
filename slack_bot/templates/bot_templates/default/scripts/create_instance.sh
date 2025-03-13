#!/bin/bash

# Script para crear una instancia de Google Compute Engine para {{ project_name_title }}

# Verificar que se proporcionen los argumentos necesarios
if [ $# -lt 2 ]; then
    echo "Uso: $0 <nombre-instancia> <zona>"
    echo "Ejemplo: $0 {{ project_name }}-bot us-central1-a"
    exit 1
fi

# Argumentos
INSTANCE_NAME=$1
ZONE=$2
PROJECT_ID=$(gcloud config get-value project)

# Colores para salida
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para manejar errores
handle_error() {
    echo -e "${RED}Error: $1${NC}"
    exit 1
}

# Verificar que gcloud esté configurado
if [ -z "$PROJECT_ID" ]; then
    handle_error "No se ha configurado un proyecto de Google Cloud. Ejecuta 'gcloud config set project <ID_PROYECTO>'"
fi

# Zonas válidas para instancias e2-micro (nivel gratuito)
VALID_ZONES=("us-east1-b" "us-east1-c" "us-east1-d" 
             "us-west1-a" "us-west1-b" "us-west1-c" 
             "us-central1-a" "us-central1-b" "us-central1-c")

# Validar zona
ZONE_VALID=false
for valid_zone in "${VALID_ZONES[@]}"; do
    if [ "$valid_zone" == "$ZONE" ]; then
        ZONE_VALID=true
        break
    fi
done

if [ "$ZONE_VALID" = false ]; then
    echo -e "${RED}Zona inválida. Zonas válidas para e2-micro:${NC}"
    printf '%s\n' "${VALID_ZONES[@]}"
    exit 1
fi

# Iniciar creación de instancia
echo -e "${BLUE}=== Creando instancia para {{ project_name_title }} ===${NC}"
echo -e "${YELLOW}Nombre de instancia: $INSTANCE_NAME${NC}"
echo -e "${YELLOW}Zona: $ZONE${NC}"
echo -e "${YELLOW}Proyecto: $PROJECT_ID${NC}"

# Crear la instancia
gcloud compute instances create "$INSTANCE_NAME" \
    --project="$PROJECT_ID" \
    --zone="$ZONE" \
    --machine-type=e2-micro \
    --network-interface=network-tier=STANDARD,subnet=default \
    --maintenance-policy=MIGRATE \
    --provisioning-model=STANDARD \
    --service-account=$(gcloud iam service-accounts list --filter="displayName:Compute Engine default service account" --format="value(email)") \
    --scopes=https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/trace.append \
    --create-disk=auto-delete=yes,boot=yes,device-name="$INSTANCE_NAME",image=projects/debian-cloud/global/images/debian-11-bullseye-v20240213,mode=rw,size=10,type=projects/"$PROJECT_ID"/zones/"$ZONE"/diskTypes/pd-balanced \
    --no-shielded-secure-boot \
    --shielded-vtpm \
    --shielded-integrity-monitoring \
    --tags=http-server,https-server \
    || handle_error "No se pudo crear la instancia"

# Configurar reglas de firewall
echo -e "${BLUE}Configurando reglas de firewall...${NC}"
gcloud compute firewall-rules create "allow-http-$INSTANCE_NAME" \
    --direction=INGRESS \
    --priority=1000 \
    --network=default \
    --action=ALLOW \
    --rules=tcp:80 \
    --source-ranges=0.0.0.0/0 \
    --target-tags=http-server \
    || handle_error "No se pudo crear regla de firewall para HTTP"

gcloud compute firewall-rules create "allow-https-$INSTANCE_NAME" \
    --direction=INGRESS \
    --priority=1000 \
    --network=default \
    --action=ALLOW \
    --rules=tcp:443 \
    --source-ranges=0.0.0.0/0 \
    --target-tags=https-server \
    || handle_error "No se pudo crear regla de firewall para HTTPS"

# Mensaje de éxito
echo -e "${GREEN}✅ Instancia $INSTANCE_NAME creada exitosamente en $ZONE${NC}"
echo -e "${YELLOW}Próximos pasos:${NC}"
echo "1. Configurar variables de entorno en la instancia"
echo "2. Desplegar el bot usando: ./deploy.sh $INSTANCE_NAME $ZONE"
