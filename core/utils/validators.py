"""
Validadores personalizados para el proyecto
"""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re


def validate_phone_number(value: str):
    """
    Valida que un número de teléfono tenga un formato válido
    """
    # Eliminar caracteres no numéricos
    phone = re.sub(r'\D', '', value)
    
    # Validar longitud (10 dígitos para México)
    if len(phone) < 10 or len(phone) > 15:
        raise ValidationError(
            _('El número de teléfono debe tener entre 10 y 15 dígitos.'),
            code='invalid_phone'
        )
    
    return value


def validate_network_user(value: str):
    """
    Valida el formato de usuario de red (username corporativo)
    """
    # Solo letras, números, puntos y guiones bajos
    pattern = r'^[a-zA-Z0-9._-]+$'
    
    if not re.match(pattern, value):
        raise ValidationError(
            _('El usuario de red solo puede contener letras, números, puntos, guiones y guiones bajos.'),
            code='invalid_network_user'
        )
    
    if len(value) < 3:
        raise ValidationError(
            _('El usuario de red debe tener al menos 3 caracteres.'),
            code='network_user_too_short'
        )
    
    return value


def validate_file_extension(value):
    """
    Valida la extensión de archivos adjuntos
    """
    import os
    
    allowed_extensions = [
        '.pdf', '.doc', '.docx', '.xls', '.xlsx',
        '.jpg', '.jpeg', '.png', '.gif',
        '.txt', '.csv', '.zip', '.rar'
    ]
    
    ext = os.path.splitext(value.name)[1].lower()
    
    if ext not in allowed_extensions:
        raise ValidationError(
            _(f'Extensión de archivo no permitida. Permitidas: {", ".join(allowed_extensions)}'),
            code='invalid_extension'
        )
    
    return value


def validate_file_size(value):
    """
    Valida el tamaño de archivos adjuntos (máximo 10MB)
    """
    max_size = 10 * 1024 * 1024  # 10 MB
    
    if value.size > max_size:
        raise ValidationError(
            _('El archivo es demasiado grande. El tamaño máximo es 10MB.'),
            code='file_too_large'
        )
    
    return value


def validate_priority(value: str):
    """
    Valida que la prioridad sea válida
    """
    valid_priorities = ['baja', 'media', 'alta', 'crítica']
    
    if value.lower() not in valid_priorities:
        raise ValidationError(
            _(f'Prioridad no válida. Debe ser una de: {", ".join(valid_priorities)}'),
            code='invalid_priority'
        )
    
    return value


def validate_positive_number(value):
    """
    Valida que un número sea positivo
    """
    if value <= 0:
        raise ValidationError(
            _('El valor debe ser un número positivo.'),
            code='not_positive'
        )
    
    return value


def validate_business_hours(value):
    """
    Valida que un tiempo esté dentro del horario laboral (9 AM - 6 PM)
    """
    if value.hour < 9 or value.hour >= 18:
        raise ValidationError(
            _('La hora debe estar dentro del horario laboral (9:00 AM - 6:00 PM).'),
            code='outside_business_hours'
        )
    
    return value


class TicketValidator:
    """
    Validador personalizado para tickets
    """
    @staticmethod
    def validate_ticket_data(ticket_data: dict) -> tuple[bool, list]:
        """
        Valida los datos de un ticket
        Retorna (es_válido, lista_de_errores)
        """
        errors = []
        
        # Validar título
        if not ticket_data.get('ticket_title'):
            errors.append('El título del ticket es requerido')
        elif len(ticket_data['ticket_title']) < 5:
            errors.append('El título debe tener al menos 5 caracteres')
        
        # Validar descripción
        if not ticket_data.get('ticket_description'):
            errors.append('La descripción del ticket es requerida')
        elif len(ticket_data['ticket_description']) < 10:
            errors.append('La descripción debe tener al menos 10 caracteres')
        
        # Validar servicio
        if not ticket_data.get('ticket_service'):
            errors.append('El servicio es requerido')
        
        # Validar prioridad
        if not ticket_data.get('ticket_priority'):
            errors.append('La prioridad es requerida')
        
        # Validar usuario reportador
        if not ticket_data.get('reporter_user'):
            errors.append('El usuario reportador es requerido')
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_ticket_closure(ticket) -> tuple[bool, str]:
        """
        Valida que un ticket pueda ser cerrado
        """
        if not ticket.assigned_to:
            return False, 'El ticket debe estar asignado antes de cerrarse'
        
        if not ticket.ticket_closing_code:
            return False, 'Se requiere un código de cierre'
        
        # Verificar que tenga al menos una nota
        if ticket.note_set.count() == 0:
            return False, 'El ticket debe tener al menos una nota antes de cerrarse'
        
        return True, ''


class UserValidator:
    """
    Validador personalizado para usuarios
    """
    @staticmethod
    def validate_user_data(user_data: dict) -> tuple[bool, list]:
        """
        Valida los datos de un usuario empresarial
        """
        errors = []
        
        # Validar nombre
        if not user_data.get('name'):
            errors.append('El nombre es requerido')
        
        # Validar apellido
        if not user_data.get('last_name'):
            errors.append('El apellido es requerido')
        
        # Validar email
        if user_data.get('email'):
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, user_data['email']):
                errors.append('El formato del email no es válido')
        
        # Validar teléfono
        if user_data.get('phone'):
            try:
                validate_phone_number(user_data['phone'])
            except ValidationError as e:
                errors.append(str(e))
        
        return len(errors) == 0, errors
