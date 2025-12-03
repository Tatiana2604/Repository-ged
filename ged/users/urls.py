from django.urls import path
from . import views

urlpatterns = [
    path('login', views.LoginView.as_view(),name="api-login"),
    path('logout', views.LogoutView.as_view(),name='api-logout'),
    path('get_user', views.UserView.as_view(),name="api-csrf"),    
    path('csrf', views.GetCSRFToken.as_view(),name="api-csrf"),
    path('get_auditeurs_zone', views.UserView.as_view(), name='recuper_auditeurs_zone'),
    path('get_auditeurs', views.UserView.as_view(), name='recuper_auditeurs'),

    path('zone/get', views.ZoneView.as_view(), name='recuper_tous_les_zones'),
    
    path('poste_comptable/all', views.PosteComptableView.as_view(), name='liste-des-postes-comptables'),
    path('poste_comptable/get', views.PosteComptableView.as_view(), name='poste_comptable_get'),
]
