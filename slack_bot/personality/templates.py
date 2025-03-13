"""
Sistema de plantillas para prompts y respuestas.
"""
import logging
import re
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class PromptTemplate:
    """
    Clase para gestionar plantillas de prompts para el modelo de IA.
    """
    
    def __init__(self, template: str):
        """
        Inicializa una plantilla de prompt.
        
        Args:
            template (str): Texto de la plantilla con marcadores de posición.
                Los marcadores deben tener el formato {nombre_variable}.
        """
        self.template = template
        self._validate_template()
        logger.debug(f"PromptTemplate inicializado: {template[:50]}...")
    
    def _validate_template(self) -> None:
        """
        Valida que la plantilla tenga un formato correcto.
        
        Raises:
            ValueError: Si la plantilla tiene un formato incorrecto.
        """
        # Verificar que los marcadores tengan el formato correcto
        placeholders = re.findall(r'{([^{}]*)}', self.template)
        
        # Verificar que no haya marcadores duplicados
        if len(placeholders) != len(set(placeholders)):
            duplicates = set([p for p in placeholders if placeholders.count(p) > 1])
            raise ValueError(f"La plantilla contiene marcadores duplicados: {duplicates}")
    
    def format(self, **kwargs) -> str:
        """
        Formatea la plantilla con los valores proporcionados.
        
        Args:
            **kwargs: Valores para los marcadores de posición.
            
        Returns:
            str: Plantilla formateada.
            
        Raises:
            KeyError: Si falta algún valor para un marcador.
        """
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            logger.error(f"Falta valor para el marcador {e}", exc_info=True)
            raise KeyError(f"Falta valor para el marcador {e}")
    
    def get_placeholders(self) -> list:
        """
        Obtiene la lista de marcadores de posición en la plantilla.
        
        Returns:
            list: Lista de nombres de marcadores.
        """
        return re.findall(r'{([^{}]*)}', self.template)


class TemplateManager:
    """
    Gestor de plantillas para diferentes tipos de prompts y respuestas.
    """
    
    def __init__(self):
        """
        Inicializa el gestor de plantillas.
        """
        self.templates = {}
        logger.debug("TemplateManager inicializado")
    
    def register_template(self, name: str, template: str) -> None:
        """
        Registra una nueva plantilla.
        
        Args:
            name (str): Nombre de la plantilla.
            template (str): Texto de la plantilla.
        """
        try:
            self.templates[name] = PromptTemplate(template)
            logger.debug(f"Plantilla '{name}' registrada")
        except ValueError as e:
            logger.error(f"Error al registrar plantilla '{name}': {e}", exc_info=True)
            raise
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """
        Obtiene una plantilla por su nombre.
        
        Args:
            name (str): Nombre de la plantilla.
            
        Returns:
            Optional[PromptTemplate]: Plantilla encontrada, o None si no existe.
        """
        template = self.templates.get(name)
        if not template:
            logger.warning(f"Plantilla '{name}' no encontrada")
        return template
    
    def format_template(self, name: str, **kwargs) -> Optional[str]:
        """
        Formatea una plantilla con los valores proporcionados.
        
        Args:
            name (str): Nombre de la plantilla.
            **kwargs: Valores para los marcadores de posición.
            
        Returns:
            Optional[str]: Plantilla formateada, o None si la plantilla no existe.
        """
        template = self.get_template(name)
        if not template:
            return None
        
        try:
            return template.format(**kwargs)
        except KeyError as e:
            logger.error(f"Error al formatear plantilla '{name}': {e}", exc_info=True)
            return None
    
    def get_available_templates(self) -> list:
        """
        Obtiene la lista de plantillas disponibles.
        
        Returns:
            list: Lista de nombres de plantillas.
        """
        return list(self.templates.keys())


# Plantillas predefinidas para prompts comunes
DEFAULT_SYSTEM_PROMPT_TEMPLATE = """
{system_instructions}

Información adicional:
- Nombre del bot: {bot_name}
- Contexto: {context}
"""

DEFAULT_USER_PROMPT_TEMPLATE = """
{user_message}
"""

DEFAULT_CONVERSATION_PROMPT_TEMPLATE = """
Historial de conversación:
{conversation_history}

Mensaje actual:
{user_message}
"""

# Inicializar gestor de plantillas con plantillas predefinidas
default_templates = {
    "system_prompt": DEFAULT_SYSTEM_PROMPT_TEMPLATE,
    "user_prompt": DEFAULT_USER_PROMPT_TEMPLATE,
    "conversation_prompt": DEFAULT_CONVERSATION_PROMPT_TEMPLATE,
}

template_manager = TemplateManager()
for name, template in default_templates.items():
    template_manager.register_template(name, template)
