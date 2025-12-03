<<<<<<< HEAD
# from rest_framework import viewSets
from rest_framework.response import Response
from rest_framework import status
from .models import Document
from.serializers import DocumentSerializer
from rest_framework.views import APIView
from .models import Piece, Archivage
from users.models import Poste_comptable
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.db.models import Q
from datetime import datetime, date
from calendar import monthrange 
import os.path
import shutil
import json


# class DocumentCreateViewSet(viewSets.ModelViewSet):
#     def post(self,request):
#         serializer = DocumentSerializer(data=request.data)
#         if serializer.issubclass_valid():
#             serializer.save()
#             return Response({"message":"Document ajouté avec succès !"},status=status.HTTP_201_CREATED)
#         return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)




# ===== ARCHIVAGE =====

# class PiecesStatusView(APIView):
#     """
#     Retourne le statut des pièces pour un poste comptable donné,
#     avec possibilité de filtrer par mois, exercice et pièce spécifique,
#     en tenant compte de la période (mensuelle, décadaire) et du retard.
#     """

#     def post(self, request):
#         data = request.data
#         poste_id = data.get("poste_id")
#         mois = data.get("mois")
#         exercice = data.get("exercice")
#         piece_id = data.get("piece_id")  # optionnel

#         if not poste_id:
#             return JsonResponse({"error": "poste_id requis"}, status=400)

#         # Vérifie que le poste existe
#         try:
#             poste = Poste_comptable.objects.get(id=poste_id)
#         except Poste_comptable.DoesNotExist:
#             return JsonResponse({"error": "Poste comptable introuvable"}, status=404)

#         # Récupère toutes les pièces liées à ce poste
#         pieces_qs = poste.piece_comptables.all()
#         if piece_id:
#             pieces_qs = pieces_qs.filter(id=piece_id)

#         resultats = []
#         today = date.today()

#         for piece in pieces_qs:
#             # Filtrer documents du poste/piece/mois/exercice
#             filtres = Q(piece=piece, poste_comptable=poste)
#             if mois:
#                 filtres &= Q(mois=mois)
#             if exercice:
#                 filtres &= Q(exercice=exercice)

#             documents = Document.objects.filter(filtres).order_by('date_arrivee')

#             periode = piece.periode.lower() if piece.periode else "mensuelle"
#             piece_status = []
#             late_status = []
#             docs_by_period = []

#             if (periode == "décadaire" or periode == "decadaire") and mois and exercice:
#                 mois_int = int(mois)
#                 exercice_int = int(exercice)
#                 last_day = monthrange(exercice_int, mois_int)[1]

#                 # Décades : 1–10, 11–20, 21–fin du mois
#                 decades = [(1, 10), (11, 20), (21, last_day)]
#                 for start, end in decades:
#                     # Filtrer uniquement les documents avec date_arrivee définie
#                     docs_in_decade = [
#                         {"id": doc.id, "nom_fichier": doc.nom_fichier,
#                          "date_arrivee": doc.date_arrivee.strftime("%Y-%m-%d")}
#                         for doc in documents if doc.date_arrivee and start <= doc.date_arrivee.day <= end
#                     ]
#                     # Arrivée
#                     piece_status.append(bool(docs_in_decade))
#                     # Documents
#                     docs_by_period.append(docs_in_decade)
#                     # Retard : décade terminée et aucun document
#                     dec_end_date = date(exercice_int, mois_int, end)
#                     late_status.append(not docs_in_decade and today > dec_end_date)

#             else:
#                 # Mensuelle ou autre période
#                 piece_status = [documents.exists()]
#                 docs_by_period = [[
#                     {"id": doc.id, "nom_fichier": doc.nom_fichier,
#                      "date_arrivee": doc.date_arrivee.strftime("%Y-%m-%d")}
#                     for doc in documents if doc.date_arrivee
#                 ]]
#                 if mois and exercice:
#                     mois_int = int(mois)
#                     exercice_int = int(exercice)
#                     last_day = monthrange(exercice_int, mois_int)[1]
#                     dec_end_date = date(exercice_int, mois_int, last_day)
#                     late_status = [not documents.exists() and today > dec_end_date]
#                 else:
#                     late_status = [False]

#             resultats.append({
#                 "id": piece.id,
#                 "nom_piece": piece.nom_piece,
#                 "periode": piece.periode,
#                 "arrived": piece_status,
#                 "late": late_status,
#                 "documents": docs_by_period
#             })

#         return JsonResponse(resultats, safe=False, status=200)


# class PiecesStatusView(APIView):
#     """
#     Retourne le statut des pièces pour un poste comptable donné,
#     avec possibilité de filtrer par mois, exercice et pièce spécifique,
#     en tenant compte de la période (mensuelle, décadaire) et du retard.
#     """

#     def post(self, request):
#         data = request.data
#         poste_id = data.get("poste_id")
#         mois = data.get("mois")
#         exercice = data.get("exercice")
#         piece_id = data.get("piece_id")  # optionnel

#         if not poste_id:
#             return JsonResponse({"error": "poste_id requis"}, status=400)

#         try:
#             poste = Poste_comptable.objects.get(id=poste_id)
#         except Poste_comptable.DoesNotExist:
#             return JsonResponse({"error": "Poste comptable introuvable"}, status=404)

#         pieces_qs = poste.piece_comptables.all()
#         if piece_id:
#             pieces_qs = pieces_qs.filter(id=piece_id)

#         resultats = []
#         today = date.today()

#         for piece in pieces_qs:
#             filtres = Q(piece=piece, poste_comptable=poste)
#             if mois:
#                 filtres &= Q(mois=mois)
#             if exercice:
#                 filtres &= Q(exercice=exercice)

#             documents = Document.objects.filter(filtres).order_by('date_arrivee')
#             periode = piece.periode.lower() if piece.periode else "mensuelle"

#             piece_status = []
#             late_status = []
#             docs_by_period = []

#             if periode == "decadaire" and mois and exercice:
#                 mois_int = int(mois)
#                 exercice_int = int(exercice)
#                 last_day = monthrange(exercice_int, mois_int)[1]

#                 # Décades
#                 decades = [(1, 10), (11, 20), (21, last_day)]

#                 for idx, (start, end) in enumerate(decades):
#                     dec_end_date = date(exercice_int, mois_int, end)

#                     # Filtrer documents correspondant à cette décade via split(", ")
#                     docs_in_decade = []
#                     for doc in documents:
#                         parts = doc.nom_fichier.split(", ")
#                         if len(parts) > 1 and parts[1].strip().lower() == f"decade {idx + 1}":
#                             docs_in_decade.append({
#                                 "id": doc.id,
#                                 "nom_fichier": doc.nom_fichier,
#                                 "date_arrivee": doc.date_arrivee.strftime("%Y-%m-%d") if doc.date_arrivee else None
#                             })

#                     piece_status.append(bool(docs_in_decade))
#                     docs_by_period.append(docs_in_decade)

#                     # Calcul du retard
#                     if docs_in_decade:
#                         # True si au moins un document est arrivé après la fin de la décade
#                         late_status.append(any(
#                             doc['date_arrivee'] and date.fromisoformat(doc['date_arrivee']) > dec_end_date
#                             for doc in docs_in_decade
#                         ))
#                     else:
#                         # True si aucun document et décade dépassée
#                         late_status.append(today > dec_end_date)

#             else:
#                 # Mensuelle ou autre
#                 docs_list = [
#                     {
#                         "id": doc.id,
#                         "nom_fichier": doc.nom_fichier,
#                         "date_arrivee": doc.date_arrivee.strftime("%Y-%m-%d") if doc.date_arrivee else None
#                     }
#                     for doc in documents
#                 ]
#                 piece_status = [bool(docs_list)]
#                 docs_by_period = [docs_list]

#                 if mois and exercice:
#                     mois_int = int(mois)
#                     exercice_int = int(exercice)
#                     last_day = monthrange(exercice_int, mois_int)[1]
#                     dec_end_date = date(exercice_int, mois_int, last_day)
#                     late_status = [not docs_list and today > dec_end_date]
#                 else:
#                     late_status = [False]

#             resultats.append({
#                 "id": piece.id,
#                 "nom_piece": piece.nom_piece,
#                 "periode": piece.periode,
#                 "arrived": piece_status,
#                 "late": late_status,
#                 "documents": docs_by_period
#             })

#         return JsonResponse(resultats, safe=False, status=200)
from datetime import date, datetime
from calendar import monthrange
from django.http import JsonResponse
from django.db.models import Q
from rest_framework.views import APIView
from .models import Poste_comptable, Document
from django.shortcuts import render, get_object_or_404
import hashlib


def hash_local_file(file):
    hash_func = hashlib.sha256()
    for chunk in file.chunks():
        hash_func.update(chunk)
    return hash_func.hexdigest()

def hash_binary(binary):
    return hashlib.sha256(binary).hexdigest()


class VerificationView(APIView):

    def post(self, request):
        # Vérifier si le fichier est présent
        if "local_file" not in request.FILES:
            return Response(
                {"error": "Aucun fichier reçu."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1. Récupérer fichier local
        local_file = request.FILES["local_file"]
        local_hash = hash_local_file(local_file)

        # 2. Vérifier si l'id du document sélectionné est présent
        id_doc = request.POST.get("id_doc")
        if not id_doc:
            return Response(
                {"error": "Aucun id_doc envoyé."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Récupérer le document en base correspondant
        try:
            document = Document.objects.get(id=id_doc)
        except Document.DoesNotExist:
            return Response(
                {"error": "Document introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 4. Comparaison
        if not document.contenu:
            return Response({
                "identique": False,
                "message": "Le document sélectionné n'a pas de contenu enregistré."
            })

        doc_hash = hash_binary(document.contenu)

        # 5. Résultat comparaison
        if doc_hash == local_hash:
            return Response({
                "identique": True,
                "document": document.nom_fichier,
                "message": "Le document local est IDENTIQUE au document sélectionné."
            })

        return Response({
            "identique": False,
            "document": document.nom_fichier,
            "message": "Les deux documents sont différents."
        })


class PiecesStatusView(APIView):
    """
    Retourne le statut des pièces pour un poste comptable donné,
    avec possibilité de filtrer par mois, exercice, pièce spécifique et période
    (mensuelle, décadaire, journalière), en tenant compte du retard.
    """

    def post(self, request): 
        data = request.data
        nom_poste = data.get("poste_comptable")
        mois = data.get("mois")
        exercice = data.get("exercice")
        piece_id = data.get("piece_id")      
        periode_filtre = data.get("periode")

        if not nom_poste:
            return JsonResponse({"error": "poste_id requis"}, status=400)

        try:
            poste = Poste_comptable.objects.get(nom_poste=nom_poste)
        except Poste_comptable.DoesNotExist:
            return JsonResponse({"error": "Poste comptable introuvable"}, status=404)

        pieces_qs = poste.piece_comptables.all()

        if piece_id:
            pieces_qs = pieces_qs.filter(id=piece_id)
        if periode_filtre:
            pieces_qs = pieces_qs.filter(periode__iexact=periode_filtre)

        resultats = []
        today = date.today()

        for piece in pieces_qs:
            filtres = Q(piece=piece, poste_comptable=poste)
            if mois:
                filtres &= Q(mois=mois)
            if exercice:
                filtres &= Q(exercice=exercice)

            # ---------------------------
            # 🔥 SYSTÈME DE VERSIONING GLOBAL
            # Conserve uniquement la dernière version par document logique
            # ---------------------------
            documents_qs = Document.objects.filter(filtres).select_related("piece", "poste_comptable")

            latest_docs_dict = {}
            for doc in documents_qs:
                parts = doc.nom_fichier.split(", ")
                info_supp = parts[1] if len(parts) > 1 else ""

                key = (doc.piece.id, doc.exercice, doc.mois, info_supp)

                if key not in latest_docs_dict or doc.version > latest_docs_dict[key].version:
                    latest_docs_dict[key] = doc

            documents = list(latest_docs_dict.values())

            periode = piece.periode.lower() if piece.periode else "mensuelle"

            # -----------------------
            # 1️⃣ Gestion DÉCADAIRE
            # -----------------------
            if periode == "décadaire" and mois and exercice:
                mois_int = int(mois)
                exercice_int = int(exercice)
                last_day = monthrange(exercice_int, mois_int)[1]

                decades = [(1, 10), (11, 20), (21, last_day)]

                for idx, (start, end) in enumerate(decades):
                    dec_end_date = date(exercice_int, mois_int, end)

                    docs_in_decade = []
                    for doc in documents:
                        parts = doc.nom_fichier.split(", ")
                        if len(parts) > 1:
                            periode_str = parts[1].strip().lower()
                            if periode_str == f"decade {idx + 1}":
                                docs_in_decade.append({
                                    "id": doc.id,
                                    "nom_fichier": doc.nom_fichier,
                                    "date_arrivee": doc.date_arrivee.strftime("%Y-%m-%d") if doc.date_arrivee else None
                                })

                    arrived = bool(docs_in_decade)
                    if arrived:
                        late = any(
                            d["date_arrivee"] and date.fromisoformat(d["date_arrivee"]) > dec_end_date
                            for d in docs_in_decade
                        )
                    else:
                        late = today > dec_end_date

                    resultats.append({
                        "id": piece.id,
                        "nom_piece": f"{piece.nom_piece} - Décade {idx + 1}",
                        "periode": piece.periode,
                        "decade": idx + 1,
                        "intervalle": f"{start}-{end}",
                        "date_limite": dec_end_date.strftime("%Y-%m-%d"),
                        "arrived": [arrived],
                        "late": [late],
                        "documents": [docs_in_decade]
                    })

            # -----------------------
            # 2️⃣ Gestion JOURNALIÈRE
            # -----------------------
            elif periode == "journalière" and mois and exercice:

                mois_int = int(mois)
                exercice_int = int(exercice)
                nb_jours = monthrange(exercice_int, mois_int)[1]

                # Filtrage des docs journaliers (dernière version déjà appliquée)
                docs_sje = documents

                for jour in range(1, nb_jours + 1):
                    date_jour = date(exercice_int, mois_int, jour)
                    date_str = date_jour.strftime("%Y-%m-%d")

                    arrived = False
                    documents_for_day = []

                    for doc in docs_sje:
                        parts = [p.strip() for p in doc.nom_fichier.split(",") if p.strip()]
                        if len(parts) > 1 and parts[1] == date_str:
                            arrived = True
                            try:
                                date_sje = datetime.strptime(parts[1], "%Y-%m-%d").date()
                            except ValueError:
                                date_sje = date_jour

                            retard = doc.date_arrivee and doc.date_arrivee > date_sje
                            documents_for_day.append({
                                "id": doc.id,
                                "nom_fichier": doc.nom_fichier,
                                "date_arrivee": doc.date_arrivee.strftime("%Y-%m-%d") if doc.date_arrivee else None,
                                "retard": retard
                            })

                    resultats.append({
                        "id": piece.id,
                        "nom_piece": f"{piece.nom_piece} ({date_str})",
                        "periode": piece.periode,
                        "date": date_str,
                        "arrived": [arrived],
                        "late": [any(doc['retard'] for doc in documents_for_day)],
                        "documents": [documents_for_day]
                    })

            # -----------------------
            # 3️⃣ Gestion MENSUELLE
            # -----------------------
            else:

                docs_list = [
                    {
                        "id": doc.id,
                        "nom_fichier": doc.nom_fichier,
                        "date_arrivee": doc.date_arrivee.strftime("%Y-%m-%d") if doc.date_arrivee else None
                    }
                    for doc in documents
                ]

                piece_status = [bool(docs_list)]
                docs_by_period = [docs_list]

                if mois and exercice:
                    mois_int = int(mois)
                    exercice_int = int(exercice)

                    if mois_int == 12:
                        mois_suiv, annee_suiv = 1, exercice_int + 1
                    else:
                        mois_suiv, annee_suiv = mois_int + 1, exercice_int

                    date_limite = date(annee_suiv, mois_suiv, 15)

                    late_status = [
                        (not docs_list and today > date_limite) or
                        any(
                            d["date_arrivee"] 
                            and date.fromisoformat(d["date_arrivee"]) > date_limite
                            for d in docs_list
                        )
                    ]
                else:
                    late_status = [False]

                resultats.append({
                    "id": piece.id,
                    "nom_piece": piece.nom_piece,
                    "periode": piece.periode,
                    "arrived": piece_status,
                    "late": late_status,
                    "documents": docs_by_period
                })

        return JsonResponse(resultats, safe=False, status=200)



class ArchiveView(APIView):

    def post(self, request):
        
        if request.data.get('action') == 'ajouter_archives':
            """Archivage d’un ou plusieurs documents"""
            document_ids = request.data.get('id_docs').split(",")
            
            if not document_ids:
                return JsonResponse({"error": "Aucun document sélectionné"}, status=400)

            for doc_id in document_ids:
                try:
                    doc = Document.objects.get(id=doc_id)
                    # On crée l’archive seulement si elle n’existe pas déjà
                    Archivage.objects.get_or_create(document=doc)
                except Document.DoesNotExist:
                    continue

            return JsonResponse({"succes": "Documents archivés avec succès"})

        elif request.data.get('action') == 'archives_documents_auditeur':
            archive = Archivage.objects.select_related('piece', 'poste_comptable').filter(document__poste_comptable__utilisateur_id=request.data.get('utilisateur')).values(
                'document__id',
                'document__nom_fichier',
                'document__poste_comptable__nom_poste',
                'document__piece__nom_piece',
                'document__date_arrivee',
                'document__exercice',
                'document__mois',
                'document__created_at',
                'document__type')
            return JsonResponse(list(archive), safe=False)

        elif request.data.get('action') == 'archives_documents_chef_unite':
            archive = Archivage.objects.filter(document__poste_comptable__utilisateur__zone__nom_zone=request.data.get('zone')).values(
                'document__id',
                'document__nom_fichier',
                'document__poste_comptable__nom_poste',
                'document__piece__nom_piece',
                'document__date_arrivee',
                'document__exercice',
                'document__mois',
                'document__created_at',
                'document__type')
            return JsonResponse(list(archive),safe=False)

        elif request.data.get('action') == 'archives_documents_directeur':
            archive = Archivage.objects.all().values(
                'document__id',
                'document__nom_fichier',
                'document__poste_comptable__nom_poste',
                'document__piece__nom_piece',
                'document__date_arrivee',
                'document__exercice',
                'document__mois',
                'document__created_at',
                'document__type')
            return JsonResponse(list(archive),safe=False)

        elif request.data.get('action') == 'telecharger_archives':
            home = os.path.expanduser("~")
            downloads = os.path.join(home,"Downloads")

            id_docs = request.data.get('id_docs').split(",")

            for id in id_docs:
                archive = Archivage.objects.filter(document_id=id).values('document__contenu', 'document__nom_fichier')
                destination_file = os.path.join(downloads, archive[0]["document__nom_fichier"].split(', ')[0])
                file = open(archive[0]["document__nom_fichier"].split(', ')[0],'wb')
                file.write(archive[0]['document__contenu'])
                shutil.copy(archive[0]['document__nom_fichier'].split(', ')[0],destination_file)
                file = file.close()
                os.remove(archive[0]['document__nom_fichier'].split(', ')[0])
            return JsonResponse({'succes': 'Le telechargement est un succès'})

    def get(self, request):
        archives = Archivage.objects.all().values(
            'id',
            'document__nom_fichier',
            'document__poste_comptable__nom_poste', 
            'document__piece__nom_piece',
            'document__date_arrivee',
            'document__exercice',
            'document__mois',
            'document__created_at',
            'document__type'
        )
        return JsonResponse(list(archives), safe=False)

        # Cas 1 : Auditeur → ses propres archives
        # if utilisateur_id:
        #     archives = Archivage.objects.filter(
        #         document__poste_comptable__utilisateur__id=utilisateur_id
        #     ).select_related("document")

        # Cas 2 : Chef d’unité → archives de son unité
        # elif unite_id:
        #     archives = Archivage.objects.filter(
        #         document__poste_comptable__zone__nom_zone=unite_id
        #     ).select_related("document")

        # # Cas 3 : Directeur → toutes les archives
        # else:
        #     archives = Archivage.objects.all().select_related("document")

        # data = [
        #     {
        #         "id": a.document.id,
        #         "nom_fichier": a.document.nom_fichier,
        #         "type": a.document.type,
        #         "date_arrivee": a.document.date_arrivee,
        #         "exercice": a.document.exercice,
        #         "mois": a.document.mois,
        #         "piece": a.document.piece.nom_piece if a.document.piece else "",
        #         "poste_comptable": a.document.poste_comptable.nom_poste if a.document.poste_comptable else "",
        #     }
        #     for a in archives
        # ]

        # return JsonResponse(data, safe=False)


class PieceComptableView(APIView):

    def get(self,request) :

        piece = Piece.objects.all().values("id","nom_piece")      
        return JsonResponse(list(piece),safe = False)
  

class DocumentView(APIView): 
    def post(self,request):
        

        # if request.data.get('action') == 'ajouter':
        #     poste_comptable = request.data.get("poste_comptable")
        #     fichier = request.FILES.get('fichier')
        #     document = Document(
        #         date_arrivee = request.data.get('date_arrivee'),
        #         contenu = fichier.read(),
        #         nom_fichier = request.data.get('nom_fichier'),
        #         type = request.data.get('type_fichier'),
        #         exercice = request.data.get('exercice'),
        #         mois = request.data.get('mois'),
        #         piece_id = request.data.get('piece'),
        #         poste_comptable = Poste_comptable.objects.get(nom_poste=poste_comptable),
        #     )
        #     document.save()
        #     return JsonResponse({'succes': 'Document enregistré avec succès'})

        # elif request.data.get('action') == 'listes_documents_auditeur':
        #     document = Document.objects.select_related('piece', 'poste_comptable').filter(poste_comptable__utilisateur_id=request.data.get('utilisateur'), archives__isnull=True).values(
        #         'id',
        #         'nom_fichier',
        #         'poste_comptable__nom_poste', 
        #         'piece__nom_piece',
        #         'date_arrivee',
        #         'exercice',
        #         'mois',
        #         'created_at',
        #         'type')
        #     return JsonResponse(list(document), safe=False)

        # elif request.data.get('action') == 'listes_documents_chef_unite':
        #     document = Document.objects.all().select_related('poste_comptable', 'piece').filter(poste_comptable__utilisateur__zone__nom_zone=request.data.get('zone'), archives__isnull=True).values('id', 'piece__nom_piece','poste_comptable__nom_poste', 'nom_fichier', 'exercice', 'mois', 'date_arrivee')
        #     return JsonResponse(list(document), safe=False)

        # elif request.data.get('action') == 'listes_documents_directeur':
        #     document = Document.objects.filter(archives__isnull=True).values('id', 'piece__nom_piece', 'poste_comptable__nom_poste', 'nom_fichier', 'exercice', 'mois', 'date_arrivee', 'created_at')
        #     return JsonResponse(list(document), safe=False)

        if request.data.get("action") == 'ajouter':

            contenu = request.FILES.get("fichier")
            Poste_comptable_nom = request.data.get("poste_comptable")
            piece_nom = request.data.get("piece")
            exercice = request.data.get("exercice")
            mois = request.data.get("mois")
            info_supp_nouveau = request.data.get("info_supp")

            #recuperation de la piece et du poste comptable
            poste_comptable = Poste_comptable.objects.get(nom_poste=Poste_comptable_nom)
            piece = Piece.objects.get(pk=piece_nom)

            #chercher la dernier version du  document existant avec le même info_supp
            documents_existants = Document.objects.filter(
                piece=piece,
                exercice=exercice,
                mois=mois,
            )
            #Extraire les documents avec le même info_supp
            documents_meme_info = [
                doc for doc in documents_existants
                if len(doc.nom_fichier.split(", ")) > 1 and doc.nom_fichier.split(", ")[1] == info_supp_nouveau
            ]

            if documents_meme_info:
                #recupérer la version max
                version = max(doc.version for doc in documents_meme_info)+1
            else:
                version = 1

            #Créer le nouveau document avec la version correcte
            document = Document(
                nom_fichier=f"{request.data.get('nom_fichier')}, {info_supp_nouveau}",
                type=request.data.get("type_fichier"),
                contenu=contenu.read(),
                date_arrivee=request.data.get("date_arrivee"),
                poste_comptable=poste_comptable,
                piece=piece,
                exercice=exercice,
                mois=mois,
                version=version
            )
            document.save()
            # return JsonResponse({"id_fichier": document.id,"version":document.version})
            return JsonResponse({'succes': 'Document enregistré avec succès'})

        elif request.data.get('action') == 'listes_documents_auditeur':

            # Récupérer tous les documents de l'utilisateur (même archivés)
            document_qs = Document.objects.filter(
                poste_comptable__utilisateur_id=request.data.get('utilisateur')
            ).select_related('poste_comptable', 'piece')

            # Construire un dictionnaire pour stocker la dernière version par document logique
            latest_docs = {}
            for doc in document_qs:
                # Extraire info_supp après la virgule
                parts = doc.nom_fichier.split(', ')
                info_supp = parts[1] if len(parts) > 1 else ''

                key = (doc.piece.id, doc.exercice, doc.mois, info_supp)

                # Garder le document avec la version maximale
                if key not in latest_docs or doc.version > latest_docs[key].version:
                    latest_docs[key] = doc

            # Préparer le résultat JSON en excluant les documents dont la dernière version est archivée
            result = []
            for doc in latest_docs.values():

                # ⚠️ Si la dernière version est archivée → on ignore complètement ce document
                if hasattr(doc, 'archives'):
                    continue

                result.append({
                    'id': doc.id,
                    'piece__nom_piece': doc.piece.nom_piece,
                    'poste_comptable__nom_poste': doc.poste_comptable.nom_poste,
                    'nom_fichier': doc.nom_fichier,
                    'exercice': doc.exercice,
                    'mois': doc.mois,
                    'date_arrivee': doc.date_arrivee,
                    'created_at': doc.created_at,
                    'version': doc.version
                })

            return JsonResponse(result, safe=False)

        
        elif request.data.get('action') == 'listes_documents_chef_unite':

            # Récupérer tous les documents de la zone (archivés ou non)
            document_qs = Document.objects.filter(
                poste_comptable__utilisateur__zone__nom_zone=request.data.get('zone')
            ).select_related('poste_comptable', 'piece')

            # Construire un dictionnaire pour stocker la dernière version par document logique
            latest_docs = {}
            for doc in document_qs:

                # Extraire info_supp après la virgule
                parts = doc.nom_fichier.split(', ')
                info_supp = parts[1] if len(parts) > 1 else ''

                key = (doc.piece.id, doc.exercice, doc.mois, info_supp)

                # Garder uniquement la version la plus élevée
                if key not in latest_docs or doc.version > latest_docs[key].version:
                    latest_docs[key] = doc

            # Préparer le résultat JSON en excluant les documents archivés
            result = []
            for doc in latest_docs.values():

                # ⚠️ Si la dernière version est archivée → on ignore
                if hasattr(doc, 'archives'):
                    continue

                result.append({
                    'id': doc.id,
                    'piece__nom_piece': doc.piece.nom_piece,
                    'poste_comptable__nom_poste': doc.poste_comptable.nom_poste,
                    'nom_fichier': doc.nom_fichier,
                    'exercice': doc.exercice,
                    'mois': doc.mois,
                    'date_arrivee': doc.date_arrivee,
                    'created_at': doc.created_at,
                    'version': doc.version
                })

            return JsonResponse(result, safe=False)


        elif request.data.get('action') == 'listes_documents_directeur':

            # Récupérer tous les documents (avec relations)
            document_qs = Document.objects.all().select_related('poste_comptable', 'piece')

            # Dictionnaire pour stocker la dernière version
            latest_docs = {}

            for doc in document_qs:
                # Extraire info_supp après la virgule
                parts = doc.nom_fichier.split(', ')
                info_supp = parts[1] if len(parts) > 1 else ''

                # Clé logique d’un document
                key = (doc.piece.id, doc.exercice, doc.mois, info_supp)

                # On garde le document avec la version la plus élevée
                if key not in latest_docs or doc.version > latest_docs[key].version:
                    latest_docs[key] = doc

            # Préparer le résultat JSON SANS les documents archivés
            result = []
            for doc in latest_docs.values():

                # ⚠️ Si la dernière version est archivée → on ignore
                if hasattr(doc, 'archives'):
                    continue

                result.append({
                    'id': doc.id,
                    'piece__nom_piece': doc.piece.nom_piece,
                    'poste_comptable__nom_poste': doc.poste_comptable.nom_poste,
                    'nom_fichier': doc.nom_fichier,
                    'exercice': doc.exercice,
                    'mois': doc.mois,
                    'date_arrivee': doc.date_arrivee,
                    'created_at': doc.created_at,
                    'version': doc.version
                })

            return JsonResponse(result, safe=False)

        
        elif request.data.get('action') == 'telecharger':
            import io
            import zipfile
            
            
            ids = request.data.get('id_docs').split(",")

            if not ids:
                return JsonResponse({"error": "Aucun fichier sélectionné"}, status=400)

            # Buffer mémoire pour créer le ZIP
            zip_buffer = io.BytesIO()

            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for id in ids:
                    doc = Document.objects.filter(pk=id).values('contenu', 'nom_fichier').first()
                    if doc:
                        zipf.writestr(doc['nom_fichier'].split(', ')[0], doc['contenu'])

            zip_buffer.seek(0)

            # Envoyer le ZIP au navigateur → téléchargé dans "Downloads"
            response = HttpResponse(zip_buffer, content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="documents.zip"'

            return response

        elif request.data.get('action') == 'recuperer_documents_a_comparer':
            # Préparer un dictionnaire de filtres dynamiques
            filters = {}

            # Ajouter uniquement les champs réellement présents et non vides
            if request.data.get('poste_comptable'):
                filters['poste_comptable__nom_poste'] = request.data.get('poste_comptable')

            if request.data.get('piece'):
                filters['piece__nom_piece'] = request.data.get('piece')

            if request.data.get('date_arrivee'):
                filters['date_arrivee'] = request.data.get('date_arrivee')

            if request.data.get('mois'):
                filters['mois'] = request.data.get('mois')

            if request.data.get('exercice'):
                filters['exercice'] = request.data.get('exercice')

            # Appliquer uniquement les filtres existants
            document_qs = Document.objects.filter(**filters).select_related('poste_comptable', 'piece')

            # Construire un dictionnaire pour stocker la dernière version par document logique
            latest_docs = {}
            for doc in document_qs:
                parts = doc.nom_fichier.split(', ')
                info_supp = parts[1] if len(parts) > 1 else ''

                key = (doc.piece.id, doc.exercice, doc.mois, info_supp)

                # Garder le document avec la version max
                if key not in latest_docs or doc.version > latest_docs[key].version:
                    latest_docs[key] = doc

            # Préparer le résultat JSON
            result = []
            for doc in latest_docs.values():
                result.append({
                    'id': doc.id,
                    'piece__nom_piece': doc.piece.nom_piece,
                    'poste_comptable__nom_poste': doc.poste_comptable.nom_poste,
                    'nom_fichier': doc.nom_fichier,
                    'exercice': doc.exercice,
                    'mois': doc.mois,
                    'date_arrivee': doc.date_arrivee,
                    'version': doc.version
                })

            return JsonResponse(result, safe=False)


   
 

        


        
   

    




=======
from django.shortcuts import render

# Create your views here.
>>>>>>> data
