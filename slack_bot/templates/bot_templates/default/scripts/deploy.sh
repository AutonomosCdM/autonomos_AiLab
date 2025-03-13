#!/bin/bash

# Script de despliegue para {{ project_name_title }}

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

# Verificar que la instancia exista
gcloud compute instances describe "$INSTANCE_NAME" --zone="$ZONE" > /dev/null 2>&1 || handle_error "La instancia $INSTANCE_NAME no existe en la zona $ZONE"

# Iniciar despliegue
echo -e "${BLUE}=== Desplegando {{ project_name_title }} ===${NC}"
echo -e "${YELLOW}Nombre de instancia: $INSTANCE_NAME${NC}"
echo -e "${YELLOW}Zona: $ZONE${NC}"
echo -e "${YELLOW}Proyecto: $PROJECT_ID${NC}"

# Crear directorio temporal para archivos de despliegue
DEPLOY_DIR=$(mktemp -d)
trap 'rm -rf "$DEPLOY_DIR"' EXIT

# Copiar archivos del proyecto a la instancia
echo -e "${BLUE}Copiando archivos del proyecto...${NC}"
gcloud compute scp --recurse ../. "$INSTANCE_NAME:~/{{ project_name }}" --zone="$ZONE" || handle_error "No se pudieron copiar los archivos"

# Ejecutar script de configuración en la instancia
echo -e "${BLUE}Configurando entorno en la instancia...${NC}"
gcloud compute ssh "$INSTANCE_NAME" --zone="$ZONE" -- << EOF
# Actualizar sistema
sudo apt-get update
sudo apt-get upgrade -y

# Instalar dependencias del sistema
sudo apt-get install -y python3 python3-pip python3-venv git supervisor

# Crear directorio del proyecto
mkdir -p ~/{{ project_name }}
cd ~/{{ project_name }}

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias de Python
pip install --upgrade pip
pip install -r requirements.txt

# Configurar supervisor
sudo tee /etc/supervisor/conf.d/{{ project_name }}.conf > /dev/null << SUPERVISOR_CONF
[program:{{ project_name }}_bot]
command=/home/\$(whoami)/{{ project_name }}/venv/bin/python /home/\$(whoami)/{{ project_name }}/app.py
directory=/home/\$(whoami)/{{ project_name }}
autostart=true
autorestart=true
startretries=10
user=\$(whoami)
redirect_stderr=true
stdout_logfile=/home/\$(whoami)/{{ project_name }}/slack_bot.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
environment=PYTHONUNBUFFERED=1
SUPERVISOR_CONF

# Recargar y reiniciar supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart {{ project_name }}_bot

# Verificar estado del servicio
sudo supervisorctl status {{ project_name }}_bot
EOF

# Mensaje de éxito
echo -e "${GREEN}✅ Despliegue de {{ project_name_title }} completado exitosamente${NC}"
echo -e "${YELLOW}Próximos pasos:${NC}"
echo "1. Verificar logs: gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command='tail -f ~/{{ project_name }}/slack_bot.log'"
echo "2. Reiniciar servicio: gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command='sudo supervisorctl restart {{ project_name }}_bot'"
