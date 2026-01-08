from rest_framework import permissions
from .models import EUser


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado que permite lectura a todos los usuarios autenticados
    pero solo escritura a los administradores
    Verifica tanto is_staff de Django como el rol 'administrador' en EUser.
    """
    def has_permission(self, request, view):
        # Los métodos seguros (GET, HEAD, OPTIONS) están permitidos para todos
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Para métodos de escritura, verificar si es staff o tiene rol administrador
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Si es staff en Django, permitir
        if request.user.is_staff:
            return True
        
        # Verificar si tiene rol "administrador" en EUser
        try:
            euser = EUser.objects.get(network_user=request.user.username)
            return euser.rol_name and euser.rol_name.rol_name.strip().lower() == 'administrador'
        except EUser.DoesNotExist:
            return False


class IsTicketOwnerOrAssigned(permissions.BasePermission):
    """
    Permiso que permite acceso al creador del ticket o a quien está asignado
    """
    def has_object_permission(self, request, view, obj):
        # Los administradores tienen acceso completo
        if request.user.is_staff:
            return True
        
        # El creador del ticket o el asignado pueden ver y editar
        return (
            obj.reporter_user.network_user == request.user.username or
            obj.assigned_to == request.user.username
        )


class IsNoteOwnerOrStaff(permissions.BasePermission):
    """
    Permiso para notas: el staff puede todo, los usuarios solo ven notas públicas
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Los administradores tienen acceso completo
        if request.user.is_staff:
            return True
        
        # Los usuarios normales solo pueden ver notas visibles para el cliente
        if request.method in permissions.SAFE_METHODS:
            return obj.visible_to_client
        
        return False


class CanManageTickets(permissions.BasePermission):
    """
    Permiso para gestionar tickets (asignar, cerrar, etc.)
    """
    def has_permission(self, request, view):
        return request.user and (request.user.is_staff or request.user.is_superuser)


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permiso que permite edición solo al dueño del objeto
    """
    def has_object_permission(self, request, view, obj):
        # Lectura permitida para todos
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Escritura solo para el dueño o staff
        if request.user.is_staff:
            return True
        
        # Verifica si el objeto tiene un campo que relaciona con el usuario
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'network_user'):
            return obj.network_user == request.user.username
        
        return False
