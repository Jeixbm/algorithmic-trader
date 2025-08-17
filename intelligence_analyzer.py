# trading_bot/intelligence_analyzer.py
import google.generativeai as genai
from config import config
from logger import log

class IntelligenceAnalyzer:
    def __init__(self):
        try:
            if not config.GEMINI_API_KEY:
                raise ValueError("La clave de API de Gemini no fue encontrada en el archivo .env")
            
            genai.configure(api_key=config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro')
            log.info("Módulo de Inteligencia (Gemini) inicializado correctamente.")
        except Exception as e:
            self.model = None
            log.error(f"Error al inicializar el modelo de Gemini: {e}")

    def get_news_sentiment(self, headlines: list):
        """
        Analiza una lista de titulares y devuelve un sentimiento general.
        """
        if not self.model or not headlines:
            return "NEUTRAL" # Devolver un valor seguro si el modelo no funciona o no hay noticias

        # Crear el prompt para la IA
        formatted_headlines = "\n- ".join(headlines)
        prompt = (
            "Analiza el sentimiento general de los siguientes titulares de noticias sobre una criptomoneda. "
            "Responde únicamente con una de estas tres palabras: POSITIVE, NEGATIVE, o NEUTRAL.\n\n"
            "Titulares:\n"
            f"- {formatted_headlines}"
        )

        try:
            log.info("Enviando titulares a la API de Gemini para análisis de sentimiento...")
            response = self.model.generate_content(prompt)
            sentiment = response.text.strip().upper()
            log.info(f"Sentimiento recibido de Gemini: {sentiment}")

            # Validar la respuesta
            if sentiment in ["POSITIVE", "NEGATIVE", "NEUTRAL"]:
                return sentiment
            else:
                log.warning(f"Respuesta no válida de Gemini: '{sentiment}'. Se usará NEUTRAL.")
                return "NEUTRAL"
        except Exception as e:
            log.error(f"Error al comunicarse con la API de Gemini: {e}")
            return "NEUTRAL"

# Crear una instancia para ser usada por el bot
intelligence_analyzer = IntelligenceAnalyzer()