from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.

class local(models.Model):
    insc = models.CharField(max_length=20)
    date_added = models.DateTimeField(auto_now_add=True)
    endereco = models.CharField(max_length= 50)

    def __str__(self):   
        """Devolve uma representação em int do modelo""" 
        return str(self.insc)

class StatusOpcoes(models.TextChoices):
    FOGO = 'fogo', 'Fogo'
    LIXO = 'lixo', 'Lixo'
    AMBULANTE = 'ambulante','Ambulante'
    NULL = 'null', 'Sem status'

class Ocorrencia(models.Model):
    nsc = models.ForeignKey(local, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    status = models.CharField(
        max_length=10,  # Ajustado para acomodar o comprimento do maior valor ('null')
        choices=StatusOpcoes.choices,  
        default=StatusOpcoes.NULL,  # Usando a enumeração corretamente
    )
    desc = models.TextField()
    noti = models.BooleanField(default=False)

    def __str__(self):   
        """Devolve uma representação em int do modelo""" 
        return self.desc

   
   





