from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    cod_finca = models.CharField(max_length=100, blank=True, null= True, unique=True)
    nombre_finca = models.CharField(max_length=200, blank=True, null=True, unique=True)

    class Meta:
        db_table = 'USER'
        verbose_name = 'usuario'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{}'.format(self.username)