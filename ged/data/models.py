from django.db import models

# Create your models here.
class PieceComptable(models.Model):
    nom = models.CharField(max_length=20)
    periode = models.CharField(max_length=30)
