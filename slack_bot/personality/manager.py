"""
Gestor de personalidad para el bot de Slack.
"""
import importlib
import logging
from typing import Dict, Any, Optional

from slack_bot.config import settings

logger = logging.getLogger(__name__)


class PersonalityManager:
    """
    Gestor de personalidad que maneja diferentes configuraciones de comportamiento del bot.
    """
    
    def __init__(self, default_personality: str = None):
        """
        Inicializa el gestor de personalidad.
        
        Args:
            default_personality (str, optional): Nombre de la personalidad por defecto.
                Si es None, se usa la configurada en settings.
        """
        self.default_personality = default_personality or settings.DEFAULT_PERSONALITY
        self.personalities = {}
        self.active_personality = self.default_personality
        
        # Cargar personalidad por defecto
        self._load_personality(self.default_personality)
        
        logger.debug(f"PersonalityManager inicializado con personalidad por defecto: {self.default_personality}")
    
    def _load_personality(self, personality_name: str) -> bool:
        """
        Carga una configuración de personalidad.
        
        Args:
            personality_name (str): Nombre de la personalidad a cargar.
            
        Returns:
            bool: True si la carga fue exitosa, False en caso contrario.
        """
        if personality_name in self.personalities:
            logger.debug(f"Personalidad {personality_name} ya está cargada")
            return True
        
        try:
            # Importar módulo de personalidad
            module_path = f"slack_bot.config.personalities.{personality_name}"
            personality_module = importlib.import_module(module_path)
            
            # Verificar si existe PERSONALITY_CONFIG
            if hasattr(personality_module, "PERSONALITY_CONFIG"):
                # Usar PERSONALITY_CONFIG
                personality_config = personality_module.PERSONALITY_CONFIG
                # Asegurarse de que tenga todos los campos necesarios
                if "name" not in personality_config:
                    personality_config["name"] = personality_name
            else:
                # Crear diccionario de configuración desde variables individuales
                personality_config = {
                    "name": personality_name,
                    "system_prompt": getattr(personality_module, "SYSTEM_PROMPT", ""),
                    "response_config": getattr(personality_module, "RESPONSE_CONFIG", {}),
                    "behavior_config": getattr(personality_module, "BEHAVIOR_CONFIG", {}),
                    "templates": getattr(personality_module, "TEMPLATES", {})
                }
            
            # Almacenar configuración
            self.personalities[personality_name] = personality_config
            logger.info(f"Personalidad {personality_name} cargada exitosamente")
            return True
        except (ImportError, AttributeError) as e:
            logger.error(f"Error al cargar personalidad {personality_name}: {e}", exc_info=True)
            return False
    
    def set_active_personality(self, personality_name: str) -> bool:
        """
        Establece la personalidad activa.
        
        Args:
            personality_name (str): Nombre de la personalidad a activar.
            
        Returns:
            bool: True si el cambio fue exitoso, False en caso contrario.
        """
        # Cargar personalidad si no está cargada
        if personality_name not in self.personalities:
            if not self._load_personality(personality_name):
                logger.error(f"No se pudo activar la personalidad {personality_name}")
                return False
        
        # Establecer como activa
        self.active_personality = personality_name
        logger.info(f"Personalidad activa cambiada a {personality_name}")
        return True
    
    def get_system_prompt(self, personality_name: Optional[str] = None) -> str:
        """
        Obtiene el prompt de sistema para la personalidad especificada.
        
        Args:
            personality_name (Optional[str]): Nombre de la personalidad.
                Si es None, se usa la personalidad activa.
                
        Returns:
            str: Prompt de sistema.
        """
        personality = personality_name or self.active_personality
        
        if personality not in self.personalities:
            if not self._load_personality(personality):
                logger.warning(f"Personalidad {personality} no encontrada, usando la activa")
                personality = self.active_personality
        
        return self.personalities[personality].get("system_prompt", "")
    
    def get_response_config(self, personality_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtiene la configuración de respuesta para la personalidad especificada.
        
        Args:
            personality_name (Optional[str]): Nombre de la personalidad.
                Si es None, se usa la personalidad activa.
                
        Returns:
            Dict[str, Any]: Configuración de respuesta.
        """
        personality = personality_name or self.active_personality
        
        if personality not in self.personalities:
            if not self._load_personality(personality):
                logger.warning(f"Personalidad {personality} no encontrada, usando la activa")
                personality = self.active_personality
        
        return self.personalities[personality].get("response_config", {})
    
    def get_behavior_config(self, personality_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtiene la configuración de comportamiento para la personalidad especificada.
        
        Args:
            personality_name (Optional[str]): Nombre de la personalidad.
                Si es None, se usa la personalidad activa.
                
        Returns:
            Dict[str, Any]: Configuración de comportamiento.
        """
        personality = personality_name or self.active_personality
        
        if personality not in self.personalities:
            if not self._load_personality(personality):
                logger.warning(f"Personalidad {personality} no encontrada, usando la activa")
                personality = self.active_personality
        
        return self.personalities[personality].get("behavior_config", {})
    
    def get_template(self, template_name: str, personality_name: Optional[str] = None) -> str:
        """
        Obtiene una plantilla de respuesta para la personalidad especificada.
        
        Args:
            template_name (str): Nombre de la plantilla.
            personality_name (Optional[str]): Nombre de la personalidad.
                Si es None, se usa la personalidad activa.
                
        Returns:
            str: Plantilla de respuesta.
        """
        personality = personality_name or self.active_personality
        
        if personality not in self.personalities:
            if not self._load_personality(personality):
                logger.warning(f"Personalidad {personality} no encontrada, usando la activa")
                personality = self.active_personality
        
        templates = self.personalities[personality].get("templates", {})
        template = templates.get(template_name, "")
        
        if not template:
            logger.warning(f"Plantilla '{template_name}' no encontrada para personalidad '{personality}'")
        
        return template
    
    def get_available_personalities(self) -> list:
        """
        Obtiene la lista de personalidades disponibles.
        
        Returns:
            list: Lista de nombres de personalidades.
        """
        return list(self.personalities.keys())
