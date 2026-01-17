from django.db import models
from users.models import Poste_comptable

# Create your models here.
class Piece(models.Model):
    nom_piece = models.CharField(max_length=20)
    periode = models.CharField(max_length=30)
    created_at = models.DateField(auto_now_add=True,null=True)
    updated_at = models.DateField(auto_now=True,null=True)
    poste_comptable = models.ManyToManyField(Poste_comptable, related_name="piece_comptables")

    def _str_(self):
        return self.nom


class Document(models.Model):
    nom_fichier = models.CharField(max_length= 255,null=True)
    type = models.CharField(max_length=10,null= True)
    contenu = models.BinaryField(null=True)
    date_arrivee = models.DateField()
    created_at = models.DateField(auto_now_add=True)
    exercice = models.CharField(max_length=10,null=True)
    mois = models.CharField(max_length=2 , null=True)
    piece = models.ForeignKey(Piece ,on_delete=models.CASCADE,related_name="piece_document",null=True)
    poste_comptable = models.ForeignKey(Poste_comptable,on_delete=models.CASCADE,related_name="documents", null = True)
    version = models.IntegerField(default=1)

    def _str_(self):
        return self.nom_fichier


class Archivage(models.Model):
    document = models.OneToOneField(Document, on_delete=models.CASCADE, related_name='archives')


class Exercice(models.Model):
    annee = models.CharField(max_length=5, unique=True)
