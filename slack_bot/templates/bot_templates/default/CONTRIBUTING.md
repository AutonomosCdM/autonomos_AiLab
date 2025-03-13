# Contribuyendo a {{ project_name_title }}

¡Gracias por tu interés en contribuir a {{ project_name_title }}! Este documento proporciona pautas para contribuir al proyecto.

## 🤝 Cómo Contribuir

### Informes de Errores

1. Verifica los [issues existentes](link-a-issues) para asegurarte de que no se haya reportado previamente.
2. Usa la plantilla de issue proporcionada.
3. Incluye:
   - Descripción del error
   - Pasos para reproducirlo
   - Comportamiento esperado
   - Entorno (SO, versión de Python, etc.)

### Solicitudes de Funcionalidades

1. Abre un issue para discutir la funcionalidad propuesta.
2. Proporciona:
   - Descripción clara
   - Caso de uso
   - Posible implementación

### Pull Requests

1. Bifurca el repositorio
2. Crea una rama para tu contribución
   ```bash
   git checkout -b feature/nombre-descriptivo
   ```
3. Sigue las pautas de codificación

## 🛠️ Configuración de Desarrollo

### Requisitos Previos

- Python 3.9+
- pip
- venv

### Configuración del Entorno

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/{{ project_name }}.git
cd {{ project_name }}

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## 📋 Proceso de Desarrollo

### Estándares de Código

- Usa `black` para formateo
- Usa `isort` para organizar imports
- Usa `mypy` para tipado estático
- Usa `flake8` para linting

### Comandos de Desarrollo

```bash
# Formatear código
black .
isort .

# Verificar tipos
mypy slack_bot

# Ejecutar pruebas
pytest

# Ejecutar todas las verificaciones
./scripts/pre-commit.sh
```

### Pruebas

- Escribe pruebas para nuevas funcionalidades
- Asegúrate de que todas las pruebas pasen
- Mantén o aumenta la cobertura de código

## 🔍 Revisión de Código

1. Todos los PRs requieren revisión
2. Mantén los commits pequeños y enfocados
3. Proporciona una descripción clara del cambio

### Proceso de Revisión

- Un revisor debe aprobar el PR
- Todas las verificaciones de CI deben pasar
- Resuelve cualquier comentario de revisión

## 📝 Guía de Estilo

### Documentación

- Usa docstrings para todas las funciones y clases
- Documenta parámetros, retornos y posibles excepciones
- Mantén la documentación actualizada

### Mensajes de Commit

```
<tipo>: <descripción corta>

[cuerpo opcional]

[pie opcional]
```

#### Tipos de Commit
- `feat`: Nueva funcionalidad
- `fix`: Corrección de errores
- `docs`: Cambios en documentación
- `style`: Formateo de código
- `refactor`: Restructuración de código
- `test`: Añadir o modificar pruebas
- `chore`: Tareas de mantenimiento

## 🔒 Código de Conducta

- Sé respetuoso
- Sé inclusivo
- Colabora constructivamente

## 📬 Contacto

- Abre un issue para preguntas
- Consulta el README para más información

## 🏆 Reconocimientos

Los contribuyentes serán reconocidos en el archivo CONTRIBUTORS.md.

¡Gracias por hacer {{ project_name_title }} mejor! 🚀
