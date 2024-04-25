import os
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
    "OpenAI-Beta": "assistants=v2",
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
        response = httpx.post(
            hook_url + "3kiyahmwul8qg5f7sps8zzppv5h8dnnp",
            params=params,
            headers=hook_headers
        )
        response.raise_for_status()
        print("RESPONSE COMPROBAR RESERVA", response)
        return response.text
    except httpx.HTTPError as e:
        print("Error Hook API", e)
        return None

async def ver_disponibilidad(params):
    try:
        response = httpx.post(
            hook_url + "bzm1bcp3cgykq5b004zptvxy00yhluic",
            params=params,
            headers=hook_headers
        )
        print("RESPONSE VER DISPONIBILIDAD", response)
        response.raise_for_status()
        return response.text
    except httpx.HTTPError as e:
        handle_error(e)
        return None

async def eliminar_mesa(params):
    try:
        response = httpx.post(
            hook_url + "ic3lgm2m85a8pjpwvd06judp06mt98gw",
            params=params,
            headers=hook_headers
        )
        response.raise_for_status()
        print("RESPONSE ELIMINAR MESA", response)
        return response.text
    except httpx.HTTPError as e:
        print("Error Hook API", e)
        return None

async def reservar_mesa(params):
    try:
        response = httpx.post(
            hook_url + "7dovs57qgwgfc5buyakktndx2s3bto8k",
            params=params,
            headers=hook_headers
        )
        response.raise_for_status()
        print("RESPONSE RESERVAR MESA", response)
        return response.text
    except httpx.HTTPError as e:
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
        media = httpx.get(f"https://graph.facebook.com/v17.0/{media_id}?access_token={WHATSAPP_TOKEN}")
        file = httpx.get(media.json()['url'], headers={"Authorization": "Bearer " + WHATSAPP_TOKEN})
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

        openai_transcription = httpx.post(
            "https://api.openai.com/v1/audio/transcriptions",
            headers=headers,
            files=files,
            data=data,
        )

        return openai_transcription.json()["text"]

    except httpx.HTTPError as e:
        handle_error(e)
        return None


#FUnciones para interactuar con la api de OPENAI
#Creacion de thread
async def create_thread(phone):
    try:
        number_object = await sync_to_async(Thread.search_by_number)(phone)
        print("NUMBER OBJECT olaaa", number_object)
        if number_object != []:
            print("ENTRO AL IF")
            thread_id = number_object[0].threadId
            print("THREAD ID", thread_id)
        else:
            print("NO ENCONTRO EN DB")
            # async with httpx.AsyncClient() as client:
            response = httpx.post(openai_url + "threads", headers=openai_headers)
            response.raise_for_status()
            thread_id = response.json()["id"]
            print("THREAD ID", thread_id)
            thread = await sync_to_async(Thread.create_thread)(phone, thread_id)
            print("THREAD CREADO", thread)

        return thread_id
    except httpx.HTTPError as e:
        print("MAL AHI")
        handle_error(e)

#Creacion de mensaje
async def create_message(thread_id, content):
    try:
        #Aca ejecutamos el post con el thread_id de la base de datos o de la api de openai
        res = httpx.post(
            openai_url+ "threads/"+thread_id+"/messages",
            json={"role": "user", "content": content},
            headers=openai_headers
        )
        res.raise_for_status()  # Lanza una excepción si la solicitud falla
        # data = res.json()  # Devuelve los datos de respuesta como JSON
        return res
    except httpx.HTTPStatusError as e:
        handle_error(e)
        print("EXCEPCIOOON", e.response.status_code)
        #En el caso de que falle la peticion por culpa de 
        if(e.response.status_code == 404 or e.response.status_code == 400):
            thread_deleted = await sync_to_async(Thread.objects.get)(threadId=thread_id)
            print("THREAD DELETED", thread_deleted)
            await sync_to_async(thread_deleted.delete)()
            return e.response

async def create_run(thread_id):
    try:
        response = httpx.post(f"{openai_url}threads/{thread_id}/runs", json={"assistant_id": ASSISTANT_ID}, headers=openai_headers)
        response.raise_for_status()
        data = response.json()
        print("DATA RUN", data)
        run_id = data.get('id')
        return run_id
    except httpx.HTTPError as e:
        handle_error(e)

async def get_run_details(thread_id, run_id):
    try:
        response = httpx.get(f'{openai_url}threads/{thread_id}/runs/{run_id}', headers=openai_headers)
        response.raise_for_status()
        data = response.json()
        # print("DATAAAAAAAAAAAAAAAAA", data)
        return data
    except httpx.HTTPError as e:
        handle_error(e)

async def submit_tool_outputs(tool_call_id, output, thread_id, run_id):
    try:
        print("SUBMIT TOOL OUTPUTS")
        print(f'TOOL CALL: {tool_call_id} OUTPUT: {output} THREAD: {thread_id} RUN: {run_id}')
        response = httpx.post(f'{openai_url}threads/{thread_id}/runs/{run_id}/submit_tool_outputs', json={"tool_outputs": [{"tool_call_id": tool_call_id, "output": output}]}, headers=openai_headers)
        response.raise_for_status()
        print("SUBMIT TOOL OUTPUTS res", response.json())
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
                print("FUNCTION NAME", function_name)
                print("ARGUMENTS", arguments)
                output = await functions.get(function_name)(arguments)
                print("OUTPUT", output)
                await submit_tool_outputs(tool_call_id, output, thread_id, run_id)
                await wait_till_run_complete(thread_id, run_id)
        return
    await wait_till_run_complete(thread_id, run_id)


async def get_run_steps(thread_id, run_id):
    try:
        response = httpx.get(f"{openai_url}threads/{thread_id}/runs/{run_id}/steps", headers=openai_headers)
        response.raise_for_status()
        data = response.json()
        print("DATAAAAAAAAAAAAAAAAA", data)
        message_id = data['data'][0]['step_details']['message_creation']['message_id']
        return message_id
    except httpx.HTTPError as e:
        handle_error(e)

async def get_message(message_id, thread_id):
    try:
        print("GETTING MESSAGE", message_id)
        response = httpx.get(f"{openai_url}threads/{thread_id}/messages/{message_id}", headers=openai_headers)
        response.raise_for_status()
        data = response.json()
        print("CONTENT", data)
        content = data.get('content')[0].get('text').get('value')
        
        return content
    except httpx.HTTPError as e:
        handle_error(e)

#Ejecucion funciones chat-gpt
async def chatgpt_execute(content, number):
    #Crea un thread en el caso de que no haya uno, si hay agarra el de la DB
    thread_id = await create_thread(phone=number)
    # Creación de mensaje inicial
    if thread_id:
        res = await create_message(thread_id, content)
        print(res, "RES EN FUNCTION")
        if res.status_code == 404 or res.status_code == 400:
            print("ERROR DETECTADO", res)
            thread_id = await create_thread(number)
            await create_message(thread_id, content)
        # Crear runner
        run_id = await create_run(thread_id)
        if run_id:
            print("RUN ID", run_id)
            # Esperar que se complete el mismo
            await wait_till_run_complete(thread_id, run_id)
            # Correr etapas
            message_id = await get_run_steps(thread_id, run_id)
            # Obtener mensaje
            if message_id:
                return await get_message(message_id, thread_id)
    return None        

#Funcion enviarr mensaje
async def send_message(phone_number_id, from_number, text):
    try:
        response = httpx.post(
            f"https://graph.facebook.com/v12.0/{phone_number_id}/messages?access_token={WHATSAPP_TOKEN}",
            json={
                "messaging_product": "whatsapp",
                "to": from_number,
                "text": {"body": text},
            },
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        print("RESPONSE SEND MESSAGE", response)
        return response.text  # Devuelve el texto de la respuesta
    except httpx.HTTPError as e:
        handle_error(e)