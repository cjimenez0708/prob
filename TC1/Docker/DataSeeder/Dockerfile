FROM python:3.12.4-slim-bookworm

WORKDIR /app

# Copiar primero solo el archivo de dependencias
COPY app/requirements.txt .

# Instalar dependencias (capa que raramente cambia)
RUN pip install --no-cache-dir -r requirements.txt

# Ahora copiar el resto del código
COPY app/. .

# Comando por defecto para ejecutar la aplicación
CMD ["python", "app.py"]