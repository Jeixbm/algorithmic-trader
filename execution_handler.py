# trading_bot/execution_handler.py
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

    def place_market_order(self, product_id, side, amount_in_quote):
        """
        Coloca una orden de mercado.
        
        :param product_id: El par de trading (ej. 'SOL/USD').
        :param side: 'buy' o 'sell'.
        :param amount_in_quote: La cantidad de dinero (ej. en USD) a gastar.
        :return: El resultado de la orden desde la API, o None si falla.
        """
        if self.bot_mode == 'LIVE':
            try:
                log.info(f"Colocando orden de mercado REAL: {side.upper()} {amount_in_quote:.2f} de {product_id}")
                order = api_client.client.create_market_order_with_cost(product_id, side, amount_in_quote)
                notifier.send_message(f"✅ **ORDEN REAL ENVIADA**\n\n**Activo:** {product_id}\n**Tipo:** {side.upper()}\n**Costo Aprox:** ${amount_in_quote:,.2f}")
                return order
            except Exception as e:
                log.error(f"Error al colocar la orden de mercado REAL: {e}")
                notifier.send_message(f"❌ **ERROR DE EJECUCIÓN**\nNo se pudo colocar la orden para {product_id}. Error: {e}")
                return None
        else:
            log.info(f"ORDEN SIMULADA: {side.upper()} {amount_in_quote:.2f} de {product_id}")
            return {'id': f'sim_{int(time.time())}', 'symbol': product_id, 'side': side, 'cost': amount_in_quote, 'status': 'closed'}

    def place_limit_order(self, product_id, side, price, amount_of_asset):
        """
        Coloca una orden límite.
        
        :param product_id: El par de trading (ej. 'SOL/USD').
        :param side: 'buy' o 'sell'.
        :param price: El precio exacto al que se debe ejecutar la orden.
        :param amount_of_asset: La cantidad del activo a comprar/vender (ej. 0.5 SOL).
        :return: El resultado de la orden desde la API, o None si falla.
        """
        if self.bot_mode == 'LIVE':
            try:
                log.info(f"Colocando orden límite REAL: {side.upper()} {amount_of_asset} {product_id} @ ${price:,.2f}")
                
                order = api_client.client.create_limit_order(product_id, side, amount_of_asset, price)
                
                mensaje = (
                    f"✅ **ORDEN LÍMITE CREADA**\n\n"
                    f"**Activo:** {product_id}\n"
                    f"**Tipo:** {side.upper()} Límite\n"
                    f"**Precio:** ${price:,.2f}\n"
                    f"**Cantidad:** {amount_of_asset}"
                )
                notifier.send_message(mensaje)
                return order

            except Exception as e:
                log.error(f"Error al colocar la orden límite REAL: {e}")
                notifier.send_message(f"❌ **ERROR DE EJECUCIÓN**\nNo se pudo colocar la orden límite para {product_id}. Error: {e}")
                return None
        else:
            log.info(f"ORDEN LÍMITE SIMULADA: {side.upper()} {amount_of_asset} {product_id} @ ${price:,.2f}")
            return {'id': f'sim_limit_{int(time.time())}', 'symbol': product_id, 'side': side, 'price': price, 'amount': amount_of_asset, 'status': 'open'}

    def get_order_status(self, order_id, product_id):
        """
        Verifica el estado de una orden específica en el exchange.
        """
        if self.bot_mode == 'LIVE':
            try:
                log.info(f"Verificando estado de la orden {order_id} para {product_id}...")
                order_status = api_client.client.fetch_order(order_id, product_id)
                return order_status
            except Exception as e:
                log.error(f"No se pudo verificar el estado de la orden {order_id}: {e}")
                return None
        else:
            log.info(f"Verificando estado de la orden simulada {order_id}.")
            # En simulación, para probar la lógica de sincronización, podemos simular que a veces
            # la orden se cierra y a veces sigue abierta. Por ahora, asumimos que siempre se ejecuta.
            return {'status': 'closed'} 

# Crear una instancia para ser usada por el bot
execution_handler = ExecutionHandler(config.BOT_MODE)