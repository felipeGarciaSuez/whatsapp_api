from django.db import models

# Create your models here.

class Thread(models.Model):
    phone = models.CharField(max_length=20)
    threadId = models.CharField(max_length=200)

    def __str__(self):
        return self.phone
    
    @classmethod
    def search_by_number(cls, number):
        # Método de clase para buscar un Thread por número de teléfono.
        # :param telefono: El número de teléfono a buscar.
        # :return: QuerySet de instancias de Thread que coinciden con el número de teléfono dado.
        return cls.objects.filter(phone=number)