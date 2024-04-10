from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import requests
import json
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from .functions import *
from asgiref.sync import async_to_sync, sync_to_async




#Create your views here.
# @sync_to_async
# @csrf_exempt
# @async_to_sync
# async def send_message_view(request):
#     print("SENDING MESSAGE")
#     body = request.body.decode('utf-8')
#     payload = json.loads(body)
#     print(payload['entry'][0]['changes'][0])
#     phone_number_id = payload['entry'][0]['changes'][0]['value']['metadata']['phone_number_id']
#     from_var = payload['entry'][0]['changes'][0]['value']['messages'][0]['from']
#     text = payload['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
#     print(phone_number_id, from_var, text)
    
#     # Agrega 'await' al llamar a la función asíncrona send_message()
#     res = await send_message(phone_number_id, from_var, text)
    
#     return HttpResponse("Message sent", res)
@sync_to_async
@csrf_exempt
@async_to_sync
async def index(request):
    print("INDEX")
    res = await chatgpt_execute("Hola respondeme saludandome!")
    return HttpResponse(res)

def webhook_verification(request):
    """
    Esta función maneja la verificación del webhook.
    """

    # Este será el valor del token de verificación cuando configure el webhook.
    verify_token = os.getenv('VERIFY_TOKEN')

    # Analizar parámetros de la solicitud de verificación del webhook
    mode = request.GET.get("hub.mode")
    token = request.GET.get("hub.verify_token")
    challenge = request.GET.get("hub.challenge")

    # Comprobar si se envió un token y un modo.
    if mode and token:
        # Verifique que el modo y el token enviado sean correctos
        if mode == "subscribe" and token == verify_token:
            # Responda con 200 OK y token de desafío de la solicitud
            print("WEBHOOK_VERIFIED")
            return HttpResponse(challenge, status=200)
        else:
            # Responde con '403 Prohibido' si los tokens de verificación no coinciden
            return HttpResponse(status=403)
    else:
        # Responde con '400 Solicitud incorrecta' si faltan parámetros
        return HttpResponse(status=400)

@sync_to_async
@csrf_exempt
@async_to_sync
async def webhook_view(request):
    if request.method == 'POST':
        # Información sobre la carga útil de los mensajes de texto de WhatsApp: https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks/payload-examples#text-messages
        body = request.body.decode('utf-8')
        payload = json.loads(body)
        
        if 'object' in payload:
            entry = payload.get('entry', [])
            if entry and 'changes' in entry[0]:
                changes = entry[0]['changes']
                if changes and 'messages' in changes[0]['value']:
                    phone_number_id = changes[0]['value']['metadata']['phone_number_id']
                    message_data = changes[0]['value']['messages'][0]
                    from_number = message_data['from']
                    message_type = message_data['type']
                    
                    if message_type == 'text':
                        message = message_data['text']['body']
                    elif message_type == 'audio':
                        # send_message(
                        #     phone_number_id,
                        #     from_number,
                        #     "Procesando nota de voz. Espera..."
                        # )
                        audio_id = message_data['audio']['id']
                        message = await transcript_audio(audio_id)
                        transcription = f'*Transcripción del audio:*\n\n"{message}"\n\n_tardará unos segundos..._'
                        await send_message(phone_number_id, from_number, transcription)
                    chatgpt_response = await chatgpt_execute(message)
                    res =await send_message(phone_number_id, from_number, chatgpt_response)
                    print(res)
            return JsonResponse({}, status=200)
        else:
            # Devuelve un '404 no encontrado' si el evento no proviene de una API de WhatsApp
            return JsonResponse({}, status=401)
    
    elif request.method == 'GET':
        return webhook_verification(request)
    else:
        return JsonResponse({}, status=405)


    
