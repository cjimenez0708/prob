FROM python:3.12.4-slim-bookworm

WORKDIR /app

# Copiar primero solo el archivo de dependencias
COPY app/requirements.txt .

# Instalar dependencias (capa que raramente cambia)
RUN pip install --no-cache-dir -r requirements.txt

# Ahora copiar el resto del código
COPY app/. .

# Exponer puerto
EXPOSE 5000

# Comando para iniciar Flask
CMD ["flask", "--app", "app", "run", "--host=0.0.0.0", "--port=5000"]
