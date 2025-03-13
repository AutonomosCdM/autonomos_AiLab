"""
Esquemas para validación de mensajes.
"""
import re
from typing import Dict, Any, List, Optional, Union, Callable


class ValidationError(Exception):
    """
    Excepción para errores de validación.
    """
    
    def __init__(self, message: str, field: Optional[str] = None):
        """
        Inicializa la excepción.
        
        Args:
            message (str): Mensaje de error.
            field (Optional[str]): Campo que falló la validación.
        """
        super().__init__(message)
        self.field = field


class Field:
    """
    Campo para validación de esquemas.
    """
    
    def __init__(
        self,
        required: bool = True,
        default: Any = None,
        validators: Optional[List[Callable[[Any], bool]]] = None,
        error_message: Optional[str] = None
    ):
        """
        Inicializa el campo.
        
        Args:
            required (bool): Si el campo es requerido.
            default (Any): Valor por defecto si el campo no está presente.
            validators (Optional[List[Callable[[Any], bool]]]): Funciones de validación.
            error_message (Optional[str]): Mensaje de error personalizado.
        """
        self.required = required
        self.default = default
        self.validators = validators or []
        self.error_message = error_message
    
    def validate(self, value: Any, field_name: str) -> Any:
        """
        Valida un valor según las reglas del campo.
        
        Args:
            value (Any): Valor a validar.
            field_name (str): Nombre del campo.
            
        Returns:
            Any: Valor validado.
            
        Raises:
            ValidationError: Si la validación falla.
        """
        # Verificar si el campo es requerido
        if value is None:
            if self.required:
                raise ValidationError(
                    self.error_message or f"El campo '{field_name}' es requerido",
                    field_name
                )
            return self.default
        
        # Aplicar validadores
        for validator in self.validators:
            if not validator(value):
                raise ValidationError(
                    self.error_message or f"El campo '{field_name}' no es válido",
                    field_name
                )
        
        return value


class StringField(Field):
    """
    Campo para validación de strings.
    """
    
    def __init__(
        self,
        required: bool = True,
        default: Optional[str] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        pattern: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """
        Inicializa el campo.
        
        Args:
            required (bool): Si el campo es requerido.
            default (Optional[str]): Valor por defecto si el campo no está presente.
            min_length (Optional[int]): Longitud mínima del string.
            max_length (Optional[int]): Longitud máxima del string.
            pattern (Optional[str]): Patrón regex que debe cumplir el string.
            error_message (Optional[str]): Mensaje de error personalizado.
        """
        validators = []
        
        # Validador de tipo
        validators.append(lambda v: isinstance(v, str))
        
        # Validador de longitud mínima
        if min_length is not None:
            validators.append(lambda v: len(v) >= min_length)
        
        # Validador de longitud máxima
        if max_length is not None:
            validators.append(lambda v: len(v) <= max_length)
        
        # Validador de patrón
        if pattern is not None:
            regex = re.compile(pattern)
            validators.append(lambda v: regex.match(v) is not None)
        
        super().__init__(required, default, validators, error_message)


class NumberField(Field):
    """
    Campo para validación de números.
    """
    
    def __init__(
        self,
        required: bool = True,
        default: Optional[Union[int, float]] = None,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        is_integer: bool = False,
        error_message: Optional[str] = None
    ):
        """
        Inicializa el campo.
        
        Args:
            required (bool): Si el campo es requerido.
            default (Optional[Union[int, float]]): Valor por defecto si el campo no está presente.
            min_value (Optional[Union[int, float]]): Valor mínimo.
            max_value (Optional[Union[int, float]]): Valor máximo.
            is_integer (bool): Si el valor debe ser un entero.
            error_message (Optional[str]): Mensaje de error personalizado.
        """
        validators = []
        
        # Validador de tipo
        if is_integer:
            validators.append(lambda v: isinstance(v, int))
        else:
            validators.append(lambda v: isinstance(v, (int, float)))
        
        # Validador de valor mínimo
        if min_value is not None:
            validators.append(lambda v: v >= min_value)
        
        # Validador de valor máximo
        if max_value is not None:
            validators.append(lambda v: v <= max_value)
        
        super().__init__(required, default, validators, error_message)


class BooleanField(Field):
    """
    Campo para validación de booleanos.
    """
    
    def __init__(
        self,
        required: bool = True,
        default: Optional[bool] = None,
        error_message: Optional[str] = None
    ):
        """
        Inicializa el campo.
        
        Args:
            required (bool): Si el campo es requerido.
            default (Optional[bool]): Valor por defecto si el campo no está presente.
            error_message (Optional[str]): Mensaje de error personalizado.
        """
        validators = [lambda v: isinstance(v, bool)]
        super().__init__(required, default, validators, error_message)


class Schema:
    """
    Esquema para validación de datos.
    """
    
    def __init__(self, fields: Dict[str, Field]):
        """
        Inicializa el esquema.
        
        Args:
            fields (Dict[str, Field]): Campos del esquema.
        """
        self.fields = fields
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida datos según el esquema.
        
        Args:
            data (Dict[str, Any]): Datos a validar.
            
        Returns:
            Dict[str, Any]: Datos validados.
            
        Raises:
            ValidationError: Si la validación falla.
        """
        if not isinstance(data, dict):
            raise ValidationError("Los datos deben ser un diccionario")
        
        validated_data = {}
        
        # Validar cada campo
        for field_name, field in self.fields.items():
            value = data.get(field_name)
            validated_data[field_name] = field.validate(value, field_name)
        
        return validated_data


# Esquema para mensajes de usuario
user_message_schema = Schema({
    "text": StringField(
        required=True,
        min_length=1,
        max_length=4000,
        error_message="El texto del mensaje es requerido y debe tener entre 1 y 4000 caracteres"
    ),
    "user_id": StringField(
        required=True,
        error_message="El ID de usuario es requerido"
    ),
    "channel_id": StringField(
        required=True,
        error_message="El ID de canal es requerido"
    ),
    "timestamp": StringField(
        required=False
    ),
    "is_mention": BooleanField(
        required=False,
        default=False
    )
})

# Esquema para respuestas del bot
bot_response_schema = Schema({
    "text": StringField(
        required=True,
        min_length=1,
        max_length=4000,
        error_message="El texto de la respuesta es requerido y debe tener entre 1 y 4000 caracteres"
    ),
    "channel_id": StringField(
        required=True,
        error_message="El ID de canal es requerido"
    ),
    "thread_ts": StringField(
        required=False
    ),
    "blocks": Field(
        required=False
    ),
    "attachments": Field(
        required=False
    )
})
