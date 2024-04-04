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
    
functions = {
    'fecha_hoy': fecha_hoy,
    'comprobar_reserva': comprobar_reserva,
    'ver_disponibilidad': ver_disponibilidad,
    'eliminar_mesa': eliminar_mesa,
    'reservar_mesa': reservar_mesa
}

# Función para transcribir un archivo de audio

def transcript_audio(media_id):
    try:
        media = requests.get(f"https://graph.facebook.com/v17.0/{media_id}?access_token={WHATSAPP_TOKEN}")
        file = requests.get(media.json()['url'], headers={"Authorization": "Bearer " + WHATSAPP_TOKEN})
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


#FUnciones para interactuar con la api de OPENAI
thread_id = None
run_id = None


def create_thread():
    try:
        response = requests.post("https://openai_api/threads")
        response.raise_for_status()
        data = response.json()
        thread_id = data.get('id')
        return thread_id
    except Exception as e:
        print(e)

def create_message(content):
    try:
        response = requests.post(f"https://openai_api/threads/{thread_id}/messages", json={"role": "user", "content": content})
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as e:
        print(e)

def create_run(assistant_id):
    try:
        response = requests.post(f"https://openai_api/threads/{thread_id}/runs", json={"assistant_id": assistant_id})
        response.raise_for_status()
        data = response.json()
        run_id = data.get('id')
        return run_id
    except Exception as e:
        print(e)

def get_run_details():
    try:
        response = requests.get(f"https://openai_api/threads/{thread_id}/runs/{run_id}")
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as e:
        print(e)

def submit_tool_outputs(tool_call_id, output):
    try:
        response = requests.post(f"https://openai_api/threads/{thread_id}/runs/{run_id}/submit_tool_outputs", json={"tool_outputs": [{"tool_call_id": tool_call_id, "output": output}]})
        response.raise_for_status()
    except Exception as e:
        print(e)


async def wait_till_run_complete():
    data = get_run_details()
    if data.get('status') not in ["queued", "in_progress"]:
        if data.get('status') == "requires_action":
            required_action = data.get('required_action')
            function_name = required_action.get('submit_tool_outputs').get('tool_calls')[0].get('function').get('name')
            if functions.get(function_name):
                tool_call_id = required_action.get('submit_tool_outputs').get('tool_calls')[0].get('id')
                arguments = required_action.get('submit_tool_outputs').get('tool_calls')[0].get('function').get('arguments')
                output = await functions[function_name](arguments)
                submit_tool_outputs(tool_call_id, output)
                await wait_till_run_complete()


def get_run_steps():
    try:
        response = requests.get(f"https://openai_api/threads/{thread_id}/runs/{run_id}/steps")
        response.raise_for_status()
        data = response.json()
        message_id = data.get('data')[0].get('step_details').get('message_creation').get('message_id')
        return message_id
    except Exception as e:
        print(e)

def get_message(message_id):
    try:
        response = requests.get(f"https://openai_api/threads/{thread_id}/messages/{message_id}")
        response.raise_for_status()
        data = response.json()
        content = data.get('content')[0].get('text').get('value')
        return content
    except Exception as e:
        print(e)
