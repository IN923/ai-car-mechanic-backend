from django.contrib import admin
from .models import Conversation,MediaFile,Diagnosis,Message
# Register your models here.
admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(MediaFile)
admin.site.register(Diagnosis)


