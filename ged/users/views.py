from django.shortcuts import render
from rest_framework.views import APIView
from django.core import serializers
import json 
from .models import Poste_comptable, Authentification, Zone, Utilisateur
from data.models import Piece
from django.http import JsonResponse
from django.middleware import csrf
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from rest_framework import status


# Create your views here.
class GetCSRFToken(APIView):
    permission_classes = []
    authentication_classes = []
    def get(self,request):
        token = csrf.get_token(request)
        return Response({"csrfToken": token})


class LoginView(APIView):
    permission_classes = []
    authentication_classes = []
    def post(self,request):
        username = request.data.get("identifiant")
        password = request.data.get("password")

        user = authenticate(request, identifiant=username, password=password) 

        if user is not None:
            login(request, user)
            texte = {"detail": "Connecté", "message": user.identifiant}
            return JsonResponse(texte)
        return Response({"error": "Incorrecte: Veuillez verifier vos identifiants et ressayer"}) 


class LogoutView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        logout(request)
        return Response({"detail": "Logged out"}, status=200)


class UserView(APIView):
    def get(self, request):
        if request.user.is_authenticated:

            auth = Authentification.objects.filter(identifiant=request.user.identifiant,password=request.user.password).values(
                'id',
                'utilisateur_id',
                'utilisateur__nom',
                'utilisateur__prenom',
                'utilisateur__fonction',
                'utilisateur__zone__nom_zone',
                'utilisateur__zone__id'
            )

            # user = {"id": auth.utilisateur.pk, "nom":auth.utilisateur.prenom, "fonction": auth.utilisateur.fonction}
            return  JsonResponse(list(auth), safe=False)
        return Response({"User": None}, status= status.HTTP_401_UNAUTHORIZED)


    def post(self, request):

        if request.data.get('action') == 'recuperer_auditeurs_zone':
            auditeurs = Utilisateur.objects.filter(fonction__icontains='auditeur',zone_id=request.data.get('zone')).values('id','nom','prenom', 'zone_id', 'zone__nom_zone')
            return JsonResponse(list(auditeurs),safe=False)
        
        elif request.data.get('action') == 'recuperer_auditeurs':
            auditeurs = Utilisateur.objects.filter(fonction__icontains='auditeur').values('id','nom','prenom', 'zone_id')
            return JsonResponse(list(auditeurs), safe=False)


class ZoneView(APIView):
    def get(self, request):
        zones = Zone.objects.all().values('id','nom_zone')
        return JsonResponse(list(zones), safe=False)


class PosteComptableView(APIView):
    def post(self, request):
        
        if request.data.get('action') == 'afficher_les_postes_comptables':
            poste = Poste_comptable.objects.filter(utilisateur_id=request.data.get('user_id')).values('id', 'nom_poste', 'utilisateur_id', 'utilisateur__zone_id')
            return JsonResponse(list(poste), safe=False)

        if request.data.get('action') == 'afficher_tous_les_postes_comptables':
            poste = Poste_comptable.objects.all().values('id', 'nom_poste', 'utilisateur_id', 'utilisateur__zone_id')
            return JsonResponse(list(poste), safe=False)
        
        elif request.data.get('action') == 'afficher_les_postes_comptables_zone':
            poste = Poste_comptable.objects.filter(utilisateur__zone__id=request.data.get('zone')).values('id', 'nom_poste', 'utilisateur_id', 'utilisateur__zone_id')
            return JsonResponse(list(poste), safe=False)

        elif request.data.get('action') == 'afficher_les_postes_comptable_specifique_a_une_piece':
            poste = Poste_comptable.objects.filter(utilisateur_id=request.data.get('utilisateur_id'),
            piece=Piece.objects.get(nom_piece=request.data.get('piece'))).distinct().values("id","nom_poste")
            return JsonResponse(list(poste), safe=False)

        elif request.data.get('action') == 'selctionner_poste_piece':
            poste = Poste_comptable.objects.select_related('piece').filter(piece__nom_piece=request.data.get('piece')).values_list('poste', flat=True).distinct()
            return JsonResponse(list(poste), safe=False)

    def get(self, request):
        poste = Poste_comptable.objects.all().values('poste').distinct().order_by('poste')
        return JsonResponse(list(poste), safe=False)

    

