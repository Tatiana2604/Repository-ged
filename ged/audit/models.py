from django.db import models
from django.conf import settings

# Create your models here.
class AuditLog(models.Model):
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    action = models.CharField(max_length=255)
    modele = models.CharField(max_length=255)
    object_id = models.CharField(max_length=50, null=True, blank=True)
    ancienne_valeur = models.JSONField(null=True, blank=True)
    nouvelle_valeur = models.JSONField(null=True, blank=True)
    date_action = models.DateTimeField(auto_now_add=True)
    adresse_ip = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.utilisateur} - {self.action} sur {self.modele}({self.object_id})"


class Phase(models.Model):
    nom_phase = models.CharField(max_length=50, null=True)


class Procedure(models.Model):
    phase = models.ForeignKey(Phase, on_delete=models.CASCADE, related_name='procedures')
    numero_orde = models.IntegerField()
    procedure = models.CharField(max_length=90, null=True)
    document_procedure = models.BinaryField(null=True)
    document_travail_valide = models.BinaryField(null=True)
