"""
Utilidades comunes para el proyecto
"""
from datetime import datetime, timedelta
from typing import Optional
import re


def generate_ticket_id() -> int:
    """
    Genera un ID único para un ticket basado en timestamp
    """
    from .models import Ticket
    
    # Obtener el último ticket
    last_ticket = Ticket.objects.order_by('-id_ticket').first()
    
    if last_ticket:
        return last_ticket.id_ticket + 1
    return 1


def calculate_estimated_closing_date(
    service,
    priority: str,
    creation_date: Optional[datetime] = None
) -> datetime:
    """
    Calcula la fecha estimada de cierre basada en el servicio y prioridad
    """
    if creation_date is None:
        creation_date = datetime.now()
    
    # Obtener tiempo estimado del servicio
    estimated_time = service.estimated_solution_time if service else None
    
    # Ajustar según prioridad
    priority_multipliers = {
        'alta': 0.5,
        'media': 1.0,
        'baja': 1.5,
        'crítica': 0.25
    }
    
    multiplier = priority_multipliers.get(priority.lower(), 1.0)
    
    if estimated_time:
        # Convertir tiempo estimado a horas
        hours = estimated_time.hour + (estimated_time.minute / 60)
        adjusted_hours = hours * multiplier
        return creation_date + timedelta(hours=adjusted_hours)
    
    # Valor por defecto si no hay tiempo estimado
    default_hours = {
        'crítica': 4,
        'alta': 8,
        'media': 24,
        'baja': 48
    }
    
    hours = default_hours.get(priority.lower(), 24)
    return creation_date + timedelta(hours=hours)


def format_phone_number(phone: str) -> str:
    """
    Formatea un número de teléfono
    """
    # Eliminar caracteres no numéricos
    phone = re.sub(r'\D', '', phone)
    
    # Formatear según la longitud
    if len(phone) == 10:
        return f"({phone[:3]}) {phone[3:6]}-{phone[6:]}"
    elif len(phone) == 11:
        return f"+{phone[0]} ({phone[1:4]}) {phone[4:7]}-{phone[7:]}"
    
    return phone


def validate_email(email: str) -> bool:
    """
    Valida un formato de email
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def get_business_hours_diff(start_date: datetime, end_date: datetime) -> float:
    """
    Calcula la diferencia en horas hábiles entre dos fechas
    Solo cuenta de lunes a viernes, de 9 AM a 6 PM
    """
    business_hours = 0
    current = start_date
    
    while current < end_date:
        # Verificar si es día hábil (lunes=0, domingo=6)
        if current.weekday() < 5:
            # Hora de inicio (9 AM)
            start_of_day = current.replace(hour=9, minute=0, second=0)
            # Hora de fin (6 PM)
            end_of_day = current.replace(hour=18, minute=0, second=0)
            
            # Ajustar inicio si la fecha actual es después de las 9 AM
            if current > start_of_day:
                start_of_day = current
            
            # Ajustar fin si la fecha final es antes de las 6 PM
            if end_date < end_of_day:
                end_of_day = end_date
            
            # Si ambas fechas están dentro del horario hábil
            if start_of_day < end_of_day and start_of_day.hour < 18:
                diff = (end_of_day - start_of_day).total_seconds() / 3600
                business_hours += diff
        
        # Avanzar al siguiente día
        current = (current + timedelta(days=1)).replace(hour=9, minute=0, second=0)
        
        if current >= end_date:
            break
    
    return business_hours


def sanitize_filename(filename: str) -> str:
    """
    Sanitiza un nombre de archivo eliminando caracteres peligrosos
    """
    # Mantener solo caracteres alfanuméricos, guiones, puntos y guiones bajos
    filename = re.sub(r'[^\w\s.-]', '', filename)
    # Reemplazar espacios por guiones bajos
    filename = re.sub(r'\s+', '_', filename)
    return filename


def generate_report_filename(report_type: str, extension: str = 'pdf') -> str:
    """
    Genera un nombre de archivo para reportes
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{report_type}_{timestamp}.{extension}"


class ResponseFormatter:
    """
    Clase para formatear respuestas consistentes de la API
    """
    @staticmethod
    def success(data=None, message: str = "Operación exitosa", status_code: int = 200):
        """
        Formato de respuesta exitosa
        """
        return {
            'success': True,
            'message': message,
            'data': data,
            'status_code': status_code
        }
    
    @staticmethod
    def error(message: str, errors=None, status_code: int = 400):
        """
        Formato de respuesta de error
        """
        return {
            'success': False,
            'message': message,
            'errors': errors,
            'status_code': status_code
        }
    
    @staticmethod
    def paginated(data, page, total_pages, total_items):
        """
        Formato de respuesta paginada
        """
        return {
            'success': True,
            'data': data,
            'pagination': {
                'current_page': page,
                'total_pages': total_pages,
                'total_items': total_items
            }
        }
