import os
import requests
import datetime
from io import BytesIO

# Definimos las variables de entorno
OPENAI_TOKEN = os.environ['OPENAI_TOKEN']
ASSISTANT_ID = os.environ['ASSISTANT_ID']
WHATSAPP_TOKEN = os.environ['WHATSAPP_TOKEN']

# Definimos una función para manejar errores
def handle_error(error):
    print("Error Hook API", error)

# def post_request(url, data):
#     try:
#         response = requests.post(url, json=data, headers={"Content-Type": "application/json"})
#         response.raise_for_status()  # Lanza una excepción si la solicitud falla
#         return response.json()  # Devuelve los datos de respuesta como JSON
#     except requests.exceptions.RequestException as e:
#         handle_error(e)
# Configuración de la API de OpenAI
openai_url = "https://api.openai.com/v1/"
openai_headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_TOKEN}",
    "OpenAI-Beta": "assistants=v1",
}

# Configuración de la API de Hook
hook_url = "https://hook.eu2.make.com/"
hook_headers = {
    "Content-Type": "application/json",
}

# Funciones
def fecha_hoy():
    return str(datetime.datetime.now())

def comprobar_reserva(params):
    try:
        response = requests.post(
            hook_url + "3kiyahmwul8qg5f7sps8zzppv5h8dnnp",
            json=params,
            headers=hook_headers
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error Hook API", e)
        return None

def ver_disponibilidad(params):
    try:
        response = requests.post(
            hook_url + "bzm1bcp3cgykq5b004zptvxy00yhluic",
            json=params,
            headers=hook_headers
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        handle_error(e)
        return None

def eliminar_mesa(params):
    try:
        response = requests.post(
            hook_url + "ic3lgm2m85a8pjpwvd06judp06mt98gw",
            json=params,
            headers=hook_headers
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error Hook API", e)
        return None

def reservar_mesa(params):
    try:
        response = requests.post(
            hook_url + "7dovs57qgwgfc5buyakktndx2s3bto8k",
            json=params,
            headers=hook_headers
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error Hook API", e)
        return None

# Función para transcribir un archivo de audio

def transcript_audio(media_id):
    try:
        media = requests.get(f"https://graph.facebook.com/v17.0/{media_id}?access_token={WHATSAPP_TOKEN}")
        file = requests.get(media.json().url, headers={"Authorization": "Bearer " + WHATSAPP_TOKEN})
        buffer = BytesIO(file.content)

        headers = {
            "Authorization": "Bearer " + OPENAI_TOKEN,
            "Content-Type": "audio/ogg",
        }
        files = {
            "file": buffer.getvalue(),
        }
        data = {
            "model": "whisper-1",
        }

        openai_transcription = requests.post(
            "https://api.openai.com/v1/audio/transcriptions",
            headers=headers,
            files=files,
            data=data,
        )

        return openai_transcription.json()["text"]

    except requests.exceptions.RequestException as e:
        handle_error(e)
        return None