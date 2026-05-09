from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Model de usuário customizado estendendo o AbstractUser do Django.
    Inclui campos adicionais para trilha de aprendizado personalizada da IA.
    """
    data_de_nascimento = models.DateField(null=True, blank=False)
    telefone = models.CharField(max_length=20, blank=False)
    escola_ou_faculdade = models.CharField(max_length=255, null=True, blank=True)
    area_de_atuacao = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.username
