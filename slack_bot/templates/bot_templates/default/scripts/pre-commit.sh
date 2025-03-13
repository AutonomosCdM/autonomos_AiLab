#!/bin/bash

# Script de pre-commit para {{ project_name_title }}

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

# Verificar que estamos en un entorno virtual
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}Activando entorno virtual...${NC}"
    source venv/bin/activate || handle_error "No se pudo activar el entorno virtual"
fi

# Mensaje de inicio
echo -e "${BLUE}=== Ejecutando verificaciones de calidad de código ===${NC}"

# Formateo de código
echo -e "${YELLOW}Formateando código con Black...${NC}"
black . || handle_error "Formateo con Black falló"

# Organizar imports
echo -e "${YELLOW}Organizando imports con isort...${NC}"
isort . || handle_error "Organización de imports con isort falló"

# Verificación de tipos con mypy
echo -e "${YELLOW}Verificando tipos con mypy...${NC}"
mypy slack_bot || handle_error "Verificación de tipos con mypy falló"

# Linting con flake8
echo -e "${YELLOW}Realizando linting con flake8...${NC}"
flake8 slack_bot || handle_error "Linting con flake8 falló"

# Seguridad con safety
echo -e "${YELLOW}Verificando dependencias con safety...${NC}"
safety check || handle_error "Verificación de seguridad con safety falló"

# Ejecutar pruebas
echo -e "${YELLOW}Ejecutando pruebas con pytest...${NC}"
pytest --cov=slack_bot --cov-report=term-missing || handle_error "Las pruebas fallaron"

# Mensaje de éxito
echo -e "${GREEN}✅ Todas las verificaciones de código pasaron exitosamente${NC}"
