# from rest_framework import viewSets
from rest_framework.response import Response
from rest_framework import status
from users.models import Poste_comptable
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.core.mail import EmailMessage
from calendar import monthrange 
import os.path
import shutil
from datetime import date, datetime
from rest_framework.views import APIView
from .models import Poste_comptable, Document, Piece, Archivage, Exercice
import os
import io
import zipfile
import hashlib
from fpdf import FPDF



# Hash du fichier local
def hash_local_file(file):
    hash_func = hashlib.sha256()
    for chunk in file.chunks():
        hash_func.update(chunk)
    return hash_func.hexdigest()

# Hash d'un contenu binaire
def hash_binary(binary):
    return hashlib.sha256(binary).hexdigest()


# Génération du PDF en mémoire et retour en bytes
def generate_diff_pdf_bytes(local_file_name, local_content, doc_name, doc_content_bytes):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Rapport de Vérification de Fichiers", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    # Fichier local
    local_size_mb = len(local_content) / (1024 * 1024)
    pdf.cell(0, 10, f"Fichier local : {local_file_name}", ln=True)
    pdf.cell(0, 10, f"Format : {local_file_name.split('.')[-1].upper() or 'Inconnu'}", ln=True)
    pdf.cell(0, 10, f"Taille : {local_size_mb:.4f} Mo", ln=True)
    pdf.cell(0, 10, f"Hash SHA-256 : {hashlib.sha256(local_content).hexdigest()}", ln=True)
    
    pdf.ln(5)
    # Fichier en base
    doc_size_mb = len(doc_content_bytes) / (1024 * 1024)
    pdf.cell(0, 10, f"Fichier en base : {doc_name}", ln=True)
    pdf.cell(0, 10, f"Format : {doc_name.split('.')[-1].split(',')[0].upper() or 'Inconnu'}", ln=True)
    pdf.cell(0, 10, f"Taille : {doc_size_mb:.4f} Mo", ln=True)
    pdf.cell(0, 10, f"Hash SHA-256 : {hashlib.sha256(doc_content_bytes).hexdigest()}", ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.multi_cell(0, 10, "Conclusion : Les fichiers sont différents.")
    
    return pdf.output(dest='S').encode('latin1')


class VerificationView(APIView):
    def post(self, request):
        if "local_file" not in request.FILES:
            return Response({"error": "Aucun fichier reçu."}, status=status.HTTP_400_BAD_REQUEST)
        local_file = request.FILES["local_file"]
        local_hash = hash_local_file(local_file)
        local_file.seek(0)
        local_content = local_file.read()
        # Vérifier id_doc
        id_doc = request.POST.get("id_doc")
        if not id_doc:
            return Response({"error": "Aucun id_doc envoyé."}, status=status.HTTP_400_BAD_REQUEST)
        # Récupérer le document en base
        try:
            document = Document.objects.get(id=id_doc)
        except Document.DoesNotExist:
            return Response({"error": "Document introuvable."}, status=status.HTTP_404_NOT_FOUND)
        if not document.contenu:
            return Response({"identique": False, "message": "Le document sélectionné n'a pas de contenu enregistré."})
        # BinaryField → bytes
        doc_content_bytes = document.contenu.tobytes()
        doc_hash = hash_binary(doc_content_bytes)
        # Si identiques
        if doc_hash == local_hash:
            return Response({
                "identique": True,
                "document": document.nom_fichier,
                "message": "Le document local est IDENTIQUE au document sélectionné."
            })
        # Sinon générer PDF en mémoire
        pdf_bytes = generate_diff_pdf_bytes(local_file.name, local_content, document.nom_fichier, doc_content_bytes)
        pdf_base64 = pdf_bytes.hex()  # Encode en hex pour l’envoyer dans JSON
        return Response({
            "identique": False,
            "document": document.nom_fichier,
            "message": "Les fichiers sont différents.",
            "pdf_bytes_hex": pdf_base64  # React pourra décoder et déclencher le téléchargement
        })


class PiecesStatusView(APIView):
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
            # Conserve la dernière version par document logique
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

            # Période Décadaire
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

            # Période Journalière
            # elif periode == "journalière" and mois and exercice:
            #     mois_int = int(mois)
            #     exercice_int = int(exercice)
            #     nb_jours = monthrange(exercice_int, mois_int)[1]
            #     # Filtrage des docs journaliers (dernière version déjà appliquée)
            #     docs_sje = documents
            #     for jour in range(1, nb_jours + 1):
            #         date_jour = date(exercice_int, mois_int, jour)
            #         date_str = date_jour.strftime("%Y-%m-%d")
            #         arrived = False
            #         documents_for_day = []
            #         for doc in docs_sje:
            #             parts = [p.strip() for p in doc.nom_fichier.split(",") if p.strip()]
            #             if len(parts) > 1 and parts[1] == date_str:
            #                 arrived = True
            #                 try:
            #                     date_sje = datetime.strptime(parts[1], "%Y-%m-%d").date()
            #                 except ValueError:
            #                     date_sje = date_jour

            #                 retard = doc.date_arrivee and doc.date_arrivee > date_sje
            #                 documents_for_day.append({
            #                     "id": doc.id,
            #                     "nom_fichier": doc.nom_fichier,
            #                     "date_arrivee": doc.date_arrivee.strftime("%Y-%m-%d") if doc.date_arrivee else None,
            #                     "retard": retard
            #                 })
            #         resultats.append({
            #             "id": piece.id,
            #             "nom_piece": f"{piece.nom_piece} ({date_str})",
            #             "periode": piece.periode,
            #             "date": date_str,
            #             "arrived": [arrived],
            #             "late": [any(doc['retard'] for doc in documents_for_day)],
            #             "documents": [documents_for_day]
            #         })

            elif periode == "journalière" and mois and exercice:
                mois_int = int(mois)
                exercice_int = int(exercice)
                nb_jours = monthrange(exercice_int, mois_int)[1]

                docs_sje = documents

                for jour in range(1, nb_jours + 1):
                    date_jour = date(exercice_int, mois_int, jour)

                    # ⛔ Ignorer samedi (5) et dimanche (6)
                    if date_jour.weekday() >= 5:
                        continue

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
                        "arrived": arrived,
                        "late": any(doc["retard"] for doc in documents_for_day),
                        "documents": documents_for_day
                    })

            # Période Mensuelle
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

        if request.data.get('action') == 'listes_documents_auditeur':
            document = Document.objects.select_related('piece', 'poste_comptable').filter(poste_comptable__utilisateur_id=request.data.get('utilisateur'), archives__isnull=True).values(
                'id',
                'nom_fichier',
                'poste_comptable__nom_poste', 
                'piece__nom_piece',
                'date_arrivee',
                'exercice',
                'mois',
                'created_at',
                'type',
                'version'
            )
            return JsonResponse(list(document), safe=False)

        elif request.data.get('action') == 'listes_documents_chef_unite':
            document = Document.objects.all().select_related('poste_comptable', 'piece').filter(poste_comptable__utilisateur__zone__nom_zone=request.data.get('zone'), archives__isnull=True).values('id', 'piece__nom_piece','poste_comptable__nom_poste', 'nom_fichier', 'exercice', 'mois', 'date_arrivee')
            return JsonResponse(list(document), safe=False)

        elif request.data.get('action') == 'listes_documents_directeur':
            document = Document.objects.filter(archives__isnull=True).values('id', 'piece__nom_piece', 'poste_comptable__nom_poste', 'nom_fichier', 'exercice', 'mois', 'date_arrivee', 'created_at')
            return JsonResponse(list(document), safe=False)

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
                #recupérer la version maximaleS
                version = max(doc.version for doc in documents_meme_info)+1
            else:
                version = 1

            #Créer le dpcument
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
           
            return JsonResponse({'succes': 'Document enregistré avec succès'})

        
        elif request.data.get('action') == 'telecharger':
            
            ids = request.data.get('id_docs').split(",")

            if not ids:
                return JsonResponse({"error": "Aucun fichier sélectionné"}, status=400)

            # Créer le fichier zip en mémoire
            zip_buffer = io.BytesIO()

            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for id in ids:
                    doc = Document.objects.filter(pk=id).values('contenu', 'nom_fichier').first()
                    if doc:
                        zipf.writestr(doc['nom_fichier'].split(', ')[0], doc['contenu'])

            zip_buffer.seek(0)

            # Envoyer les documents vers React dans un fichier zip
            response = HttpResponse(zip_buffer, content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="documents.zip"'

            return response



        elif request.data.get('action') == 'envoyer_documents':
            sujet = request.data.get('sujet')
            message = request.data.get('message')
            email_destinataire = request.data.get('email')
            document = request.FILES.get('fichier')

            try:
                email = EmailMessage(
                    subject=sujet,
                    body=message,
                    from_email=None,  # utilise EMAIL_HOST_USER si configuré
                    to=[email_destinataire],
                )

                # 🔹 Ajout de la pièce jointe
                if document:
                    email.attach(
                        document.name,
                        document.read(),
                        document.content_type
                    )

                email.send(fail_silently=False)

                return JsonResponse({'succes': 'Document envoyé avec succès'})

            except Exception as e:
                return JsonResponse({'error': str(e)})

                

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


class ExerciceView(APIView):

    def get(self, request):
        exercices = Exercice.objects.all().values('id', 'annee').order_by('-id')
        return JsonResponse(list(exercices), safe=False) 

        


        
   

    






