# risk_manager.py
from logger import log

class RiskManager:
    """
    Gestiona el riesgo de capital, incluyendo el tamaño de las posiciones
    y los niveles de stop-loss/take-profit.
    """
    def __init__(self, risk_per_trade_percentage=0.01):
        """
        Inicializa el gestor de riesgo.
        :param risk_per_trade_percentage: El porcentaje del capital total a arriesgar por operación (ej. 0.01 para 1%).
        """
        if not 0 < risk_per_trade_percentage < 1:
            raise ValueError("El porcentaje de riesgo debe estar entre 0 y 1.")
        
        self.risk_per_trade_percentage = risk_per_trade_percentage
        log.info(f"Módulo de Gestión de Riesgo inicializado. Riesgo por operación: {self.risk_per_trade_percentage:.2%}")

    def calculate_position_size(self, total_capital, entry_price, stop_loss_price):
        """
        Calcula el tamaño de la posición en la moneda de cotización (ej. USD).
        
        :param total_capital: El capital total disponible para trading.
        :param entry_price: El precio de entrada de la operación.
        :param stop_loss_price: El precio del stop-loss.
        :return: El tamaño de la posición a abrir (en USD) o None si los precios son inválidos.
        """
        if entry_price <= 0 or stop_loss_price <= 0 or entry_price <= stop_loss_price:
            log.error("Precios de entrada o stop-loss inválidos para calcular el tamaño de la posición.")
            return None

        # 1. Calcular la cantidad de dinero que estamos dispuestos a arriesgar
        amount_to_risk = total_capital * self.risk_per_trade_percentage

        # 2. Calcular la distancia del stop-loss en porcentaje
        stop_loss_distance_percentage = (entry_price - stop_loss_price) / entry_price

        # 3. Calcular el tamaño de la posición
        # Fórmula: Posición = (Capital a Arriesgar) / (Distancia del Stop-Loss %)
        position_size = amount_to_risk / stop_loss_distance_percentage
        
        log.info(f"Cálculo de posición: Capital Total=${total_capital:,.2f}, Entrada=${entry_price:.2f}, Stop-Loss=${stop_loss_price:.2f}")
        log.info(f"Resultado: Arriesgando ${amount_to_risk:,.2f}, el tamaño de la posición es ${position_size:,.2f}")
        
        return position_size