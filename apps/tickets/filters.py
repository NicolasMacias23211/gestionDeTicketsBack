import django_filters
from django.db.models import Q
from .models import Ticket, ReportedTime


class TicketFilter(django_filters.FilterSet):
    """
    Filtros personalizados para tickets
    """
    # Filtros de fecha
    create_at_after = django_filters.DateTimeFilter(
        field_name='create_at',
        lookup_expr='gte',
        label='Creado después de'
    )
    create_at_before = django_filters.DateTimeFilter(
        field_name='create_at',
        lookup_expr='lte',
        label='Creado antes de'
    )
    
    # Filtros de cierre
    closing_date_after = django_filters.DateTimeFilter(
        field_name='closing_date',
        lookup_expr='gte',
        label='Cerrado después de'
    )
    closing_date_before = django_filters.DateTimeFilter(
        field_name='closing_date',
        lookup_expr='lte',
        label='Cerrado antes de'
    )
    
    # Filtro de búsqueda general
    search = django_filters.CharFilter(
        method='filter_search',
        label='Búsqueda general'
    )
    
    # Filtros por relaciones
    service = django_filters.NumberFilter(
        field_name='ticket_service__id_services',
        label='Servicio'
    )
    priority = django_filters.CharFilter(
        field_name='ticket_priority__priority_name',
        label='Prioridad'
    )
    status = django_filters.NumberFilter(
        field_name='status_id__status_id',
        label='Estado'
    )
    client = django_filters.CharFilter(
        field_name='sub_program_name__program_name__client_name__client_name',
        label='Cliente'
    )
    
    # Filtro booleano para tickets asignados/sin asignar
    is_assigned = django_filters.BooleanFilter(
        method='filter_is_assigned',
        label='Está asignado'
    )
    
    # Filtro para tickets vencidos
    is_overdue = django_filters.BooleanFilter(
        method='filter_is_overdue',
        label='Está vencido'
    )

    class Meta:
        model = Ticket
        fields = {
            'id_ticket': ['exact'],
            'reporter_user': ['exact'],
            'assigned_to': ['exact', 'isnull'],
            'ticket_service': ['exact'],
            'ticket_priority': ['exact'],
            'status_id': ['exact'],
        }

    def filter_search(self, queryset, name, value):
        """
        Búsqueda general en múltiples campos
        """
        return queryset.filter(
            Q(ticket_title__icontains=value) |
            Q(ticket_description__icontains=value) |
            Q(id_ticket__icontains=value)
        )

    def filter_is_assigned(self, queryset, name, value):
        """
        Filtrar por tickets asignados o sin asignar
        """
        if value:
            return queryset.exclude(assigned_to__isnull=True).exclude(assigned_to='')
        return queryset.filter(Q(assigned_to__isnull=True) | Q(assigned_to=''))

    def filter_is_overdue(self, queryset, name, value):
        """
        Filtrar por tickets vencidos
        """
        from django.utils import timezone
        
        if value:
            return queryset.filter(
                estimated_closing_date__lt=timezone.now(),
                closing_date__isnull=True
            )
        return queryset.filter(
            Q(estimated_closing_date__gte=timezone.now()) |
            Q(closing_date__isnull=False)
        )


class ReportedTimeFilter(django_filters.FilterSet):
    """
    Filtros personalizados para tiempos reportados
    """
    # Filtro de usuario
    network_user = django_filters.CharFilter(
        field_name='network_user__network_user',
        lookup_expr='exact',
        label='Usuario de Red'
    )
    
    # Filtros de rango de fechas
    date_reported_after = django_filters.DateTimeFilter(
        field_name='date_reported',
        lookup_expr='gte',
        label='Fecha reportada después de'
    )
    date_reported_before = django_filters.DateTimeFilter(
        field_name='date_reported',
        lookup_expr='lte',
        label='Fecha reportada antes de'
    )
    
    # Filtro combinado de usuario y rango de fechas
    user_date_range = django_filters.CharFilter(
        method='filter_user_date_range',
        label='Filtrar por usuario y rango de fechas'
    )
    
    class Meta:
        model = ReportedTime
        fields = {
            'id_reported_times': ['exact'],
            'id_ticket': ['exact'],
            'network_user': ['exact'],
        }
    
    def filter_user_date_range(self, queryset, name, value):
        """
        Método personalizado para aplicar filtros combinados
        Este método puede usarse desde código si necesitas un filtrado programático
        """
        # Este es un método de ejemplo, normalmente usarás los filtros individuales
        # pero se puede extender si necesitas lógica más compleja
        return queryset
