from django.db import models

# Create your models here.

class Request(models.Model):
    phone = models.CharField(max_length=20)
    threadId = models.CharField(max_length=200)
    conversa = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.phone