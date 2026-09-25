# AI Car Mechanic Backend

This project is a Django REST API backend for an AI-powered car mechanic assistant. It accepts vehicle questions, optional uploaded media files, stores conversation context, and uses Google Gemini for AI-powered assistant responses and lightweight diagnostic summaries.

## Tech stack

- Python 3.11+
- Django 6.1
- Django REST Framework
- SQLite (default local database)
- Google GenAI SDK for Gemini model integration
- django-cors-headers
- django-environ

## Project structure

```text
ai_car_mechanic/
├── ai_car_mechanic/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── mechanic/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── prompts.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── uploads/
├── .env
├── db.sqlite3
├── manage.py
└── README.md
```

## Short architecture explanation

The application follows a simple Django app architecture:

- `ai_car_mechanic/` contains the project settings and root URL routing.
- `mechanic/` is the feature app that handles chatbot behavior, uploaded files, and diagnostic storage.
- `models.py` defines the persistence layer:
  - `Chat`: stores user input, AI output, and conversation identifiers.
  - `Context`: stores structured JSON context extracted from chats.
  - `FileUpload`: stores uploaded files and associated metadata.
  - `DiagnosticReport`: stores diagnostic output linked to a conversation.
- `views.py` contains the API endpoints for chat generation, file upload, and diagnosis requests.
- `prompts.py` contains the system instructions sent to Gemini.
- The backend integrates with Google Gemini via `google.genai` to generate car-related responses and context extraction.

This is suitable for local development and prototype work. It is not production-hardened security-wise.

## Setup instructions

### 1. Clone and open the project

```bash
cd "c:\Users\inder.DESKTOP-SQUU3T5\Desktop\ai car mechanic\backend\ai_car_mechanic"
```

### 2. Create a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install django djangorestframework django-environ django-cors-headers google-genai
```

### 4. Configure environment variables

Create a `.env` file in the project root with the following values:

```env
SECRET_KEY=your_django_secret_key
GEMINI_API_KEY=your_google_gemini_api_key
```

Example:

```env
SECRET_KEY=django-insecure-your-secret-key
GEMINI_API_KEY=your_actual_api_key_here
```

The project reads these values through `django-environ` in `ai_car_mechanic/settings.py`.

### 5. Run database migrations

```bash
python manage.py migrate
```

### 6. Start the development server

```bash
python manage.py runserver
```

The backend will be available at:

```text
http://127.0.0.1:8000/
```

## API documentation

All endpoints are mounted under `/api/`.

### 1) Generate a chat response

Endpoint:

```http
POST /api/chat/
```

Request body:

```json
{
  "input_text": "My Toyota Corolla makes a knocking sound when idling.",
  "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
  "file_ids": [1, 2]
}
```

Notes:

- `input_text` is the user message to the mechanic assistant.
- `conversation_id` is optional. If omitted, a new UUID is created.
- `file_ids` is optional and contains uploaded file records from the upload endpoint.
- Uploaded image/audio/video/PDF files are processed and passed into the Gemini request as media context.

Example response:

```json
{
  "response": "The knocking sound may indicate ...",
  "conversation_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### 2) Upload a file

Endpoint:

```http
POST /api/upload/
```

Form-data fields:

- `file` — uploaded file
- `conversation_id` — optional UUID for the related conversation
- `file_type` — optional descriptive type
- `file_mime_type` — optional mime type

Example request using curl:

```bash
curl -X POST http://127.0.0.1:8000/api/upload/ \
  -F "file=@/path/to/car_photo.jpg" \
  -F "conversation_id=123e4567-e89b-12d3-a456-426614174000" \
  -F "file_type=image" \
  -F "file_mime_type=image/jpeg"
```

Example response:

```json
{
  "message": "File uploaded successfully.",
  "file_id": 5
}
```

### 3) Generate a diagnostic report

Endpoint:

```http
POST /api/diagnose/<conversation_id>/
```

Example:

```http
POST /api/diagnose/123e4567-e89b-12d3-a456-426614174000/
```

Example response:

```json
{
  "diagnostic_report": {
    "diagnosis": "Sample diagnosis based on context data."
  }
}
```

> Note: The current diagnosis endpoint is a starter implementation and returns a sample report payload rather than a full real diagnostic engine.

## Supported file types

The current upload logic handles these file categories:

- Images: `image/*`
- Audio: `audio/*`
- Video: `video/*`
- PDF: `application/pdf`

Files larger than 20 MB are rejected with a `400 Bad Request`.

## Development notes

- The app uses SQLite for local development.
- CORS is enabled for `http://localhost:3000` and `http://127.0.0.1:5173`.
- The app currently runs with `DEBUG = True` in settings.
- `uploads/` is the default upload directory.

## Common commands

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
python manage.py shell
```

## Troubleshooting

### Missing environment variables

If Django raises an error about missing `GEMINI_API_KEY` or `SECRET_KEY`, make sure your `.env` file exists in the project root and contains the required keys.

### Gemini API issues

Ensure that the Gemini API key is valid and has access to the model in use by the app. The code currently calls the Gemini API with `gemini-3.5-flash-lite`.

### File upload problems

Verify that the uploaded file type is in the supported set and that the file is smaller than 20 MB.

## License

This project is currently provided as a local backend prototype without a formal license file.
