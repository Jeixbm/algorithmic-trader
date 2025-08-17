import time
from api_client import api_client
from logger import log
from notifier import notifier
from config import config

class ExecutionHandler:
    """
    Gestiona la colocación, monitoreo y cancelación de órdenes en el exchange.
    """
    def __init__(self, bot_mode='SIMULATED'):
        self.bot_mode = bot_mode
        log.info("Módulo de Ejecución inicializado.")

    # --- NUEVA FUNCIÓN MEJORADA ---
    def place_market_order_with_sl(self, symbol, side, amount, stop_loss, leverage):
        """
        Coloca una orden de mercado con un stop-loss asociado.
        En modo SIMULATED, solo registra la acción (paper trading).
        """
        if self.bot_mode == 'SIMULATED':
            log.info("--- MODO SIMULADO: Registrando orden en lugar de ejecutarla ---")
            log.info(f"ORDEN DE PAPEL: {side.upper()} {amount:.4f} {symbol}")
            log.info(f"PARÁMETROS: Stop-Loss=${stop_loss:.2f}, Apalancamiento={leverage}x")
            # Devolvemos un diccionario de éxito simulado
            return {
                'id': f'sim_{int(time.time())}',
                'status': 'open',
                'symbol': symbol,
                'side': side,
                'amount': amount
            }
        
        # --- LÓGICA DE TRADING REAL ---
        log.info(f"Iniciando ejecución de orden REAL para {symbol}...")
        try:
            # CCXT unifica la compra ('long') y venta ('short') con el parámetro 'side'
            # La mayoría de exchanges permiten añadir el stop-loss en los parámetros de la orden
            params = {
                'stopLoss': {
                    'type': 'stopMarket',
                    'triggerPrice': stop_loss,
                }
            }
            # Asegurarse de que el exchange esté configurado para el apalancamiento deseado
            # api_client.exchange.set_leverage(leverage, symbol) # Esta línea puede ser necesaria dependiendo del exchange

            order = api_client.exchange.create_market_order(symbol, side, amount, params=params)
            
            mensaje = (
                f"✅ **ORDEN REAL ENVIADA**\n\n"
                f"**Activo:** {symbol}\n"
                f"**Tipo:** {side.upper()} @ Mercado\n"
                f"**Cantidad:** {amount:.4f}\n"
                f"**Stop-Loss:** ${stop_loss:,.2f}"
            )
            notifier.send_message(mensaje)
            return order
        except Exception as e:
            log.error(f"Error al ejecutar la orden REAL: {e}", exc_info=True)
            notifier.send_message(f"❌ **ERROR DE EJECUCIÓN**\nNo se pudo colocar la orden para {symbol}. Error: {e}")
            return None

    # --- El resto de las funciones pueden permanecer como estaban ---
    def place_limit_order(self, product_id, side, price, amount_of_asset):
        """
        Coloca una orden límite.
        """
        if self.bot_mode == 'LIVE':
            # ... (Lógica para órdenes límite en real) ...
            pass
        else:
            log.info(f"ORDEN LÍMITE SIMULADA: {side.upper()} {amount_of_asset} {product_id} @ ${price:,.2f}")
            return {'id': f'sim_limit_{int(time.time())}', 'status': 'open'}

    def get_order_status(self, order_id, product_id):
        """
        Verifica el estado de una orden específica en el exchange.
        """
        if self.bot_mode == 'LIVE':
            # ... (Lógica para obtener estado de orden en real) ...
            pass
        else:
            log.info(f"Verificando estado de la orden simulada {order_id}.")
            return {'status': 'closed'}

# Crear una instancia para ser usada por el bot
execution_handler = ExecutionHandler(config.BOT_MODE)