from django.urls import path
from . import views
# from .views import (
#     PhaseListCreateAPIView,
#     PhaseRetrieveUpdateDeleteAPIView,
#     ProcedureListCreateAPIView,
#     ProcedureRetrieveUpdateDeleteAPIView
# )



urlpatterns = [
    path('get', views.AuditLogView.as_view(),
    name='get_audit_log'),

    # Phases
    path('phases', views.PhaseListCreateAPIView.as_view(), name='phase-list-create'),
    path('phases/<int:pk>', views.PhaseRetrieveUpdateDeleteAPIView.as_view(), name='phase-rud'),

    # Procedures
    path('procedures', views.ProcedureListCreateAPIView.as_view(), name='procedure-list-create'),
    path('procedures/<int:pk>', views.ProcedureRetrieveUpdateDeleteAPIView.as_view(), name='procedure-rud'),
]
