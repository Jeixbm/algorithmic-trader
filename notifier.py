# trading_bot/notifier.py
import telegram
import asyncio
from config import config
from logger import log

class Notifier:
    def __init__(self):
        self.bot_token = config.TELEGRAM_TOKEN
        self.chat_id = config.TELEGRAM_CHAT_ID
        self.bot = None

        if self.bot_token and self.chat_id:
            try:
                self.bot = telegram.Bot(token=self.bot_token)
                log.info("Módulo de Notificaciones (Telegram) inicializado correctamente.")
            except Exception as e:
                log.error(f"Error al inicializar el bot de Telegram: {e}")
        else:
            log.warning("Credenciales de Telegram no encontradas. Las notificaciones estarán desactivadas.")

    def send_message(self, message):
        """
        Envía un mensaje a través de Telegram de forma asíncrona.
        """
        if not self.bot:
            log.warning(f"Intento de enviar notificación, pero el bot de Telegram no está configurado: '{message}'")
            return

        async def send():
            try:
                await self.bot.send_message(chat_id=self.chat_id, text=message, parse_mode='Markdown')
                log.info("Notificación enviada por Telegram.")
            except Exception as e:
                log.error(f"Error al enviar la notificación por Telegram: {e}")

        # Ejecutar la función asíncrona desde nuestro código síncrono
        try:
            asyncio.run(send())
        except RuntimeError: # En caso de que ya haya un bucle de eventos corriendo
            loop = asyncio.get_event_loop()
            loop.create_task(send())

# Crear una instancia para ser usada por otros módulos
notifier = Notifier()