import time
import pandas_ta as ta
from logger import log
import health_checker
from config import config
from api_client import APIClient
import strategy
import risk_manager
from state_manager import StateManager
from notifier import notifier
from execution_handler import execution_handler
from intelligence_analyzer import intelligence_analyzer

def get_latest_solana_news():
    log.info("Simulando obtención de noticias sobre Solana...")
    return ["Solana price shows strength as network activity surges."]

def main():
    log.info("==============================================")
    log.info(f"    INICIANDO BOT - MODO: {config.BOT_MODE}    ")
    log.info(f"    ESTRATEGIA: Breakout 6H (SOL/USDT)    ")
    log.info("==============================================")
    
    api_client = APIClient() 
    state_manager = StateManager()

    notifier.send_message(f"✅ **Bot Iniciado**\nModo: {config.BOT_MODE}\nEstrategia: Breakout 6H (SOL)")
    if not health_checker.perform_initial_checks(api_client):
        return
    
    while True:
        log.info("***************** INICIANDO NUEVO CICLO DE TRADING *****************")
        
        try:
            current_balance = api_client.get_balance('USDT')
            if current_balance is not None:
                log.info(f"SALDO ACTUAL EN CUENTA: ${current_balance:,.2f} USDT")
            else:
                log.warning("No se pudo obtener el balance actual de la cuenta.")

            if state_manager.is_in_position('SOL/USDT'):
                log.info("Posición abierta detectada para SOL. Monitoreando condiciones de salida.")
                time.sleep(300)
                continue

            log.info("Buscando nueva oportunidad de entrada para SOL...")
            sol_data = api_client.get_historical_data('SOL/USDT', '6h', limit=400)
            btc_6h_data = api_client.get_historical_data('BTC/USDT', '6h', limit=400)
            btc_1d_data = api_client.get_historical_data('BTC/USDT', '1d', limit=400)
            
            if sol_data is not None and not sol_data.empty and btc_6h_data is not None and btc_1d_data is not None:
                signal = strategy.check_strategy_6h_breakout(sol_data, btc_6h_data, btc_1d_data, config)
                log.info(f"Señal de la estrategia cuantitativa: {signal}")
                
                if signal in ['long', 'short']:
                    if signal == 'long':
                        log.info("Señal de compra recibida. Consultando filtro de IA...")
                        headlines = get_latest_solana_news()
                        sentiment = intelligence_analyzer.get_news_sentiment(headlines)
                        
                        if sentiment == 'NEGATIVE':
                            log.warning("OPERACIÓN VETADA POR IA.")
                            time.sleep(300)
                            continue
                        
                        log.info(f"Sentimiento de mercado '{sentiment}'. APROBANDO operación.")

                    if current_balance is not None and current_balance > 0:
                        current_price = sol_data['close'].iloc[-1]
                        atr = ta.atr(sol_data['high'], sol_data['low'], sol_data['close'], length=14).iloc[-1]
                        
                        position_size, sl_long, sl_short = risk_manager.calculate_position_details(
                            price=current_price,
                            balance=current_balance,
                            risk_pct=config.STRATEGY_CONFIG['risk_pct'],
                            atr=atr,
                            atr_stop_mult=config.STRATEGY_CONFIG['atr_stop_mult']
                        )
                        
                        stop_loss_price = sl_long if signal == 'long' else sl_short
                        
                        if position_size > 0:
                            log.info(f"Ejecutando orden {signal.upper()} para {position_size:.4f} SOL a ${current_price:.2f}")
                            
                            log.warning("LA EJECUCIÓN DE ÓRDENES ESTÁ DESACTIVADA. Esta es una prueba en seco.")
                            # order_result = execution_handler.place_market_order_with_sl(...)
                else:
                    # --- MEJORA 2: Notificación de "Sigo Vivo" en Telegram ---
                    log.info("No hay señal. Enviando notificación de estado.")
                    notifier.send_message("✅ Ciclo completado sin señal. El bot sigue activo y monitoreando.")
            
            # --- MEJORA 1: Temporizador Visual en la Consola ---
            total_sleep_seconds = 6 * 60 * 60
            sleep_interval_seconds = 15 * 60 # Intervalo de 15 minutos
            
            log.info("Ciclo finalizado. Entrando en modo de espera de 6 horas...")
            num_intervals = total_sleep_seconds // sleep_interval_seconds
            
            for i in range(num_intervals):
                remaining_seconds = total_sleep_seconds - ((i + 1) * sleep_interval_seconds)
                # Convertir segundos a horas y minutos para el log
                hours, remainder = divmod(remaining_seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                # Usamos print() con '\r' para una línea que se actualiza sola en la consola
                print(f"  Próximo ciclo de análisis en {int(hours)}h {int(minutes)}m...          \r", end="")
                time.sleep(sleep_interval_seconds)
            print("\n") # Nueva línea para limpiar el contador
        
        except Exception as e:
            log.error(f"Ocurrió un error en el bucle principal: {e}", exc_info=True)
            notifier.send_message(f"🚨 **Error Crítico en el Bot**\nError: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()