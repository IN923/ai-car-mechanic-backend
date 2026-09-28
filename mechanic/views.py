from django.shortcuts import render
from google import genai
from google.genai import types
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .prompts import SYSTEM_INSTRUCTIONS,CONTEXT_SYSTEM_INSTRUCTION
# from .models import Chat,Context, DiagnosticReport, FileUpload
from .models import Conversation,Message,MediaFile,Diagnosis,Context,Booking
import uuid
import base64
import json
# Create your views here.

@api_view(['POST'])
def generate_response(request):
    print("request data=",request.data)
    conversation_id = request.data.get('conversation_id')
    role = request.data.get('role')
    content = request.data.get('message')
    file_id = request.data.get('file_id')
    gemini_content = []

    file_upload = ''

    if file_id:
        # getting file from database
        try:
            file_upload = MediaFile.objects.get(
                id=file_id
            )
            print("file uploadfffffffff",file_upload)
        except MediaFile.DoesNotExist:
            return Response(
                {
                    "error":
                    f"File {file_id} not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        if file_upload:
            print(f"Processing file: {file_upload.file.name}, MIME type: {file_upload.mime_type}")

        mime_type = file_upload.mime_type or ""

        # ---------------------------
        # IMAGE
        # ---------------------------
        if mime_type.startswith("image/"):

            with file_upload.file.open("rb") as f:
                file_bytes = f.read()

            file_b64 = base64.b64encode(
                file_bytes
            ).decode("utf-8")

            gemini_content.append({
                "type": "image",
                "data": file_b64,
                "mime_type": mime_type
            })
        # ---------------------------
        # AUDIO
        # ---------------------------
        elif mime_type.startswith("audio/"):

            gemini_content= client.files.upload(
                file=file_upload.file.path
            )

            gemini_content.append({
                "type": "audio",
                "uri": gemini_file.uri,
                "mime_type": gemini_file.mime_type
            })

        # ---------------------------
        # VIDEO
        # ---------------------------
        elif mime_type.startswith("video/"):

            gemini_file = client.files.upload(
                file=file_upload.file.path
            )

            gemini_content.append({
                "type": "video",
                "uri": gemini_file.uri,
                "mime_type": gemini_file.mime_type
            })

    if not conversation_id:
        unique_id = uuid.uuid4()
        conversation = Conversation.objects.create(unique_id=unique_id)
    else:
        conversation = Conversation.objects.filter(unique_id=conversation_id).first()

    try:
        context= Context.objects.get(conversation_id=conversation)
    except Context.DoesNotExist:
        context = Context.objects.create(conversation_id=conversation)

    if context.context_data is None:
        generated_context = ''
    else:
        generated_context = context.context_data

    print("context=",context.context_data,"generated_content=",generated_context)

    gemini_content.append({"type": "text", "text": f'{content}+\n+{generated_context}'})

    user_message = Message.objects.create(conversation = conversation,role = "user",content = content)

    if file_upload:
        print("saving message for file upload",file_upload)
        file_upload.message = user_message
        file_upload.save()
    
    print("user_message=",user_message,user_message.content,user_message.role,user_message.created_at)

    client = genai.Client()
    output = client.interactions.create(
    model="gemini-3.5-flash-lite",
    input=gemini_content,
    system_instruction=f"{SYSTEM_INSTRUCTIONS}+{CONTEXT_SYSTEM_INSTRUCTION}")

    # extra_body={
    #         "generation_config": {
    #             "max_output_tokens": 100
    #         }
    #     }
    print("conservation bbbbbbbbbb=",conversation,output.output_text)

    print("output=",output.output_text)
    json_output = json.loads(output.output_text)
    print("gemini response=",json_output,"typeof ouput text",type(json_output))

    assistant_message = Message.objects.create(conversation = conversation,role = "assistant",content = json_output['message'])

    if file_upload:
        print("file url=",file_upload.file.url)

    if context:
        context.context_data=json_output['context']
        context.save()

    print("context_data=",context.context_data)

    return Response({"output":[
        {"id":user_message.id,"role":user_message.role,"text":user_message.content,"timestamp":user_message.created_at,"senderName": 'You',
        'file':(file_upload and file_upload.file.url) or '','file_type':(file_upload and file_upload.mime_type) or ''},
        {"id":assistant_message.id,"role":assistant_message.role,"text":assistant_message.content,"timestamp":assistant_message.created_at,"senderName":'You',},
        {'diagnose':json_output['diagnosis'],'conversation_id':conversation.unique_id}
    ]
    }
    )

@api_view(['POST'])
def upload_file(request):
    print("request data=",request.data)
    conversation_id = request.data.get('conversation_id')
    file = request.FILES.get('file')
    mime_type = request.data.get('mime_type')
    file_type = request.data.get('file_type')
    print("bool=",not conversation_id)
    if not conversation_id:
        print("ifffffff")
        unique_id = uuid.uuid4()
        conversation = Conversation.objects.create(unique_id=unique_id)
    else:
        print("elseeeeeeeeee",conversation_id)
        conversation = Conversation.objects.filter(unique_id=conversation_id).first()
        print("conversation=",conversation)

    print("conversation=",conversation)
    media_file = MediaFile.objects.create(conversation=conversation,file=file,mime_type=mime_type)
    return Response({'conversation':conversation.unique_id,'file_id':media_file.id},status=status.HTTP_200_OK)

@api_view(['POST'])
def generate_diagnosis(request):
    conversation_id = request.data.get('conversation_id')

    try:
        conversation = Conversation.objects.get(unique_id=conversation_id)
    except Conversation.DoesNotExist:
        return Response({'error':'conversation lost'},status.HTTP_404_NOT_FOUND)

    try:
        context = Context.objects.get(conversation_id=conversation)
    except:
        return Response({'error':'unable to generate diagnosis'},status.HTTP_404_NOT_FOUND)
    
    client = genai.Client()
    output = client.interactions.create(
    model="gemini-3.5-flash-lite",
    input=f'{context.context_data}',
    system_instruction=f"generate diagnosis for this issues stated by user")

    diagnosis_data = Diagnosis.objects.create(conversation_id=conversation,report_data=output.output_text)

    return Response({'diagnosis_data':diagnosis_data.report_data},status.HTTP_200_OK)

@api_view(['POST'])
def booking(request): 
    requested_service = request.data.get('service')
    vehicle = request.data.get('vehicle') 
    location = request.data.get('location') 
    phone_number = request.data.get('phone_number', '') 
    email = request.data.get('email', '') 

    if not requested_service: 
        return Response( {'error': 'Service is required.'},status=status.HTTP_400_BAD_REQUEST ) 
    
    if not vehicle: 
        return Response( {'error': 'Vehicle is required.'}, status=status.HTTP_400_BAD_REQUEST ) 
    
    if not location: 
        return Response( {'error': 'Location is required.'}, status=status.HTTP_400_BAD_REQUEST )

    Booking.objects.create( service=requested_service, location=location, vehicle=vehicle, phone_number=phone_number, email=email, status='confirmed' ) 
    
    return Response( { 'id': booking.id, 
        'service': booking.get_service_display(), 
        'location': booking.location, 'vehicle': booking.vehicle, 
        'status': booking.status, 
        'message': 'Booking created successfully.' }, 
        status=status.HTTP_201_CREATED )


