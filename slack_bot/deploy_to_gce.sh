#!/bin/bash

# Script completo para desplegar el bot de Slack en Google Compute Engine
# Uso: ./deploy_to_gce.sh [nombre-instancia] [zona]
# Ejemplo: ./deploy_to_gce.sh slack-bot-instance us-central1-a

# Colores para mejor legibilidad
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Verificar argumentos
if [ $# -lt 2 ]; then
    echo -e "${RED}Error: Faltan argumentos${NC}"
    echo "Uso: ./deploy_to_gce.sh [nombre-instancia] [zona]"
    echo "Ejemplo: ./deploy_to_gce.sh slack-bot-instance us-central1-a"
    exit 1
fi

INSTANCE_NAME=$1
ZONE=$2
PROJECT_ID=$(gcloud config get-value project)

echo -e "${BLUE}=== Desplegando Bot de Slack en Google Compute Engine ===${NC}"
echo -e "${BLUE}Instancia: ${YELLOW}$INSTANCE_NAME${NC}"
echo -e "${BLUE}Zona: ${YELLOW}$ZONE${NC}"
echo -e "${BLUE}Proyecto: ${YELLOW}$PROJECT_ID${NC}"
echo ""

# Verificar si la instancia ya existe
echo -e "${BLUE}Verificando si la instancia ya existe...${NC}"
INSTANCE_EXISTS=$(gcloud compute instances list --filter="name=$INSTANCE_NAME" --format="value(name)")

if [ -z "$INSTANCE_EXISTS" ]; then
    echo -e "${YELLOW}La instancia no existe. Creando nueva instancia...${NC}"
    
    # Crear la instancia
    echo -e "${BLUE}Creando instancia e2-micro...${NC}"
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
        --reservation-affinity=any
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error al crear la instancia. Abortando.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Instancia creada exitosamente.${NC}"
else
    echo -e "${GREEN}La instancia $INSTANCE_NAME ya existe.${NC}"
fi

# Crear directorio temporal para archivos de despliegue
echo -e "${BLUE}Preparando archivos para despliegue...${NC}"
TEMP_DIR=$(mktemp -d)
echo -e "${BLUE}Directorio temporal: ${YELLOW}$TEMP_DIR${NC}"

# Copiar archivos necesarios al directorio temporal
cp -r ./* $TEMP_DIR/
echo -e "${GREEN}Archivos copiados al directorio temporal.${NC}"

# Crear script de configuración para ejecutar en la instancia
echo -e "${BLUE}Creando script de configuración...${NC}"
cat > $TEMP_DIR/setup.sh << 'EOF'
#!/bin/bash

# Colores para mejor legibilidad
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Configurando Bot de Slack en GCE ===${NC}"

# Actualizar sistema
echo -e "${BLUE}Actualizando sistema...${NC}"
sudo apt-get update
sudo apt-get upgrade -y

# Instalar dependencias
echo -e "${BLUE}Instalando dependencias...${NC}"
sudo apt-get install -y python3 python3-pip python3-venv git supervisor

# Crear directorio para el bot
echo -e "${BLUE}Configurando directorio del bot...${NC}"
mkdir -p ~/slack_bot

# Mover archivos al directorio del bot
echo -e "${BLUE}Moviendo archivos...${NC}"
mv ./* ~/slack_bot/

# Crear entorno virtual
echo -e "${BLUE}Creando entorno virtual...${NC}"
cd ~/slack_bot
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
echo -e "${BLUE}Instalando dependencias de Python...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Crear archivo de configuración para supervisor
echo -e "${BLUE}Configurando supervisor...${NC}"
cat > slack_bot.conf << EOT
[program:slack_bot]
command=/home/$(whoami)/slack_bot/venv/bin/python /home/$(whoami)/slack_bot/app.py
directory=/home/$(whoami)/slack_bot
autostart=true
autorestart=true
startretries=10
user=$(whoami)
redirect_stderr=true
stdout_logfile=/home/$(whoami)/slack_bot/slack_bot.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
environment=PYTHONUNBUFFERED=1
EOT

# Instalar el servicio
echo -e "${BLUE}Instalando servicio...${NC}"
sudo mv slack_bot.conf /etc/supervisor/conf.d/
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start slack_bot

# Verificar estado del servicio
echo -e "${BLUE}Verificando estado del servicio...${NC}"
sudo supervisorctl status slack_bot

echo -e "${GREEN}¡Configuración completada!${NC}"
echo -e "${YELLOW}El bot está ahora ejecutándose como un servicio.${NC}"
echo -e "${YELLOW}Puedes ver los logs en: ~/slack_bot/slack_bot.log${NC}"
EOF

# Hacer el script ejecutable
chmod +x $TEMP_DIR/setup.sh
echo -e "${GREEN}Script de configuración creado.${NC}"

# Copiar archivos a la instancia
echo -e "${BLUE}Copiando archivos a la instancia...${NC}"
gcloud compute scp --recurse $TEMP_DIR/* $INSTANCE_NAME:~/ --zone=$ZONE

if [ $? -ne 0 ]; then
    echo -e "${RED}Error al copiar archivos a la instancia. Abortando.${NC}"
    rm -rf $TEMP_DIR
    exit 1
fi

echo -e "${GREEN}Archivos copiados exitosamente.${NC}"

# Ejecutar script de configuración en la instancia
echo -e "${BLUE}Ejecutando script de configuración en la instancia...${NC}"
gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command="bash ~/setup.sh"

if [ $? -ne 0 ]; then
    echo -e "${RED}Error al ejecutar el script de configuración. Abortando.${NC}"
    rm -rf $TEMP_DIR
    exit 1
fi

# Limpiar
rm -rf $TEMP_DIR
echo -e "${GREEN}Directorio temporal eliminado.${NC}"

echo -e "${GREEN}¡Despliegue completado exitosamente!${NC}"
echo -e "${YELLOW}El bot está ahora ejecutándose en la instancia de GCE.${NC}"
echo -e "${YELLOW}Para verificar el estado del bot, ejecuta:${NC}"
echo -e "${BLUE}gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command=\"sudo supervisorctl status slack_bot\"${NC}"
echo -e "${YELLOW}Para ver los logs del bot, ejecuta:${NC}"
echo -e "${BLUE}gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command=\"tail -f ~/slack_bot/slack_bot.log\"${NC}"
