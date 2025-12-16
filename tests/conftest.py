"""
Configuración de tests para pytest-django
"""
import pytest
from django.conf import settings


@pytest.fixture(scope='session')
def django_db_setup():
    """
    Configuración de base de datos para tests
    """
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }


@pytest.fixture
def api_client():
    """
    Cliente de API para tests
    """
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, django_user_model):
    """
    Cliente autenticado para tests
    """
    user = django_user_model.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_client(api_client, django_user_model):
    """
    Cliente con usuario administrador para tests
    """
    admin = django_user_model.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123'
    )
    api_client.force_authenticate(user=admin)
    return api_client
