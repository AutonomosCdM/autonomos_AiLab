"""
Herramienta CLI para desplegar bots de Slack en Google Compute Engine.
"""
import argparse
import os
import sys
import subprocess
import tempfile
import shutil
from typing import Dict, Any, List, Optional, Tuple

# Añadir directorio raíz al path para importar módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from slack_bot.utils.logging import setup_logging

logger = setup_logging()


def parse_args():
    """
    Parsea los argumentos de línea de comandos.
    
    Returns:
        argparse.Namespace: Argumentos parseados.
    """
    parser = argparse.ArgumentParser(description='Herramienta de despliegue de bots de Slack en GCE')
    
    parser.add_argument('--project-dir', '-p', default='.', help='Directorio del proyecto')
    parser.add_argument('--instance-name', '-i', required=True, help='Nombre de la instancia de GCE')
    parser.add_argument('--zone', '-z', default='us-central1-a', help='Zona de GCE')
    parser.add_argument('--create-instance', '-c', action='store_true', help='Crear instancia si no existe')
    parser.add_argument('--machine-type', '-m', default='e2-micro', help='Tipo de máquina para la instancia')
    parser.add_argument('--verbose', '-v', action='store_true', help='Modo verboso')
    
    return parser.parse_args()


def run_command(command: List[str], cwd: Optional[str] = None) -> Tuple[int, str, str]:
    """
    Ejecuta un comando y devuelve su salida.
    
    Args:
        command (List[str]): Comando a ejecutar.
        cwd (Optional[str]): Directorio de trabajo.
        
    Returns:
        Tuple[int, str, str]: Código de salida, stdout y stderr.
    """
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd,
            text=True
        )
        stdout, stderr = process.communicate()
        return process.returncode, stdout, stderr
    except Exception as e:
        logger.error(f"Error al ejecutar comando {' '.join(command)}: {e}")
        return 1, "", str(e)


def check_instance_exists(instance_name: str, zone: str) -> bool:
    """
    Verifica si una instancia de GCE existe.
    
    Args:
        instance_name (str): Nombre de la instancia.
        zone (str): Zona de GCE.
        
    Returns:
        bool: True si la instancia existe, False en caso contrario.
    """
    command = [
        "gcloud", "compute", "instances", "describe",
        instance_name, "--zone", zone, "--format=value(name)"
    ]
    
    returncode, stdout, stderr = run_command(command)
    
    if returncode == 0 and stdout.strip():
        logger.info(f"Instancia {instance_name} encontrada en zona {zone}")
        return True
    
    logger.info(f"Instancia {instance_name} no encontrada en zona {zone}")
    return False


def create_instance(instance_name: str, zone: str, machine_type: str) -> bool:
    """
    Crea una instancia de GCE.
    
    Args:
        instance_name (str): Nombre de la instancia.
        zone (str): Zona de GCE.
        machine_type (str): Tipo de máquina.
        
    Returns:
        bool: True si se creó correctamente, False en caso contrario.
    """
    logger.info(f"Creando instancia {instance_name} en zona {zone} con tipo {machine_type}")
    
    command = [
        "gcloud", "compute", "instances", "create", instance_name,
        "--zone", zone,
        "--machine-type", machine_type,
        "--image-family", "debian-11",
        "--image-project", "debian-cloud",
        "--boot-disk-size", "10GB",
        "--boot-disk-type", "pd-standard"
    ]
    
    returncode, stdout, stderr = run_command(command)
    
    if returncode == 0:
        logger.info(f"Instancia {instance_name} creada exitosamente")
        return True
    
    logger.error(f"Error al crear instancia: {stderr}")
    return False


def create_setup_script() -> str:
    """
    Crea un script de configuración para la instancia.
    
    Returns:
        str: Ruta del script creado.
    """
    script_content = """#!/bin/bash

# Actualizar sistema
echo "Actualizando sistema..."
sudo apt-get update
sudo apt-get upgrade -y

# Instalar dependencias
echo "Instalando dependencias..."
sudo apt-get install -y python3 python3-pip python3-venv git supervisor

# Crear directorio para el bot
echo "Configurando directorio del bot..."
mkdir -p ~/slack_bot

# Mover archivos al directorio del bot
echo "Moviendo archivos..."
mv ./* ~/slack_bot/ 2>/dev/null || true

# Crear entorno virtual
echo "Creando entorno virtual..."
cd ~/slack_bot
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
echo "Instalando dependencias de Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Crear archivo de configuración para supervisor
echo "Configurando supervisor..."
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
echo "Instalando servicio..."
sudo mv slack_bot.conf /etc/supervisor/conf.d/
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start slack_bot

# Verificar estado del servicio
echo "Verificando estado del servicio..."
sudo supervisorctl status slack_bot

echo "¡Configuración completada!"
echo "El bot está ahora ejecutándose como un servicio."
echo "Puedes ver los logs en: ~/slack_bot/slack_bot.log"
"""
    
    # Crear archivo temporal
    fd, path = tempfile.mkstemp(suffix='.sh')
    os.write(fd, script_content.encode('utf-8'))
    os.close(fd)
    os.chmod(path, 0o755)  # Hacer ejecutable
    
    logger.debug(f"Script de configuración creado en: {path}")
    return path


def prepare_deployment_files(project_dir: str) -> str:
    """
    Prepara los archivos para el despliegue.
    
    Args:
        project_dir (str): Directorio del proyecto.
        
    Returns:
        str: Ruta del directorio temporal con los archivos preparados.
    """
    # Crear directorio temporal
    temp_dir = tempfile.mkdtemp()
    logger.debug(f"Directorio temporal creado: {temp_dir}")
    
    try:
        # Copiar archivos del proyecto
        for item in os.listdir(project_dir):
            # Ignorar directorios y archivos que no deben desplegarse
            if item in ['.git', '.venv', 'venv', '__pycache__', '.env', '.vscode']:
                continue
            
            source = os.path.join(project_dir, item)
            destination = os.path.join(temp_dir, item)
            
            if os.path.isdir(source):
                shutil.copytree(source, destination)
                logger.debug(f"Directorio copiado: {item}")
            else:
                shutil.copy2(source, destination)
                logger.debug(f"Archivo copiado: {item}")
        
        # Crear script de configuración
        setup_script = create_setup_script()
        shutil.copy2(setup_script, os.path.join(temp_dir, 'setup.sh'))
        os.unlink(setup_script)  # Eliminar archivo temporal
        
        logger.info(f"Archivos preparados en: {temp_dir}")
        return temp_dir
    except Exception as e:
        logger.error(f"Error al preparar archivos: {e}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise


def deploy_to_instance(temp_dir: str, instance_name: str, zone: str) -> bool:
    """
    Despliega los archivos a la instancia.
    
    Args:
        temp_dir (str): Directorio temporal con los archivos.
        instance_name (str): Nombre de la instancia.
        zone (str): Zona de GCE.
        
    Returns:
        bool: True si se desplegó correctamente, False en caso contrario.
    """
    try:
        # Copiar archivos a la instancia
        logger.info(f"Copiando archivos a la instancia {instance_name}...")
        command = [
            "gcloud", "compute", "scp", "--recurse",
            f"{temp_dir}/*", f"{instance_name}:~/",
            "--zone", zone
        ]
        
        returncode, stdout, stderr = run_command(command)
        
        if returncode != 0:
            logger.error(f"Error al copiar archivos: {stderr}")
            return False
        
        logger.info("Archivos copiados exitosamente")
        
        # Ejecutar script de configuración
        logger.info("Ejecutando script de configuración...")
        command = [
            "gcloud", "compute", "ssh",
            instance_name, "--zone", zone,
            "--command", "bash ~/setup.sh"
        ]
        
        returncode, stdout, stderr = run_command(command)
        
        if returncode != 0:
            logger.error(f"Error al ejecutar script de configuración: {stderr}")
            return False
        
        logger.info("Script de configuración ejecutado exitosamente")
        logger.info(stdout)
        
        return True
    except Exception as e:
        logger.error(f"Error al desplegar a la instancia: {e}")
        return False
    finally:
        # Limpiar directorio temporal
        shutil.rmtree(temp_dir, ignore_errors=True)
        logger.debug(f"Directorio temporal eliminado: {temp_dir}")


def deploy(
    project_dir: str,
    instance_name: str,
    zone: str,
    create_instance_if_not_exists: bool = False,
    machine_type: str = 'e2-micro'
) -> bool:
    """
    Despliega un bot de Slack en Google Compute Engine.
    
    Args:
        project_dir (str): Directorio del proyecto.
        instance_name (str): Nombre de la instancia de GCE.
        zone (str): Zona de GCE.
        create_instance_if_not_exists (bool): Si se debe crear la instancia si no existe.
        machine_type (str): Tipo de máquina para la instancia.
        
    Returns:
        bool: True si se desplegó correctamente, False en caso contrario.
    """
    # Verificar si la instancia existe
    instance_exists = check_instance_exists(instance_name, zone)
    
    # Crear instancia si es necesario
    if not instance_exists:
        if create_instance_if_not_exists:
            if not create_instance(instance_name, zone, machine_type):
                return False
        else:
            logger.error(f"La instancia {instance_name} no existe y no se ha especificado --create-instance")
            return False
    
    # Preparar archivos para el despliegue
    try:
        temp_dir = prepare_deployment_files(project_dir)
    except Exception:
        return False
    
    # Desplegar a la instancia
    return deploy_to_instance(temp_dir, instance_name, zone)


def main():
    """
    Función principal.
    """
    args = parse_args()
    
    # Configurar nivel de logging
    if args.verbose:
        logger.setLevel('DEBUG')
    
    # Desplegar
    success = deploy(
        project_dir=args.project_dir,
        instance_name=args.instance_name,
        zone=args.zone,
        create_instance_if_not_exists=args.create_instance,
        machine_type=args.machine_type
    )
    
    # Mostrar mensaje final
    if success:
        print(f"\n✅ Bot desplegado exitosamente en la instancia {args.instance_name}.")
        print("\nComandos útiles:")
        print(f"- Ver logs: gcloud compute ssh {args.instance_name} --zone={args.zone} --command=\"tail -f ~/slack_bot/slack_bot.log\"")
        print(f"- Estado del servicio: gcloud compute ssh {args.instance_name} --zone={args.zone} --command=\"sudo supervisorctl status slack_bot\"")
        print(f"- Reiniciar servicio: gcloud compute ssh {args.instance_name} --zone={args.zone} --command=\"sudo supervisorctl restart slack_bot\"")
    else:
        print("\n❌ Error al desplegar el bot. Revise los mensajes de error.")
        sys.exit(1)


if __name__ == '__main__':
    main()
