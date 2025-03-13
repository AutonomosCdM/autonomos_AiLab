# Bot de Slack con Groq API

Un bot de Slack simple que responde a mensajes utilizando la API de Groq.

## Requisitos Previos

- Python 3.6 o superior
- Un espacio de trabajo de Slack con permisos de administrador
- Tokens de bot y app de Slack
- Clave API de Groq

## Configuración de la App de Slack

1. Ve a [https://api.slack.com/apps](https://api.slack.com/apps)
2. Haz clic en "Create New App" y selecciona "From scratch"
3. Ingresa un nombre para tu app (ej., "Lucius") y selecciona tu espacio de trabajo
4. En "Add features and functionality", selecciona "Socket Mode" y habilítalo
   - Esto generará tu Token de Nivel de Aplicación (comienza con `xapp-`)
5. En "Add features and functionality", selecciona "Bots"
   - Haz clic en "Add a Bot User" y configura el nombre de visualización y nombre de usuario
6. En "OAuth & Permissions", desplázate hasta "Scopes" y agrega los siguientes alcances de Bot Token:
   - `chat:write` - Enviar mensajes como la app
   - `app_mentions:read` - Ver mensajes que mencionan a la app
   - `channels:history` - Ver mensajes en canales
   - `channels:read` - Ver información básica sobre canales
   - `groups:history` - Ver mensajes en canales privados
   - `im:history` - Ver mensajes en mensajes directos
   - `mpim:history` - Ver mensajes en mensajes directos grupales
7. Instala la app en tu espacio de trabajo haciendo clic en "Install to Workspace"
   - Esto generará tu Token OAuth de Usuario Bot (comienza con `xoxb-`)
8. Invita a tu bot al canal donde quieres que opere:
   - En Slack, ve al canal
   - Escribe `/invite @NombreDeTuBot`

## Configuración Local

1. Clona este repositorio o descarga los archivos

2. Crea un entorno virtual y actívalo:
   ```
   python3 -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. Instala las dependencias requeridas:
   ```
   pip install -r requirements.txt
   ```

4. Configura tus variables de entorno en el archivo `.env`:
   ```
   SLACK_BOT_TOKEN=xoxb-tu-token-de-bot
   SLACK_APP_TOKEN=xapp-tu-token-de-app
   GROQ_API_KEY=tu-clave-api-de-groq
   SLACK_CHANNEL=tu-id-de-canal
   ```
   
   Asegúrate de reemplazar los valores de ejemplo con tus tokens reales.

## Ejecutando el Bot Localmente

1. Prueba la conexión a Slack:
   ```
   python test_bot.py
   ```
   Si es exitoso, deberías ver información sobre la conexión.

2. Ejecuta el bot:
   ```
   python app.py
   ```
   El bot se conectará a Slack y responderá a:
   - Mensajes directos enviados al bot
   - Menciones en canales (usando @NombreDeTuBot)

## Despliegue en Google Compute Engine

Este proyecto incluye un script de despliegue automatizado para Google Compute Engine que configura todo lo necesario para ejecutar el bot como un servicio.

### Requisitos para el Despliegue

1. Tener instalado Google Cloud SDK (gcloud) en tu máquina local
2. Estar autenticado con `gcloud auth login`
3. Tener un proyecto de Google Cloud configurado

### Pasos para el Despliegue

1. Asegúrate de que el archivo `.env` contenga tus tokens correctos

2. Ejecuta el script de despliegue:
   ```
   ./deploy_to_gce.sh [nombre-instancia] [zona]
   ```
   
   Ejemplo:
   ```
   ./deploy_to_gce.sh slack-bot-instance us-central1-a
   ```
   
   Zonas elegibles para el nivel gratuito:
   - us-east1 (Carolina del Sur)
   - us-west1 (Oregón)
   - us-central1 (Iowa)

3. El script realizará automáticamente:
   - Creación de una instancia e2-micro (si no existe)
   - Transferencia de archivos a la instancia
   - Instalación de dependencias
   - Configuración del bot como un servicio usando supervisor
   - Inicio del servicio

4. Una vez completado, el bot estará ejecutándose permanentemente en la instancia de GCE

### Comandos Útiles Post-Despliegue

Para verificar el estado del bot:
```
gcloud compute ssh [nombre-instancia] --zone=[zona] --command="sudo supervisorctl status slack_bot"
```

Para ver los logs del bot:
```
gcloud compute ssh [nombre-instancia] --zone=[zona] --command="tail -f ~/slack_bot/slack_bot.log"
```

Para reiniciar el bot:
```
gcloud compute ssh [nombre-instancia] --zone=[zona] --command="sudo supervisorctl restart slack_bot"
```

## Solución de Problemas

### Error: account_inactive

Este error típicamente significa uno de los siguientes:
- El token del bot es inválido o expiró
- La app de Slack ha sido desactivada
- El usuario bot ha sido removido del espacio de trabajo

Soluciones:
1. Verifica que tus tokens sean correctos en el archivo `.env`
2. Asegúrate de que tu app de Slack esté instalada en tu espacio de trabajo
3. Verifica que el usuario bot esté activo y haya sido invitado al canal
4. Regenera tus tokens si es necesario yendo a la configuración de tu app de Slack

### Error: invalid_auth

Este error significa que el token de autenticación es inválido.

Soluciones:
1. Verifica que estés usando el formato correcto de token:
   - El token de bot comienza con `xoxb-`
   - El token de app comienza con `xapp-`
2. Regenera tus tokens en el panel de control de la API de Slack
