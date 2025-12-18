from rest_framework import status
from rest_framework.response import Response


class CustomDeleteMixin:
    """
    Mixin que sobrescribe el comportamiento por defecto de DELETE
    para retornar 200 OK con un mensaje en lugar de 204 No Content
    """
    
    def destroy(self, request, *args, **kwargs):
        """
        Elimina el objeto y retorna una respuesta personalizada
        """
        instance = self.get_object()
        
        model_name = instance.__class__.__name__
        object_info = self.get_object_info(instance)
        
        self.perform_destroy(instance)
        
        return Response({
            'success': True,
            'message': f'{model_name} eliminado exitosamente',
            'deleted_object': object_info
        }, status=status.HTTP_200_OK)
    
    def get_object_info(self, instance):
        """
        Obtiene información básica del objeto a eliminar.
        Puede ser sobrescrito en los ViewSets individuales para personalizar.
        """
        info = {}
        
        if hasattr(instance, 'pk'):
            info['id'] = instance.pk
        
        name_fields = ['name', 'title', 'network_user', 'client_name', 
                      'service_name', 'rol_name', 'priority_name', 
                      'program_name', 'sub_program_name', 'closing_code_name',
                      'ans_name', 'status_name', 'ticket_title']
        
        for field in name_fields:
            if hasattr(instance, field):
                info['name'] = getattr(instance, field)
                break
        
        return info
