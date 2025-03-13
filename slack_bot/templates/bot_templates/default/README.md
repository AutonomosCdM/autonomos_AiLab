# {{ project_name_title }} - Bot de Slack con IA

Un bot de Slack inteligente impulsado por Groq Llama3, diseñado para proporcionar asistencia contextual y conversacional.

## 🚀 Características

- Integración nativa con Slack
- Generación de respuestas usando IA de última generación (Groq Llama3)
- Gestión de contexto conversacional
- Personalidades configurables
- Despliegue sencillo en Google Compute Engine

## 📋 Requisitos Previos

- Python 3.9+
- Cuenta de Slack Developer
- Cuenta de Groq
- Cuenta de Google Cloud (opcional, para despliegue)

## 🔧 Configuración

### 1. Clonar Repositorio

```bash
git clone https://github.com/tu-usuario/{{ project_name }}.git
cd {{ project_name }}
```

### 2. Configurar Entorno Virtual

```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

1. Copiar el archivo de ejemplo:
```bash
cp .env.example .env
```

2. Editar `.env` con tus credenciales:
- Token de bot de Slack
- Token de app de Slack
- Clave API de Groq
- Canal predeterminado

## 🤖 Ejecución Local

### Prueba de Conexión

```bash
python test_bot.py
```

### Iniciar Bot

```bash
python app.py
```

## ☁️ Despliegue en Google Compute Engine

### Requisitos

- Google Cloud SDK instalado
- Autenticación con `gcloud auth login`

### Desplegar

```bash
# Crear instancia (opcional)
./scripts/create_instance.sh mi-bot-instance us-central1-a

# Desplegar bot
./scripts/deploy.sh mi-bot-instance us-central1-a
```

## 🛠️ Herramientas CLI

### Generar Nuevo Proyecto

```bash
python -m slack_bot.cli.generate mi-nuevo-bot
```

### Desplegar Bot

```bash
python -m slack_bot.cli.deploy -i mi-bot-instance
```

## 🧪 Pruebas

```bash
pytest
```

## 📊 Monitoreo

- Logs: `~/slack_bot/slack_bot.log`
- Estado del servicio: `sudo supervisorctl status slack_bot`

## 🔒 Seguridad

- Tokens almacenados en variables de entorno
- Validación de tokens en cada solicitud
- Logging de eventos para auditoría

## 🚧 Próximas Mejoras

- Soporte multilenguaje
- Integración con más servicios
- Panel de administración

## 📄 Licencia

[Especificar licencia]

## 👥 Contribuciones

¡Las contribuciones son bienvenidas! Por favor, lee las pautas de contribución antes de enviar un pull request.

## 📧 Contacto

[Información de contacto]
