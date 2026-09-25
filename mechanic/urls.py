from django.urls import path
from .views import generate_response,upload_file,diagnose

urlpatterns = [
    path('chat/', generate_response, name='generate_response'),
    path('upload/', upload_file, name='upload_file'),
    path('diagnose/<uuid:conversation_id>/', diagnose, name='diagnose'),
]

