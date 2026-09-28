from django.urls import path
from .views import generate_response,upload_file,generate_diagnosis,booking

urlpatterns = [
    path('chat/', generate_response, name='generate_response'),
    path('upload/', upload_file, name='upload_file'),
    path('diagnose/', generate_diagnosis, name='diagnose'),
    path('booking/',booking,name='booking')
]

