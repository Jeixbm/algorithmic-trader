# Dockerfile

# --- 1. Imagen Base ---
# Empezamos con una imagen oficial de Python 3.11, ligera y optimizada.
FROM python:3.11-slim

# --- 2. Establecer el Directorio de Trabajo ---
# Creamos una carpeta dentro del contenedor para nuestro bot.
WORKDIR /app

# --- 3. Copiar los Requisitos ---
# Copiamos primero solo el archivo de requisitos para aprovechar el caché de Docker.
COPY requirements.txt .

# --- 4. Instalar las Dependencias ---
# Instalamos todas las librerías que necesita el bot.
RUN pip install --no-cache-dir -r requirements.txt

# --- 5. Copiar el Código del Bot ---
# Copiamos todo el código de nuestro bot a la carpeta /app del contenedor.
COPY . .

# --- 6. Comando de Ejecución ---
# Le decimos a Docker qué comando ejecutar cuando se inicie el contenedor.
CMD ["python", "main.py"]