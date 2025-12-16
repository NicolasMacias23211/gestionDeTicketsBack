from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    LDAPAuthView,
    LogoutView,
    UserProfileView
)

app_name = 'authentication'

urlpatterns = [
    # JWT Authentication basada en LDAP
    path('login/', LDAPAuthView.as_view(), name='ldap_auth'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # User Profile (solo consulta, datos vienen de LDAP)
    path('profile/', UserProfileView.as_view(), name='profile'),
]
