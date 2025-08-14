# trading_bot/risk_manager.py
from logger import log

class RiskManager:
    """
    Gestiona el riesgo de capital, incluyendo el tamaño de las posiciones
    y los niveles de stop-loss/take-profit.
    """
    def __init__(self, default_risk_per_trade=0.02):
        """
        :param default_risk_per_trade: El porcentaje de riesgo por defecto si no se especifica otro.
        """
        if not 0 < default_risk_per_trade < 1:
            raise ValueError("El porcentaje de riesgo debe estar entre 0 y 1.")
        
        self.default_risk = default_risk_per_trade
        log.info(f"Módulo de Gestión de Riesgo inicializado. Riesgo por defecto: {self.default_risk:.2%}")

    def calculate_position_size(self, total_capital, entry_price, stop_loss_price, risk_per_trade=None):
        """
        Calcula el tamaño de la posición aceptando un porcentaje de riesgo dinámico.
        
        :param risk_per_trade: Si se proporciona, usa este valor. Si no, usa el valor por defecto.
        """
        # Si no se especifica un riesgo para esta operación, usa el valor por defecto de la clase.
        risk = risk_per_trade if risk_per_trade is not None else self.default_risk

        if entry_price <= 0 or stop_loss_price <= 0 or entry_price <= stop_loss_price:
            log.error("Precios inválidos para calcular el tamaño de la posición.")
            return None

        amount_to_risk = total_capital * risk
        stop_loss_distance = (entry_price - stop_loss_price) / entry_price
        
        if stop_loss_distance == 0: 
            return None
        
        position_size = amount_to_risk / stop_loss_distance
        
        log.info(f"Cálculo de Posición: Capital=${total_capital:,.2f}, Riesgo={risk:.2%}, Entrada=${entry_price:.2f}, SL=${stop_loss_price:.2f}")
        log.info(f"Resultado: Arriesgando ${amount_to_risk:,.2f} para una posición de ${position_size:,.2f}")
        
        return position_size