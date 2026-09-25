from django.contrib import admin
from .models import Chat, Context, FileUpload
# Register your models here.
admin.site.register(Chat)
admin.site.register(Context)
admin.site.register(FileUpload)
