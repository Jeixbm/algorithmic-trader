# state_manager.py
import json
import os
from logger import log

class StateManager:
    """
    Gestiona el estado del bot, guardando y cargando datos de un archivo JSON.
    Esto permite que el bot recuerde sus operaciones entre reinicios.
    """
    def __init__(self, state_file='state.json'):
        """
        Inicializa el gestor de estado.
        :param state_file: El nombre del archivo donde se guardará el estado.
        """
        self.state_file = state_file
        log.info(f"Módulo de Estado inicializado. Archivo de estado: '{self.state_file}'")

    def save_state(self, state_data):
        """
        Guarda el diccionario de estado proporcionado en el archivo JSON.
        
        :param state_data: Un diccionario que representa el estado actual del bot.
        """
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state_data, f, indent=4)
            log.info(f"Estado guardado exitosamente en '{self.state_file}'.")
        except IOError as e:
            log.error(f"Error al guardar el estado en '{self.state_file}': {e}")

    def load_state(self):
        """
        Carga el estado desde el archivo JSON.
        
        :return: Un diccionario con el estado del bot. Si el archivo no existe o está vacío,
                 devuelve un diccionario vacío.
        """
        if not os.path.exists(self.state_file):
            log.warning(f"No se encontró el archivo de estado '{self.state_file}'. Se creará uno nuevo. Empezando con un estado vacío.")
            return {}
        
        try:
            with open(self.state_file, 'r') as f:
                # Comprobar si el archivo está vacío
                if os.path.getsize(self.state_file) == 0:
                    log.warning(f"El archivo de estado '{self.state_file}' está vacío. Empezando con un estado vacío.")
                    return {}
                state_data = json.load(f)
                log.info(f"Estado cargado exitosamente desde '{self.state_file}'.")
                return state_data
        except (IOError, json.JSONDecodeError) as e:
            log.error(f"Error al cargar o decodificar el estado desde '{self.state_file}': {e}. Empezando con un estado vacío.")
            return {}