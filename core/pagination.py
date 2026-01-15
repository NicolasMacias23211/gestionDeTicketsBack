"""
Clases de paginación personalizadas
"""
from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """
    Paginación estándar que permite al cliente especificar el tamaño de página
    """
    page_size = 10
    page_size_query_param = 'page_size'  
    max_page_size = 100 
