"""
Clases de paginación personalizadas
"""
from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """
    Paginación personalizada que permite al cliente especificar el tamaño de página
    """
    page_size = 20  # Tamaño por defecto
    page_size_query_param = 'page_size'  # Permite ?page_size=10
    max_page_size = 100  # Máximo permitido para evitar sobrecarga
