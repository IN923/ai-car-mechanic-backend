from django.db import models

# Create your models here.

class Conversation(models.Model):
    unique_id = models.UUIDField(editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    gemini_conversation_id = models.CharField(null=True)

    def __str__(self):
        return f'conversation-{self.unique_id}'

class Message(models.Model):
    ROLE_CHOICES = [
        ('user','User'),
        ('assistant','Assistant')
    ]

    conversation = models.ForeignKey(Conversation,on_delete=models.CASCADE)
    role = models.CharField(choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField(null=True)

class MediaFile(models.Model):
    conversation = models.ForeignKey(Conversation,on_delete=models.CASCADE,null=True)
    file = models.FileField()
    message = models.ForeignKey(Message,on_delete=models.CASCADE,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    mime_type = models.CharField(null=True)

# class Diagnosis(models.Model):
#     conversation = models.ForeignKey(Conversation,on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)
#     summary = models.TextField()
#     recommended_service = models.CharField()
#     severity = models.CharField()

class Diagnosis(models.Model):
    conversation_id = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='diagnostic_reports',null=True)
    report_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

class Context(models.Model):
    conversation_id = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='contexts')
    context_data = models.JSONField(null=True)

class Booking(models.Model):
    SERVICE_CHOICES = [
        ('diagnostic inspection', 'diagnostic inspection'),
        ('engine repair', 'engine repair')
    ]

    service = models.CharField(choices=SERVICE_CHOICES)
    location = models.CharField()
    vehicle = models.CharField()
    phone_number = models.CharField()
    email = models.EmailField()
    status = models.CharField(default='confirmed')


# class Chat(models.Model):
#     conversation_id = models.UUIDField(editable=False)
#     input_text = models.TextField()
#     output_text = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Chat {self.id} - {self.created_at}"

# class Context(models.Model):
#     conversation_id = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='contexts')
#     context_data = models.JSONField()

# class FileUpload(models.Model):
#     file = models.FileField(upload_to='uploads/')
#     uploaded_at = models.DateTimeField(auto_now_add=True)
#     conversation_id = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='file_uploads', null=True, blank=True)
#     file_type = models.CharField(max_length=50,null=True,blank=True)
#     mime_type = models.CharField(max_length=100,null=True,blank=True)


# class DiagnosticReport(models.Model):
#     conversation_id = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='diagnostic_reports')
#     report_data = models.JSONField()
#     created_at = models.DateTimeField(auto_now_add=True)