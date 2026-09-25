from django.db import models

# Create your models here.

class Chat(models.Model):
    conversation_id = models.UUIDField(editable=False)
    input_text = models.TextField()
    output_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat {self.id} - {self.created_at}"

class Context(models.Model):
    conversation_id = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='contexts')
    context_data = models.JSONField()

class FileUpload(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    conversation_id = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='file_uploads', null=True, blank=True)
    file_type = models.CharField(max_length=50,null=True,blank=True)
    mime_type = models.CharField(max_length=100,null=True,blank=True)


class DiagnosticReport(models.Model):
    conversation_id = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='diagnostic_reports')
    report_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)