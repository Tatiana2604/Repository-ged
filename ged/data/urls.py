from django.urls import path
from . import views

urlpatterns = [

    path('exercice/get', views.ExerciceView.as_view(), name='liste_exercices'),
    
    path('piece_comptable/get', views.PieceComptableView.as_view(), name='piece_comptable_get'),
    path("pieces/status", views.PiecesStatusView.as_view(), name="pieces_status"),

    path('document/create', views.DocumentView.as_view(), name='insertion_document'),
    path('document/liste', views.DocumentView.as_view(), name='liste_document'),
    path('document/telecharger', views.DocumentView.as_view(), name='telecharger_documents'),
    path('document/send', views.DocumentView.as_view(), name='envoyer_documents'),
    path('document/comparaison', views.DocumentView.as_view(), name='afficher_les_documents_a_comparer'),
    path('verification', views.VerificationView.as_view(), name='comparer_des_documents'),
    # path('document/archiver', views.DocumentView.as_view(), name='archiver_document'),
    path('archives', views.ArchiveView.as_view(), name='archives'),
    path('archive/list', views.ArchiveView.as_view(), name='liste_archives'),
    path('archive/telecharger', views.ArchiveView.as_view(), name='telecharger_documents_archives'),
    

]
