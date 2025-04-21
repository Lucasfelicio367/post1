from django.db import models
from django.conf import settings
from django.utils import timezone


class local(models.Model):
    insc = models.CharField(max_length=200)
    endereco = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.insc


class Ocorrencia(models.Model):

    STATUS_CHOICES = [
        ('fogo', 'Fogo'),
        ('lixo', 'Lixo'),
        ('barulho', 'Barulho'),
        ('ambulante', 'Ambulante'),
        ('terreno sujo', 'Terreno Sujo'),
        ('costrução comprometida', 'Construção Comprometida'),
        ('invazão de plantas', 'Invazão de Plantas'),
        ('outro', 'Outro'),
    ]

    ANDAMENTO_CHOICES = [
        ("aguardando prazo", "Aguardando Prazo"),
        ("resolvido", "Resolvido"),
        ("vencido", "Vencido"),
    ]

    local = models.ForeignKey(local, on_delete=models.CASCADE)
    status = models.CharField(max_length=200, choices=STATUS_CHOICES)
    desc = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    noti = models.BooleanField(default=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    prazo = models.DateField(null=True, blank=True)
    andamento = models.CharField(
        max_length=20,
        choices=ANDAMENTO_CHOICES,
        default="aguardando prazo"
    )

    def atualizar_andamento(self):
        if self.andamento == "resolvido":
            return
        if self.prazo:
            if timezone.now().date() > self.prazo:
                self.andamento = "vencido"
            else:
                self.andamento = "aguardando prazo"
        else:
            self.andamento = "aguardando prazo"

    def save(self, *args, **kwargs):
        # Só atualiza automaticamente se o andamento NÃO for "resolvido"
        if self.andamento != "resolvido":
            self.atualizar_andamento()
        super().save(*args, **kwargs)
