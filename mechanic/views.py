from django.shortcuts import render
from google import genai
from google.genai import types
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .prompts import SYSTEM_INSTRUCTIONS,CONTEXT_SYSTEM_INSTRUCTION
from .models import Chat,Context, DiagnosticReport, FileUpload
import uuid
import base64
# Create your views here.

@api_view(['POST'])
def generate_response(request):
    input_text = request.data.get('input_text')
    conversation_id = request.data.get('conversation_id')
    file_ids = request.data.get('file_ids',[])
    gemini_input = []
    for file_id in file_ids:

        try:
            file_upload = FileUpload.objects.get(
                id=file_id
            )
        except FileUpload.DoesNotExist:
            return Response(
                {
                    "error":
                    f"File {file_id} not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

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

            gemini_input.append({
                "type": "image",
                "data": file_b64,
                "mime_type": mime_type
            })

        # ---------------------------
        # AUDIO
        # ---------------------------
        elif mime_type.startswith("audio/"):

            gemini_file = client.files.upload(
                file=file_upload.file.path
            )

            gemini_input.append({
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

            gemini_input.append({
                "type": "video",
                "uri": gemini_file.uri,
                "mime_type": gemini_file.mime_type
            })

        # ---------------------------
        # PDF
        # ---------------------------
        elif mime_type == "application/pdf":

            gemini_file = client.files.upload(
                file=file_upload.file.path
            )

            gemini_input.append({
                "type": "document",
                "uri": gemini_file.uri,
                "mime_type": gemini_file.mime_type
            })

        else:
            return Response(
                {
                    "error":
                    f"Unsupported file type: {mime_type}"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        
    # if not input_text:
    #     return Response({"error": "Input text is required."}, status=status.HTTP_400_BAD_REQUEST)

    client = genai.Client()
    output = client.interactions.create(
    model="gemini-3.5-flash-lite",
    input=[
        {'type': 'text', 'text': f'{input_text}'},
    ],
    system_instruction=f"{SYSTEM_INSTRUCTIONS}",
    extra_body={
        "generation_config": {
            "max_output_tokens": 100
        }
    }
    )

    print(output.output_text)

    if not conversation_id:
        conversation_id = uuid.uuid4()

    stored_chat = Chat.objects.create(input_text=input_text, output_text=output.output_text, conversation_id=conversation_id)

    extracted_context = extract_context(input_text,output.output_text)
    Context.objects.create(conversation_id=stored_chat, context_data=extracted_context)

    return Response({"response": output.output_text, "conversation_id": stored_chat.conversation_id}, status.HTTP_200_OK)

def extract_context(input_text,output_text):

    conversation = f"""
        User:
        {input_text}

        Assistant:
        {output_text}
    """

    if not input_text or not output_text:
        return None

    client = genai.Client()
    client.max_output_tokens = 5
    response = client.interactions.create(
    model="gemini-3.5-flash-lite",
    input=f'{input_text}',
    system_instruction=f"{CONTEXT_SYSTEM_INSTRUCTION}",
    extra_body={
        "generation_config": {
            "max_output_tokens": 100
        }
    }
    )

    return response.output_text

@api_view(['POST'])
def diagnose(request, conversation_id):
    try:
        chat = Chat.objects.filter(conversation_id=conversation_id).first()
        contexts = Context.objects.filter(conversation_id=chat)
        context_data = [context.context_data for context in contexts]

        diagnostic_report = DiagnosticReport.objects.create(conversation_id=chat, report_data={"diagnosis": "Sample diagnosis based on context data."})

        return Response({
            "diagnostic_report": diagnostic_report.report_data
        }, status=status.HTTP_200_OK)

    except Chat.DoesNotExist:
        return Response({"error": "Conversation not found."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def upload_file(request):
    uploaded_file = request.FILES.get('file')
    conversation_id = request.data.get('conversation_id')
    file_type = request.data.get('file_type')
    file_mime_type = request.data.get('file_mime_type')
    print("file data:", request.data,file_type,file_mime_type)
    print(f"Received file: {uploaded_file}, Conversation ID: {conversation_id}")
    if not uploaded_file:
        return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

    if uploaded_file.size > 20 * 1024 * 1024:  # 20MB limit
        return Response({"error": "File size exceeds the limit of 20MB."}, status=status.HTTP_400_BAD_REQUEST)

    if not conversation_id:
        conversation_id = uuid.uuid4()
        stored_chat = Chat.objects.create(input_text="File uploaded", output_text="File uploaded", conversation_id=conversation_id)
        file = FileUpload.objects.create(file=uploaded_file, conversation_id=stored_chat, file_type=file_type, mime_type=file_mime_type)
    else:
        stored_chat = Chat.objects.filter(conversation_id=conversation_id).first()
        file = FileUpload.objects.create(file=uploaded_file, conversation_id=stored_chat, file_type=file_type, mime_type=file_mime_type)

    return Response({"message": "File uploaded successfully.", "file_id": file.id}, status=status.HTTP_200_OK)

