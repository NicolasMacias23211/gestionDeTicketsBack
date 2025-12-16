import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware para registrar todas las peticiones HTTP
    """
    def process_request(self, request):
        logger.info(
            f"Request: {request.method} {request.path} "
            f"from {request.META.get('REMOTE_ADDR')} "
            f"User: {request.user if request.user.is_authenticated else 'Anonymous'}"
        )
        return None

    def process_response(self, request, response):
        logger.info(
            f"Response: {request.method} {request.path} "
            f"Status: {response.status_code}"
        )
        return response


class ExceptionLoggingMiddleware(MiddlewareMixin):
    """
    Middleware para registrar excepciones
    """
    def process_exception(self, request, exception):
        logger.error(
            f"Exception in {request.method} {request.path}: {str(exception)}",
            exc_info=True,
            extra={
                'request': request,
                'user': request.user if request.user.is_authenticated else 'Anonymous'
            }
        )
        return None


class HealthCheckMiddleware(MiddlewareMixin):
    """
    Middleware para health check (útil para balanceadores de carga)
    """
    def process_request(self, request):
        if request.path == '/health/':
            return JsonResponse({'status': 'ok', 'service': 'e-seus-api'})
        return None


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware para agregar headers de seguridad adicionales
    """
    def process_response(self, request, response):
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response
