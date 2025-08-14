# main.py
import time
import pandas as pd
import pandas_ta as ta
from logger import log
import health_checker
from config import config
from api_client import api_client
from strategy import Strategy
from risk_manager import RiskManager
from state_manager import StateManager
from notifier import notifier
from execution_handler import execution_handler

def main():
    log.info("==============================================")
    log.info(f"    INICIANDO BOT (ESTRATEGIA SOLANA OPTIMIZADA) - MODO: {config.BOT_MODE}    ")
    log.info("==============================================")
    notifier.send_message(f"✅ **Bot Iniciado**\nModo: {config.BOT_MODE}\nActivo: SOL/USD\nTemporalidad: 6h")

    if not health_checker.perform_initial_checks(): 
        notifier.send_message("❌ **Error Crítico**\nEl bot no superó los chequeos de salud y se apagará.")
        return

    # --- Parámetros Óptimos para Solana ---
    strategy_params_sol = {'fast': 20, 'slow': 60, 'rsi_period': 21, 'rsi_threshold': 55}
    risk_params_sol = {'risk_per_trade': 0.02, 'atr_period': 14, 'atr_multiplier': 3.5}
    
    sol_strategy = Strategy(**strategy_params_sol)
    risk_manager = RiskManager(risk_per_trade_percentage=risk_params_sol['risk_per_trade'])
    state_manager = StateManager()
    total_capital = 10000 
    
    while True:
        log.info("***************** INICIANDO NUEVO CICLO DE TRADING *****************")
        active_trades = state_manager.load_state()
        log.info(f"Estado actual cargado. Operaciones activas: {len(active_trades)}")
        
        # --- LÓGICA DE GESTIÓN Y SINCRONIZACIÓN DE POSICIÓN ---
        if 'SOL' in active_trades and active_trades['SOL']['status'] == 'open':
            log.info("Posición abierta detectada para SOL. Verificando estado...")
            trade = active_trades['SOL']
            order_id = trade['order_details']['id']
            product_id = trade['order_details']['symbol']
            
            # 1. Verificamos el estado real de la orden en el exchange
            order_status = execution_handler.get_order_status(order_id, product_id)
            
            if order_status and order_status['status'] == 'closed':
                log.info(f"Orden {order_id} confirmada como EJECUTADA. La posición está activa.")
                # Aquí iría la lógica para gestionar el trailing stop-loss de la posición activa.
                
            elif order_status and order_status['status'] == 'open':
                log.info(f"La orden de compra {order_id} todavía está abierta (esperando a ser ejecutada). No se tomarán más acciones.")

            elif order_status is None:
                log.warning(f"No se pudo confirmar el estado de la orden {order_id}. Se reintentará en el próximo ciclo.")

        # --- LÓGICA DE BÚSQUEDA DE NUEVAS ENTRADAS ---
        elif 'SOL' not in active_trades:
            log.info("--- Buscando nueva oportunidad de entrada para Solana (SOL) ---")
            sol_data = api_client.get_historical_data(product_id='SOL/USD', granularity='6h', min_candles=201)
            
            if sol_data is not None and not sol_data.empty:
                sol_data.ta.atr(append=True, length=risk_params_sol['atr_period'])
                sol_signal = sol_strategy.analyze_sol_combined(sol_data)
                log.info(f"Señal de la estrategia SOL: {sol_signal}")
                
                if sol_signal == 'BUY':
                    latest_data = sol_data.iloc[-1]
                    entry_price = latest_data['close']
                    atr_col_name = f'ATRr_{risk_params_sol["atr_period"]}'
                    stop_loss_price = entry_price - (latest_data[atr_col_name] * risk_params_sol['atr_multiplier'])
                    position_size = risk_manager.calculate_position_size(total_capital, entry_price, stop_loss_price)
                    
                    if position_size is not None:
                        amount_of_asset = position_size / entry_price
                        # Usar la nueva función para colocar una orden límite un 0.5% por debajo del precio actual
                        limit_price = entry_price * 0.995
                        order_result = execution_handler.place_limit_order(
                            product_id='SOL/USD', 
                            side='buy', 
                            price=limit_price, 
                            amount_of_asset=amount_of_asset
                        )
                        
                        if order_result:
                            log.info(f"Orden Límite para SOL colocada. ID: {order_result['id']}")
                            active_trades['SOL'] = { 
                                "order_details": order_result, 
                                "stop_loss_price": stop_loss_price,
                                "status": "open" 
                            }
                            state_manager.save_state(active_trades)

        # Pausa de 6 horas
        sleep_duration_seconds = 6 * 60 * 60
        log.info(f"Ciclo finalizado. Durmiendo durante {sleep_duration_seconds / 3600:.1f} horas...")
        time.sleep(sleep_duration_seconds)

if __name__ == "__main__":
    main()