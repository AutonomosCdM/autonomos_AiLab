"""
Implementación de almacenamiento en memoria para el contexto.
"""
import logging
import time
import json
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class MemoryStore:
    """
    Almacenamiento en memoria para el contexto de conversaciones.
    """
    
    def __init__(self):
        """
        Inicializa el almacenamiento en memoria.
        """
        self.store = {}
        logger.debug("MemoryStore inicializado")
    
    def save(self, key: str, data: Any) -> bool:
        """
        Guarda datos en el almacenamiento.
        
        Args:
            key (str): Clave para identificar los datos.
            data (Any): Datos a guardar.
            
        Returns:
            bool: True si se guardó correctamente, False en caso contrario.
        """
        try:
            self.store[key] = {
                "data": data,
                "timestamp": time.time()
            }
            logger.debug(f"Datos guardados con clave {key}")
            return True
        except Exception as e:
            logger.error(f"Error al guardar datos con clave {key}: {e}", exc_info=True)
            return False
    
    def load(self, key: str) -> Optional[Any]:
        """
        Carga datos del almacenamiento.
        
        Args:
            key (str): Clave para identificar los datos.
            
        Returns:
            Optional[Any]: Datos cargados, o None si no existen.
        """
        if key not in self.store:
            logger.debug(f"Clave {key} no encontrada en el almacenamiento")
            return None
        
        return self.store[key]["data"]
    
    def delete(self, key: str) -> bool:
        """
        Elimina datos del almacenamiento.
        
        Args:
            key (str): Clave para identificar los datos.
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario.
        """
        if key in self.store:
            del self.store[key]
            logger.debug(f"Datos con clave {key} eliminados")
            return True
        
        logger.debug(f"Clave {key} no encontrada para eliminar")
        return False
    
    def exists(self, key: str) -> bool:
        """
        Verifica si una clave existe en el almacenamiento.
        
        Args:
            key (str): Clave a verificar.
            
        Returns:
            bool: True si la clave existe, False en caso contrario.
        """
        return key in self.store
    
    def get_timestamp(self, key: str) -> Optional[float]:
        """
        Obtiene el timestamp de cuando se guardaron los datos.
        
        Args:
            key (str): Clave para identificar los datos.
            
        Returns:
            Optional[float]: Timestamp en segundos desde epoch, o None si la clave no existe.
        """
        if key not in self.store:
            return None
        
        return self.store[key]["timestamp"]
    
    def get_all_keys(self) -> List[str]:
        """
        Obtiene todas las claves en el almacenamiento.
        
        Returns:
            List[str]: Lista de claves.
        """
        return list(self.store.keys())
    
    def clear(self) -> None:
        """
        Limpia todo el almacenamiento.
        """
        self.store.clear()
        logger.debug("Almacenamiento limpiado")


class PersistentMemoryStore(MemoryStore):
    """
    Almacenamiento en memoria con persistencia a disco.
    """
    
    def __init__(self, file_path: str):
        """
        Inicializa el almacenamiento con persistencia.
        
        Args:
            file_path (str): Ruta del archivo para persistencia.
        """
        super().__init__()
        self.file_path = file_path
        self._load_from_disk()
        logger.debug(f"PersistentMemoryStore inicializado con archivo {file_path}")
    
    def _load_from_disk(self) -> None:
        """
        Carga los datos desde el archivo de persistencia.
        """
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                self.store = data
                logger.debug(f"Datos cargados desde {self.file_path}")
        except FileNotFoundError:
            logger.debug(f"Archivo {self.file_path} no encontrado, se creará al guardar")
        except json.JSONDecodeError:
            logger.error(f"Error al decodificar JSON desde {self.file_path}", exc_info=True)
        except Exception as e:
            logger.error(f"Error al cargar datos desde {self.file_path}: {e}", exc_info=True)
    
    def _save_to_disk(self) -> bool:
        """
        Guarda los datos en el archivo de persistencia.
        
        Returns:
            bool: True si se guardó correctamente, False en caso contrario.
        """
        try:
            with open(self.file_path, 'w') as f:
                json.dump(self.store, f)
                logger.debug(f"Datos guardados en {self.file_path}")
            return True
        except Exception as e:
            logger.error(f"Error al guardar datos en {self.file_path}: {e}", exc_info=True)
            return False
    
    def save(self, key: str, data: Any) -> bool:
        """
        Guarda datos en el almacenamiento y persiste a disco.
        
        Args:
            key (str): Clave para identificar los datos.
            data (Any): Datos a guardar.
            
        Returns:
            bool: True si se guardó correctamente, False en caso contrario.
        """
        result = super().save(key, data)
        if result:
            return self._save_to_disk()
        return result
    
    def delete(self, key: str) -> bool:
        """
        Elimina datos del almacenamiento y persiste a disco.
        
        Args:
            key (str): Clave para identificar los datos.
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario.
        """
        result = super().delete(key)
        if result:
            return self._save_to_disk()
        return result
    
    def clear(self) -> None:
        """
        Limpia todo el almacenamiento y persiste a disco.
        """
        super().clear()
        self._save_to_disk()
