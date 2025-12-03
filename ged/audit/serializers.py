from rest_framework import serializers
from audit.models import AuditLog, Phase, Procedure

class AuditLogSerializer(serializers.ModelSerializer):

    utilisateur = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "utilisateur",
            "action",
            "modele",
            "object_id",
            "ancienne_valeur",
            "nouvelle_valeur",
            "date_action",
            "adresse_ip"
        ]
           
           
    def get_utilisateur(self,obj):
        
        if obj.utilisateur and obj.utilisateur.utilisateur:
            prenom = obj.utilisateur.utilisateur.prenom or ""
            nom = obj.utilisateur.utilisateur.nom or ""
            return f"{nom} {prenom}".strip()
        return "-"


class PhaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phase
        fields = ['id', 'nom_phase']

# class ProcedureSerializer(serializers.ModelSerializer):
#     phase = PhaseSerializer(read_only=True)
#     phase_id = serializers.PrimaryKeyRelatedField(
#         queryset=Phase.objects.all(), source='phase', write_only=True
#     )

#     class Meta:
#         model = Procedure
#         fields = ['id', 'phase', 'procedure','phase_id', 'numero_orde', 'document_procedure', 'document_travail_valide']

class ProcedureSerializer(serializers.ModelSerializer):
    nom_phase = serializers.CharField(source='phase.nom_phase', read_only=True)

    # pour envoyer la valeur au backend
    phase_id = serializers.PrimaryKeyRelatedField(
        queryset=Phase.objects.all(),
        source='phase'
    )

    # pour afficher l’ID dans le GET
    phase = serializers.IntegerField(source='phase.id', read_only=True)

    class Meta:
        model = Procedure
        fields = [
            'id',
            'nom_phase',
            'procedure',
            'phase_id',   # utilisé en POST
            'phase',      # visible en GET
            'numero_orde',
            'document_procedure',
            'document_travail_valide',
        ]

    def create(self, validated_data):
        # Récupération des fichiers
        doc_proc = self.context['request'].FILES.get('document_procedure')
        doc_travail = self.context['request'].FILES.get('document_travail_valide')

        # Conversion fichier → bytes
        if doc_proc:
            validated_data['document_procedure'] = doc_proc.read()

        if doc_travail:
            validated_data['document_travail_valide'] = doc_travail.read()

        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Récupération des fichiers
        doc_proc = self.context['request'].FILES.get('document_procedure')
        doc_travail = self.context['request'].FILES.get('document_travail_valide')

        # Conversion fichier → bytes
        if doc_proc:
            validated_data['document_procedure'] = doc_proc.read()

        if doc_travail:
            validated_data['document_travail_valide'] = doc_travail.read()

        return super().update(instance, validated_data)

