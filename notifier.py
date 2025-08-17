import telegram
import asyncio
from logger import log
from config import config

class Notifier:
    def __init__(self):
        self.token = config.TELEGRAM_TOKEN
        self.chat_id = config.TELEGRAM_CHAT_ID
        
        if self.token and self.chat_id:
            log.info("Módulo de Notificaciones (Telegram) inicializado correctamente.")
        else:
            log.warning("Credenciales de Telegram no encontradas. El notificador está desactivado.")

    async def _send_async(self, message):
        """
        Función asíncrona interna para enviar el mensaje.
        """
        try:
            bot = telegram.Bot(token=self.token)
            await bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown'
            )
            log.info("Notificación enviada por Telegram.")
        except Exception as e:
            log.error(f"Error al enviar la notificación asíncrona por Telegram: {e}")

    def send_message(self, message):
        """
        Función síncrona que el bot puede llamar de forma segura.
        Crea un nuevo ciclo de conexión para cada mensaje.
        """
        if not self.token or not self.chat_id:
            return

        try:
            # Esta es la magia: asyncio.run() crea un nuevo "hilo" de comunicación
            # para cada mensaje, evitando problemas con conexiones cerradas.
            asyncio.run(self._send_async(message))
        except RuntimeError as e:
            # Maneja un caso raro donde un bucle ya podría estar corriendo
            if "cannot run loop while another loop is running" in str(e):
                # Si ya hay un bucle, simplemente lo usamos
                loop = asyncio.get_event_loop()
                loop.create_task(self._send_async(message))
            else:
                log.error(f"Error de Runtime en el notificador: {e}")
        except Exception as e:
            log.error(f"Error general en el notificador: {e}")

# Crear una instancia global para ser usada por el bot
notifier = Notifier()