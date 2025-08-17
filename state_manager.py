import json
import os
from logger import log

class StateManager:
    """
    Gestiona el estado de las operaciones abiertas guardándolo y leyéndolo
    de un archivo JSON.
    """
    def __init__(self, state_file='state.json'):
        self.state_file = state_file

    def load_state(self):
        """
        Carga el estado de las operaciones desde el archivo JSON.
        Si el archivo no existe, devuelve un diccionario vacío.
        """
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    log.info(f"Estado cargado desde '{self.state_file}': {state}")
                    return state
            except json.JSONDecodeError:
                log.warning("El archivo de estado está corrupto. Se creará uno nuevo.")
                return {}
        return {}

    def save_state(self, state):
        """
        Guarda el estado actual de las operaciones en el archivo JSON.
        """
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=4)
                log.info(f"Estado guardado en '{self.state_file}': {state}")
        except Exception as e:
            log.error(f"No se pudo guardar el estado en '{self.state_file}': {e}")

    # --- FUNCIÓN NUEVA Y CORREGIDA ---
    def is_in_position(self, symbol):
        """
        Verifica si hay una posición abierta para un símbolo específico.
        """
        active_trades = self.load_state()
        # Devuelve True si el símbolo está en las operaciones y su estado es 'open'
        return symbol in active_trades and active_trades[symbol].get('status') == 'open'

    def enter_position(self, symbol, side, size, entry_price, stop_loss_price):
        """
        Registra una nueva posición abierta en el estado.
        """
        state = self.load_state()
        state[symbol] = {
            "side": side,
            "size": size,
            "entry_price": entry_price,
            "stop_loss_price": stop_loss_price,
            "status": "open"
        }
        self.save_state(state)

    def exit_position(self, symbol):
        """
        Elimina una posición del estado (cuando se cierra).
        """
        state = self.load_state()
        if symbol in state:
            del state[symbol]
            self.save_state(state)
            log.info(f"Posición para {symbol} eliminada del estado.")