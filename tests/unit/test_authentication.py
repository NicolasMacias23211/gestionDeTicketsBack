"""
Tests de ejemplo para las vistas de autenticación
"""
import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestAuthenticationViews:
    """
    Tests para las vistas de autenticación
    """
    
    def test_user_registration(self, api_client):
        """
        Test de registro de usuario
        """
        url = reverse('authentication:register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'tokens' in response.data
        assert 'user' in response.data
        assert response.data['user']['username'] == 'newuser'
    
    def test_user_login(self, api_client, django_user_model):
        """
        Test de login de usuario
        """
        # Crear usuario
        user = django_user_model.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        url = reverse('authentication:token_obtain_pair')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
    
    def test_user_profile(self, authenticated_client):
        """
        Test de obtención de perfil de usuario
        """
        url = reverse('authentication:profile')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == 'testuser'
