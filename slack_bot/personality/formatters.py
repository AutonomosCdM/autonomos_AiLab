"""
Formateadores de respuesta para diferentes personalidades.
"""
import logging
import re
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ResponseFormatter:
    """
    Clase base para formateadores de respuesta.
    """
    
    def format_response(self, text: str, **kwargs) -> str:
        """
        Formatea una respuesta según la configuración.
        
        Args:
            text (str): Texto de la respuesta.
            **kwargs: Opciones adicionales de formato.
            
        Returns:
            str: Respuesta formateada.
        """
        raise NotImplementedError("Las subclases deben implementar format_response")


class DefaultFormatter(ResponseFormatter):
    """
    Formateador de respuesta por defecto.
    """
    
    def __init__(self, response_config: Optional[Dict[str, Any]] = None):
        """
        Inicializa el formateador con una configuración.
        
        Args:
            response_config (Optional[Dict[str, Any]]): Configuración de respuesta.
                Si es None, se usa una configuración por defecto.
        """
        self.response_config = response_config or {
            "max_length": 500,
            "tone": "amigable",
            "format": "texto",
        }
        logger.debug(f"DefaultFormatter inicializado con config: {self.response_config}")
    
    def format_response(self, text: str, **kwargs) -> str:
        """
        Formatea una respuesta según la configuración.
        
        Args:
            text (str): Texto de la respuesta.
            **kwargs: Opciones adicionales de formato.
                - max_length (int): Longitud máxima de la respuesta.
                - tone (str): Tono de la respuesta.
                - format (str): Formato de la respuesta.
            
        Returns:
            str: Respuesta formateada.
        """
        # Combinar configuración por defecto con opciones adicionales
        config = {**self.response_config, **kwargs}
        
        # Aplicar longitud máxima
        max_length = config.get("max_length", 500)
        if len(text) > max_length:
            text = text[:max_length-3] + "..."
        
        # Aplicar formato según configuración
        format_type = config.get("format", "texto")
        if format_type == "markdown":
            # No hacemos nada, ya que el texto ya debería estar en markdown
            pass
        elif format_type == "texto":
            # Eliminar formato markdown si está presente
            text = self._remove_markdown(text)
        
        # Aplicar emojis según configuración de comportamiento
        emoji_use = config.get("emoji_use", "moderado")
        if emoji_use == "ninguno":
            text = self._remove_emojis(text)
        elif emoji_use == "abundante":
            text = self._enhance_emojis(text)
        
        return text
    
    def _remove_markdown(self, text: str) -> str:
        """
        Elimina formato markdown del texto.
        
        Args:
            text (str): Texto con formato markdown.
            
        Returns:
            str: Texto sin formato markdown.
        """
        # Eliminar encabezados
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
        
        # Eliminar negrita y cursiva
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        text = re.sub(r'__(.*?)__', r'\1', text)
        text = re.sub(r'_(.*?)_', r'\1', text)
        
        # Eliminar bloques de código
        text = re.sub(r'```.*?\n(.*?)```', r'\1', text, flags=re.DOTALL)
        text = re.sub(r'`(.*?)`', r'\1', text)
        
        # Eliminar listas
        text = re.sub(r'^\s*[-*+]\s+', '- ', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
        
        # Eliminar enlaces
        text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
        
        return text
    
    def _remove_emojis(self, text: str) -> str:
        """
        Elimina emojis del texto.
        
        Args:
            text (str): Texto con emojis.
            
        Returns:
            str: Texto sin emojis.
        """
        # Patrón simple para detectar emojis comunes
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticones
            "\U0001F300-\U0001F5FF"  # símbolos y pictogramas
            "\U0001F680-\U0001F6FF"  # transporte y símbolos de mapas
            "\U0001F700-\U0001F77F"  # alchemical symbols
            "\U0001F780-\U0001F7FF"  # Geometric Shapes
            "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            "\U0001FA00-\U0001FA6F"  # Chess Symbols
            "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            "\U00002702-\U000027B0"  # Dingbats
            "\U000024C2-\U0001F251" 
            "]+", flags=re.UNICODE)
        
        return emoji_pattern.sub(r'', text)
    
    def _enhance_emojis(self, text: str) -> str:
        """
        Añade más emojis al texto según el contexto.
        
        Args:
            text (str): Texto original.
            
        Returns:
            str: Texto con más emojis.
        """
        # Esta es una implementación simple que añade emojis al final de oraciones
        # En una implementación real, se podría usar NLP para identificar el sentimiento
        # y añadir emojis apropiados según el contexto
        
        # Añadir emoji al final si no hay ya uno
        if not re.search(r'[\U0001F300-\U0001F9FF]\s*$', text):
            text += " 😊"
        
        # Añadir emojis a algunas palabras clave
        emoji_mappings = {
            r'\b(?:gracias|agradec\w+)\b': ' 🙏',
            r'\b(?:excelente|genial|increíble|asombroso)\b': ' 🎉',
            r'\b(?:problema|error|fallo)\b': ' 😅',
            r'\b(?:ayuda|ayudar)\b': ' 🆘',
            r'\b(?:código|programación|desarrollar)\b': ' 💻',
            r'\b(?:idea|pensar|considerar)\b': ' 💡',
        }
        
        for pattern, emoji in emoji_mappings.items():
            text = re.sub(pattern, lambda m: m.group(0) + emoji, text, flags=re.IGNORECASE)
        
        return text


class MarkdownFormatter(ResponseFormatter):
    """
    Formateador de respuesta para formato markdown.
    """
    
    def __init__(self, response_config: Optional[Dict[str, Any]] = None):
        """
        Inicializa el formateador con una configuración.
        
        Args:
            response_config (Optional[Dict[str, Any]]): Configuración de respuesta.
                Si es None, se usa una configuración por defecto.
        """
        self.response_config = response_config or {
            "max_length": 800,
            "tone": "técnico",
            "format": "markdown",
        }
        logger.debug(f"MarkdownFormatter inicializado con config: {self.response_config}")
    
    def format_response(self, text: str, **kwargs) -> str:
        """
        Formatea una respuesta en markdown según la configuración.
        
        Args:
            text (str): Texto de la respuesta.
            **kwargs: Opciones adicionales de formato.
                - max_length (int): Longitud máxima de la respuesta.
                - headers (bool): Si se deben incluir encabezados.
                - code_blocks (bool): Si se deben formatear bloques de código.
            
        Returns:
            str: Respuesta formateada en markdown.
        """
        # Combinar configuración por defecto con opciones adicionales
        config = {**self.response_config, **kwargs}
        
        # Aplicar longitud máxima
        max_length = config.get("max_length", 800)
        if len(text) > max_length:
            text = text[:max_length-3] + "..."
        
        # Asegurar que el texto esté en formato markdown
        text = self._ensure_markdown(text, config)
        
        return text
    
    def _ensure_markdown(self, text: str, config: Dict[str, Any]) -> str:
        """
        Asegura que el texto esté en formato markdown.
        
        Args:
            text (str): Texto original.
            config (Dict[str, Any]): Configuración de formato.
            
        Returns:
            str: Texto en formato markdown.
        """
        # Verificar si ya tiene formato markdown
        has_markdown = (
            re.search(r'^#+\s+', text, re.MULTILINE) or  # Encabezados
            re.search(r'\*\*(.*?)\*\*', text) or  # Negrita
            re.search(r'\*(.*?)\*', text) or  # Cursiva
            re.search(r'```', text) or  # Bloques de código
            re.search(r'^\s*[-*+]\s+', text, re.MULTILINE) or  # Listas
            re.search(r'\[(.*?)\]\(.*?\)', text)  # Enlaces
        )
        
        if has_markdown:
            return text
        
        # Aplicar formato markdown básico
        
        # Detectar posibles encabezados (líneas cortas seguidas de líneas en blanco)
        if config.get("headers", True):
            lines = text.split('\n')
            for i in range(len(lines)):
                if i > 0 and lines[i-1].strip() == '' and i < len(lines)-1 and lines[i+1].strip() == '':
                    if len(lines[i]) <= 50 and lines[i].strip() and not lines[i].strip().endswith(':'):
                        lines[i] = f"## {lines[i]}"
            text = '\n'.join(lines)
        
        # Detectar posibles bloques de código (indentados o con patrones comunes)
        if config.get("code_blocks", True):
            code_patterns = [
                r'((?:^|\n)(?:\s{4}|\t).*(?:\n(?:\s{4}|\t).*)*)',  # Indentado
                r'((?:^|\n)(?:import|from|def|class|if|for|while|return|function|var|let|const).*(?:\n(?!$).*)*)',  # Palabras clave de programación
            ]
            
            for pattern in code_patterns:
                text = re.sub(
                    pattern,
                    lambda m: f"\n```\n{m.group(1).strip()}\n```\n",
                    text
                )
        
        return text


class FormatterFactory:
    """
    Fábrica para crear formateadores de respuesta según la configuración.
    """
    
    @staticmethod
    def create_formatter(response_config: Dict[str, Any]) -> ResponseFormatter:
        """
        Crea un formateador según la configuración.
        
        Args:
            response_config (Dict[str, Any]): Configuración de respuesta.
            
        Returns:
            ResponseFormatter: Formateador de respuesta.
        """
        format_type = response_config.get("format", "texto")
        
        if format_type == "markdown":
            return MarkdownFormatter(response_config)
        else:
            return DefaultFormatter(response_config)
