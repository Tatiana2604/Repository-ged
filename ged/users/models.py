from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,BaseUserManager

# Create your models here.

class Zone(models.Model):
    nom_zone = models.CharField(max_length=50)


class Utilisateur(models.Model):
    # im = models.CharField(max_length=15)
    nom = models.CharField(max_length=80)
    prenom = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    fonction = models.CharField(max_length=30)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE,related_name='zones')
    def _str_(self):
        return f"{self.nom} {self.prenom}"


class Poste_comptable(models.Model):
    code_poste = models.CharField(max_length=25, null=True)
    nom_poste = models.CharField(max_length=50, null=True)
    responsable = models.CharField(max_length=50, null=True)
    poste = models.CharField(max_length=50, null=True)
    lieu = models.CharField(max_length=50,null=True)
    # categorie = models.CharField(max_length=20)
    # comptable = models.CharField(max_length=100)
    comptable_rattachement = models.ForeignKey("self", on_delete=models.SET_NULL, related_name ="poste_rattaches", null=True)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='poste_comptable',null=True)


class AuthentificationMananger(BaseUserManager):
    def create_user(self,identifiant,password=None, **extra_fields):
        if not identifiant:
            raise ValueError("L'identifiant est obligatoire")
        user = self.model(identifiant=identifiant, **extra_fields)
        user.set_password(password) #hash du mot de passe
        user.save(using=self._db)
        return user
    

    def create_superuser(self,identifiant,password=None, **extra_fields):
        extra_fields.setdefault("is_staff",True)
        extra_fields.setdefault("is_superuser",True)
        return self.create_user(identifiant,password, **extra_fields)
    

class Authentification(AbstractBaseUser, PermissionsMixin):
    identifiant = models.CharField(max_length=20,unique=True)
    date_joined = models.DateTimeField(auto_now_add=True, null=True)
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE, null=True, blank=True,related_name="authentification")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = AuthentificationMananger()

    USERNAME_FIELD = "identifiant"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.identifiant



    
