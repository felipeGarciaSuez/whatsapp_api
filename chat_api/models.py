from django.db import models

# Create your models here.

class Thread(models.Model):
    phone = models.CharField(max_length=20)
    threadId = models.CharField(max_length=200)

    def __str__(self):
        return f"NUMERO: {self.phone}, THREAD_ID: {self.threadId}"

    
    @classmethod
    def search_by_number(cls, phone):
        # Método de clase para buscar un Thread por número de teléfono.
        # :param telefono: El número de teléfono a buscar.
        # :return: QuerySet de instancias de Thread que coinciden con el número de teléfono dado.
        # print(cls.objects.filter(phone=phone).exists())
        return list(cls.objects.filter(phone=phone))
    
    @classmethod
    def create_thread(cls, phone, thread_id):
        # Método de clase para crear y guardar una instancia de Thread en la base de datos.
        # :param number: Número de teléfono.
        # :param thread_id: Identificador de hilo.
        # :return: Instancia de Thread creada.
        thread = cls(phone=phone, threadId=thread_id)
        thread.save()
        return thread.threadId