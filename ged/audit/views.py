from django.shortcuts import get_object_or_404
# from rest_framework.permissions import isAuthenticated
from audit.models import AuditLog
from audit.serializers import AuditLogSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Phase, Procedure
from .serializers import PhaseSerializer, ProcedureSerializer
from django.http import HttpResponse, Http404


# Create your views here.

class AuditLogView(APIView):

    def get(self, request):

        audit_logs = AuditLog.objects.all().order_by('-date_action')
        
        serializer = AuditLogSerializer(audit_logs, many=True)

        return Response(serializer.data)



# === PHASES ===
class PhaseListCreateAPIView(APIView):
    def get(self, request):
        phases = Phase.objects.all()
        serializer = PhaseSerializer(phases, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PhaseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PhaseRetrieveUpdateDeleteAPIView(APIView):
    def get_object(self, pk):
        try:
            return Phase.objects.get(pk=pk)
        except Phase.DoesNotExist:
            return None

    def get(self, request, pk):
        phase = self.get_object(pk)
        if not phase:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = PhaseSerializer(phase)
        return Response(serializer.data)

    def put(self, request, pk):
        phase = self.get_object(pk)
        if not phase:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = PhaseSerializer(phase, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        phase = self.get_object(pk)
        if not phase:
            return Response(status=status.HTTP_404_NOT_FOUND)
        phase.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# === PROCEDURES ===
class ProcedureListCreateAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        procedures = Procedure.objects.all().order_by('numero_orde')
        serializer = ProcedureSerializer(procedures, many=True)
        return Response(serializer.data)

    def post(self, request):
        # serializer = ProcedureSerializer(data=request.data)
        serializer = ProcedureSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            # return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({"succes": "Ajout d'une procedure efectuée avec succès"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProcedureRetrieveUpdateDeleteAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self, pk):
        try:
            return Procedure.objects.get(pk=pk)
        except Procedure.DoesNotExist:
            return None

    def get(self, request, pk):
        procedure = self.get_object(pk)
        if not procedure:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ProcedureSerializer(procedure)
        return Response(serializer.data)

    def put(self, request, pk):
        procedure = self.get_object(pk)
        if not procedure:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = ProcedureSerializer(
            procedure,
            data=request.data,
            context={'request': request}   # 🔥 Très important !
        )

        if serializer.is_valid():
            serializer.save()
            return Response({"succes": "Modification d'une procedure effectuée avec succès"})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        procedure = self.get_object(pk)
        if not procedure:
            return Response(status=status.HTTP_404_NOT_FOUND)
        procedure.delete()
        # return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"succes": "Suppression d'une procedure effectuée avec succès"})
    

class DownloadDocumentTravailValide(APIView):

    def get(self, request, pk):
        procedure = get_object_or_404(Procedure, id=pk)

        if not procedure.document_travail_valide:
            raise Http404("Aucun document disponible")

        response = HttpResponse(
            procedure.document_travail_valide,
            content_type="application/octet-stream"
        )

        response["Content-Disposition"] = (
            f'attachment; filename="document_travail_procedure_{pk}.pdf"'
        )

        return response
    
class DownloadDocumentProcedure(APIView):

    def get(self, request, pk):
        procedure = get_object_or_404(Procedure, id=pk)

        if not procedure.document_procedure:
            raise Http404("Aucun document disponible")

        response = HttpResponse(
            procedure.document_procedure,
            content_type="application/octet-stream"
        )

        response["Content-Disposition"] = (
            f'attachment; filename="document_travail_procedure_{pk}.pdf"'
        )

        return response

