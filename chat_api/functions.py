import os
import requests
import httpx
import datetime
from io import BytesIO
import os
from dotenv import load_dotenv
from .models import Thread
from asgiref.sync import sync_to_async

# Definimos las variables de entorno
# Load environment variables from .env file

load_dotenv()
OPENAI_TOKEN = os.getenv('OPENAI_TOKEN')
ASSISTANT_ID = os.getenv('ASSISTANT_ID')
WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')

# Definimos una función para manejar errores
def handle_error(error):
    print("ERROR: ", error)

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
async def fecha_hoy(params):
    print(params, "PARAMS DE FECHA HOY")
    return str(datetime.datetime.now())

async def comprobar_reserva(params):
    try:
        response = requests.post(
            hook_url + "3kiyahmwul8qg5f7sps8zzppv5h8dnnp",
            json=params,
            headers=hook_headers
        )
        response.raise_for_status()
        print("RESPONSE COMPROBAR RESERVA", response)
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error Hook API", e)
        return None

async def ver_disponibilidad(params):
    try:
        response = requests.post(
            hook_url + "bzm1bcp3cgykq5b004zptvxy00yhluic",
            json=params,
            headers=hook_headers
        )
        response.raise_for_status()
        print("RESPONSE VER DISP", response)
        return response.json()
    except requests.exceptions.RequestException as e:
        handle_error(e)
        return None

async def eliminar_mesa(params):
    try:
        response = requests.post(
            hook_url + "ic3lgm2m85a8pjpwvd06judp06mt98gw",
            json=params,
            headers=hook_headers
        )
        response.raise_for_status()
        print("RESPONSE ELIMINAR MESA", response)
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error Hook API", e)
        return None

async def reservar_mesa(params):
    try:
        response = requests.post(
            hook_url + "7dovs57qgwgfc5buyakktndx2s3bto8k",
            json=params,
            headers=hook_headers
        )
        response.raise_for_status()
        print("RESPONSE RESERVAR MESA", response)
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

async def transcript_audio(media_id):
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
#Creacion de thread
async def create_thread(number):
    try:
        # number_object = None
        number_object = await sync_to_async(Thread.search_by_number)(number)
        print("NUMBER OBJECT olaaa")
        print(number_object.first())
        if number_object.exists():
            print("ENTRO AL IF", number_object)
            thread_id = number_object.first().threadId
        else:
            print("EL ERROR ESTA ACA")
            async with httpx.AsyncClient() as client:
                response = await client.post(openai_url + "threads", headers=openai_headers)
                response.raise_for_status()
                thread_id = response.json()["id"]
                print("THREAD ID", thread_id)
                thread = Thread(phone=number, threadId=thread_id)
                thread.save()
                print("THREAD GUARDADO EN DB", thread)

        return thread_id
    except Exception as e:
        print("MAL AHI")
        handle_error(e)

#Creacion de mensaje
async def create_message(thread_id, content):
    try:
        #Aca ejecutamos el post con el thread_id de la base de datos o de la api de openai
        response = requests.post(
            openai_url+ "threads/"+thread_id+"/messages",
            json={"role": "user", "content": content},
            headers=openai_headers,
        )
        response.raise_for_status()  # Lanza una excepción si la solicitud falla
        data = response.json()  # Devuelve los datos de respuesta como JSON
        return data
    except Exception as e:
        handle_error(e)
        print("EXCEPCIOOON", e)
        #En el caso de que falle la peticion por culpa de 
        if(e):
            thread_deleted = await Thread.objects.get(threadId=thread_id)
            print("THREAD DELETED", thread_deleted)
            thread_deleted.delete()
            return e

async def create_run(thread_id):
    try:
        response = requests.post(f"{openai_url}threads/{thread_id}/runs", json={"assistant_id": ASSISTANT_ID}, headers=openai_headers)
        response.raise_for_status()
        data = response.json()
        run_id = data.get('id')
        return run_id
    except Exception as e:
        handle_error(e)

async def get_run_details(thread_id, run_id):
    try:
        response = requests.get(f'{openai_url}threads/{thread_id}/runs/{run_id}', headers=openai_headers)
        response.raise_for_status()
        data = response.json()
        # print("DATAAAAAAAAAAAAAAAAA", data)
        return data
    except Exception as e:
        handle_error(e)

async def submit_tool_outputs(tool_call_id, output, thread_id, run_id):
    try:
        response = requests.post(f'{openai_url}threads/{thread_id}/runs/{run_id}/submit_tool_outputs', json={"tool_outputs": [{"tool_call_id": tool_call_id, "output": output}]}, headers=openai_headers)
        response.raise_for_status()
        print(f'{openai_url}threads/{thread_id}/runs/{run_id}/submit_tool_outputs', json={"tool_outputs": [{"tool_call_id": tool_call_id, "output": output}]})
        print("SUBMIT TOOL OUTPUTS", response.json())
    except Exception as e:
        handle_error(e)


async def wait_till_run_complete(thread_id, run_id):
    print("Waiting for run to complete", run_id, thread_id)
    data = await get_run_details(thread_id, run_id)
    print("DATAAAAAAAAAAAAAAAAA TILL THE RUNN", data['status'])
    if data.get('status') not in ["queued", "in_progress"]:
        if data.get('status') == "requires_action":
            required_action = data.get('required_action')
            function_name = required_action.get('submit_tool_outputs').get('tool_calls')[0].get('function').get('name')
            if functions.get(function_name):
                tool_call_id = required_action.get('submit_tool_outputs').get('tool_calls')[0].get('id')
                arguments = required_action.get('submit_tool_outputs').get('tool_calls')[0].get('function').get('arguments')
                output = await functions.get(function_name)(arguments)
                print("OUTPUT", output)
                await submit_tool_outputs(tool_call_id, output, thread_id, run_id)
                await wait_till_run_complete(thread_id, run_id)
        return
    await wait_till_run_complete(thread_id, run_id)


async def get_run_steps(thread_id, run_id):
    try:
        response = requests.get(f"{openai_url}threads/{thread_id}/runs/{run_id}/steps", headers=openai_headers)
        response.raise_for_status()
        data = response.json()
        print("DATAAAAAAAAAAAAAAAAA", data)
        message_id = data['data'][0]['step_details']['message_creation']['message_id']
        return message_id
    except Exception as e:
        handle_error(e)

async def get_message(message_id, thread_id):
    try:
        print("GETTING MESSAGE", message_id)
        response = requests.get(f"{openai_url}threads/{thread_id}/messages/{message_id}", headers=openai_headers)
        response.raise_for_status()
        data = response.json()
        print("CONTENT", data)
        content = data.get('content')[0].get('text').get('value')
        
        return content
    except Exception as e:
        handle_error(e)

#Ejecucion funciones chat-gpt
async def chatgpt_execute(content, number):
    #Crea un thread en el caso de que no haya uno, si hay agarra el de la DB
    thread_id = await create_thread(number)
    # Creación de mensaje inicial
    print("RANDOMM")
    res = await create_message(thread_id, content)
    print("THREAD ID", thread_id, "CONTENT", content)
    if res.get('error'):
        print("ERROR DETECTADO", res)
        thread_id = await create_thread(number)
        await create_message(thread_id, content)
    # Crear runner
    run_id = await create_run(thread_id)
    print("RUN ID", run_id)
    # Esperar que se complete el mismo
    await wait_till_run_complete(thread_id, run_id)
    # Correr etapas
    message_id = await get_run_steps(thread_id, run_id)
    # Obtener mensaje
    return await get_message(message_id, thread_id)

#Funcion enviarr mensaje
async def send_message(phone_number_id, from_number, text):
    try:
        response = requests.post(
            f"https://graph.facebook.com/v12.0/{phone_number_id}/messages?access_token={WHATSAPP_TOKEN}",
            json={
                "messaging_product": "whatsapp",
                "to": from_number,
                "text": {"body": text},
            },
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.text  # Devuelve el texto de la respuesta
    except requests.exceptions.RequestException as e:
        handle_error(e)