# trading_bot/portfolio_analyzer.py
import pandas as pd
from logger import log
from api_client import api_client

class PortfolioAnalyzer:
    def __init__(self, correlation_threshold=0.7):
        self.correlation_threshold = correlation_threshold
        log.info("Módulo de Análisis de Cartera inicializado.")

    def is_highly_correlated(self, new_asset_id, new_asset_data, open_trades):
        """
        Verifica la correlación usando un DataFrame ya descargado.
        """
        if not open_trades:
            return False

        log.info(f"Verificando correlación para el nuevo activo: {new_asset_id}")
        
        if new_asset_data is None:
            log.warning(f"No se proporcionaron datos para {new_asset_id}, no se puede verificar la correlación.")
            return False

        for asset, trade in open_trades.items():
            existing_asset_id = trade.get('order_details', {}).get('symbol', asset)
            
            existing_asset_data = api_client.get_historical_data(
                product_id=existing_asset_id,
                granularity='1d', # Usar datos diarios para una correlación más estable
                limit=100
            )

            if existing_asset_data is None: continue

            # Asegurarse de que los índices de tiempo coincidan
            common_index = new_asset_data.index.intersection(existing_asset_data.index)
            if len(common_index) < 2:
                log.warning("No hay suficientes datos superpuestos para calcular la correlación.")
                continue

            correlation = new_asset_data.loc[common_index]['close'].corr(existing_asset_data.loc[common_index]['close'])
            log.info(f"Correlación entre {new_asset_id} y {existing_asset_id}: {correlation:.2f}")

            if correlation > self.correlation_threshold:
                log.warning(f"¡ALERTA DE ALTA CORRELACIÓN! {new_asset_id} está altamente correlacionado con {existing_asset_id}.")
                return True
        
        return False

portfolio_analyzer = PortfolioAnalyzer()