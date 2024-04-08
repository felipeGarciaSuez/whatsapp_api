# Usa una imagen base de Python
FROM python:3.8

# Establece el directorio de trabajo en /app
WORKDIR /whatsapp_api

# Copia el archivo requirements.txt y lo instala
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# # Copiar el archivo .env al contenedor
COPY .env ./

# # Cargar las variables de entorno desde el archivo .env
ENV $(cat .env | xargs)

# Copia todo el contenido actual del directorio de trabajo en el contenedor en /app
COPY . .

# Comando por defecto a ejecutar cuando se inicie el contenedor
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
