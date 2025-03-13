"""
Herramienta CLI para generar proyectos de bot de Slack.
"""
import argparse
import os
import shutil
import sys
from typing import Dict, Any, List, Optional

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
    parser = argparse.ArgumentParser(description='Generador de proyectos de bot de Slack')
    
    parser.add_argument('project_name', help='Nombre del proyecto')
    parser.add_argument('--output-dir', '-o', default='.', help='Directorio de salida')
    parser.add_argument('--template', '-t', default='default', help='Plantilla a utilizar')
    parser.add_argument('--verbose', '-v', action='store_true', help='Modo verboso')
    
    return parser.parse_args()


def create_project_directory(project_path: str) -> bool:
    """
    Crea el directorio del proyecto.
    
    Args:
        project_path (str): Ruta del proyecto.
        
    Returns:
        bool: True si se creó correctamente, False en caso contrario.
    """
    try:
        os.makedirs(project_path, exist_ok=True)
        logger.info(f"Directorio del proyecto creado: {project_path}")
        return True
    except Exception as e:
        logger.error(f"Error al crear directorio del proyecto: {e}")
        return False


def copy_template_files(template_name: str, project_path: str) -> bool:
    """
    Copia los archivos de la plantilla al directorio del proyecto.
    
    Args:
        template_name (str): Nombre de la plantilla.
        project_path (str): Ruta del proyecto.
        
    Returns:
        bool: True si se copiaron correctamente, False en caso contrario.
    """
    try:
        # Obtener ruta de la plantilla
        template_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            '../templates/bot_templates',
            template_name
        ))
        
        # Verificar si la plantilla existe
        if not os.path.exists(template_path):
            logger.error(f"La plantilla '{template_name}' no existe")
            return False
        
        # Copiar archivos
        for item in os.listdir(template_path):
            source = os.path.join(template_path, item)
            destination = os.path.join(project_path, item)
            
            if os.path.isdir(source):
                shutil.copytree(source, destination, dirs_exist_ok=True)
                logger.debug(f"Directorio copiado: {item}")
            else:
                shutil.copy2(source, destination)
                logger.debug(f"Archivo copiado: {item}")
        
        logger.info(f"Archivos de plantilla copiados desde: {template_path}")
        return True
    except Exception as e:
        logger.error(f"Error al copiar archivos de plantilla: {e}")
        return False


def replace_template_variables(project_path: str, variables: Dict[str, str]) -> bool:
    """
    Reemplaza las variables de la plantilla en los archivos.
    
    Args:
        project_path (str): Ruta del proyecto.
        variables (Dict[str, str]): Variables a reemplazar.
        
    Returns:
        bool: True si se reemplazaron correctamente, False en caso contrario.
    """
    try:
        # Recorrer todos los archivos del proyecto
        for root, _, files in os.walk(project_path):
            for file in files:
                # Ignorar archivos binarios
                if file.endswith(('.pyc', '.pyo', '.so', '.dll', '.exe')):
                    continue
                
                file_path = os.path.join(root, file)
                
                # Leer contenido del archivo
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    # Ignorar archivos binarios que no se detectaron por extensión
                    logger.debug(f"Ignorando archivo binario: {file_path}")
                    continue
                
                # Reemplazar variables
                modified = False
                for var_name, var_value in variables.items():
                    placeholder = f"{{{{ {var_name} }}}}"
                    if placeholder in content:
                        content = content.replace(placeholder, var_value)
                        modified = True
                
                # Guardar archivo modificado
                if modified:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    logger.debug(f"Variables reemplazadas en: {file_path}")
        
        logger.info("Variables de plantilla reemplazadas")
        return True
    except Exception as e:
        logger.error(f"Error al reemplazar variables de plantilla: {e}")
        return False


def create_project(
    project_name: str,
    output_dir: str = '.',
    template: str = 'default'
) -> bool:
    """
    Crea un nuevo proyecto de bot de Slack.
    
    Args:
        project_name (str): Nombre del proyecto.
        output_dir (str): Directorio de salida.
        template (str): Plantilla a utilizar.
        
    Returns:
        bool: True si se creó correctamente, False en caso contrario.
    """
    # Normalizar nombre del proyecto
    project_name = project_name.lower().replace(' ', '_')
    
    # Crear ruta del proyecto
    project_path = os.path.abspath(os.path.join(output_dir, project_name))
    
    # Verificar si el directorio ya existe
    if os.path.exists(project_path) and os.listdir(project_path):
        logger.error(f"El directorio '{project_path}' ya existe y no está vacío")
        return False
    
    # Crear directorio del proyecto
    if not create_project_directory(project_path):
        return False
    
    # Copiar archivos de la plantilla
    if not copy_template_files(template, project_path):
        return False
    
    # Reemplazar variables de la plantilla
    variables = {
        'project_name': project_name,
        'project_name_title': project_name.replace('_', ' ').title(),
    }
    
    if not replace_template_variables(project_path, variables):
        return False
    
    logger.info(f"Proyecto '{project_name}' creado exitosamente en: {project_path}")
    return True


def main():
    """
    Función principal.
    """
    args = parse_args()
    
    # Configurar nivel de logging
    if args.verbose:
        logger.setLevel('DEBUG')
    
    # Crear proyecto
    success = create_project(
        project_name=args.project_name,
        output_dir=args.output_dir,
        template=args.template
    )
    
    # Mostrar mensaje final
    if success:
        print(f"\n✅ Proyecto '{args.project_name}' creado exitosamente.")
        print(f"   Ubicación: {os.path.abspath(os.path.join(args.output_dir, args.project_name))}")
        print("\nPasos siguientes:")
        print("1. Crear un entorno virtual: python -m venv venv")
        print("2. Activar el entorno virtual:")
        print("   - Windows: venv\\Scripts\\activate")
        print("   - Unix/MacOS: source venv/bin/activate")
        print("3. Instalar dependencias: pip install -r requirements.txt")
        print("4. Configurar variables de entorno en .env")
        print("5. Ejecutar el bot: python app.py")
    else:
        print("\n❌ Error al crear el proyecto. Revise los mensajes de error.")
        sys.exit(1)


if __name__ == '__main__':
    main()
