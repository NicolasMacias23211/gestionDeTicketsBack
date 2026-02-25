from urllib import response
from django.http import HttpResponse
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from django.utils import timezone
import requests
from datetime import datetime, timedelta
from core.utils.helpers import Pagination

from core.base.mixins import CustomDeleteMixin

from .models import (
    Client, Service, Role, EUser, TicketPriority, Program, SubProgram,
    ClosingCode, ANS, User, Status, Ticket, ReportedTime, Note, WorkingHours
)
from .serializers import (
    ClientSerializer, ServiceSerializer, RoleSerializer, EUserSerializer,
    EUserCreateSerializer, TicketPrioritySerializer, ProgramSerializer,
    SubProgramSerializer, ClosingCodeSerializer, ANSSerializer,
    TicketUserSerializer, StatusSerializer, TicketListSerializer,
    TicketDetailSerializer, TicketCreateSerializer, TicketUpdateSerializer,
    ReportedTimeSerializer, ReportedTimeCreateSerializer, NoteSerializer,
    NoteCreateSerializer, TicketAssignSerializer, TicketStatsSerializer, 
    WorkingHoursSerializer, ProjectDateSerializer
)
from .filters import TicketFilter, ReportedTimeFilter
from .permissions import IsTicketOwnerOrAssigned, IsAdminOrReadOnly


class ClientViewSet(CustomDeleteMixin, viewsets.ModelViewSet):
    """
    ViewSet para gestionar clientes
    """
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['client_name']
    ordering_fields = ['client_name']


class ServiceViewSet(CustomDeleteMixin, viewsets.ModelViewSet):
    """
    ViewSet para gestionar servicios
    """
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['service_name', 'service_description']
    ordering_fields = ['id_services', 'service_name']


class RoleViewSet(CustomDeleteMixin, viewsets.ModelViewSet):
    """
    ViewSet para gestionar roles
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['rol_name', 'description']


class EUserViewSet(CustomDeleteMixin, viewsets.ModelViewSet):
    """
    ViewSet para gestionar usuarios empresariales
    """
    queryset = EUser.objects.select_related(
        'user_client_name', 'id_services', 'rol_name'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['network_user', 'name', 'last_name', 'email']
    filterset_fields = ['user_client_name', 'rol_name', 'id_services']
    ordering_fields = ['network_user', 'name', 'last_name']
    lookup_field = 'network_user'

    def get_serializer_class(self):
        if self.action == 'create':
            return EUserCreateSerializer
        return EUserSerializer

    @action(detail=False, methods=['get'], url_path='metricas-cumplimiento')
    def metricas_cumplimiento(self, request):
        """
        Obtiene el porcentaje de cumplimiento de un usuario en un rango de fechas
        
        Parámetros query:
        - network_user (obligatorio): Usuario a consultar
        - fecha_desde (opcional): Fecha inicio en formato YYYY-MM-DD (por defecto: día 1 del mes actual)
        - fecha_hasta (opcional): Fecha fin en formato YYYY-MM-DD (por defecto: día actual)
        """
        from datetime import datetime, time
        
        # Obtener parámetros
        network_user = request.query_params.get('network_user')
        
        if not network_user:
            return Response({
                'success': False,
                'message': 'El parámetro network_user es obligatorio'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar que el usuario existe
        try:
            user = EUser.objects.get(network_user=network_user)
        except EUser.DoesNotExist:
            return Response({
                'success': False,
                'message': f'El usuario {network_user} no existe'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Configurar fechas
        now = timezone.now()
        
        # Fecha desde: día 1 del mes actual a las 00:00:00
        fecha_desde_str = request.query_params.get('fecha_desde')
        if fecha_desde_str:
            try:
                fecha_desde = datetime.strptime(fecha_desde_str, '%Y-%m-%d')
                fecha_desde = timezone.make_aware(datetime.combine(fecha_desde.date(), time.min))
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'Formato de fecha_desde inválido. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            fecha_desde = timezone.make_aware(datetime(now.year, now.month, 1, 0, 0, 0))
        
        # Fecha hasta: día actual a las 23:59:59
        fecha_hasta_str = request.query_params.get('fecha_hasta')
        if fecha_hasta_str:
            try:
                fecha_hasta = datetime.strptime(fecha_hasta_str, '%Y-%m-%d')
                fecha_hasta = timezone.make_aware(datetime.combine(fecha_hasta.date(), time.max))
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'Formato de fecha_hasta inválido. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            fecha_hasta = timezone.make_aware(datetime.combine(now.date(), time.max))
        
        # Consultar tickets asignados al usuario en el rango de fechas
        tickets = Ticket.objects.filter(
            assigned_to=network_user,
            create_at__gte=fecha_desde,
            create_at__lte=fecha_hasta
        )
        
        total_tickets = tickets.count()
        
        if total_tickets == 0:
            return Response({
                'success': True,
                'data': {
                    'network_user': network_user,
                    'nombre_completo': user.name + ' ' + user.last_name,
                    'fecha_desde': fecha_desde.strftime('%Y-%m-%d'),
                    'fecha_hasta': fecha_hasta.strftime('%Y-%m-%d'),
                    'total_tickets': 0,
                    'tickets_cumplimiento': 0,
                    'porcentaje_cumplimiento': 0
                }
            })
        
        # Contar tickets con cumplimiento = True
        tickets_cumplimiento = tickets.filter(cumplimiento=True).count()
        
        # Calcular porcentaje
        porcentaje_cumplimiento = round((tickets_cumplimiento / total_tickets) * 100, 2)
        
        return Response({
            'success': True,
            'data': {
                'network_user': network_user,
                'nombre_completo': user.name + ' ' + user.last_name,
                'fecha_desde': fecha_desde.strftime('%Y-%m-%d'),
                'fecha_hasta': fecha_hasta.strftime('%Y-%m-%d'),
                'total_tickets': total_tickets,
                'tickets_cumplimiento': tickets_cumplimiento,
                'porcentaje_cumplimiento': porcentaje_cumplimiento
            }
        })

    @action(detail=False, methods=['get'], url_path='metricas-ocupacion')
    def metricas_ocupacion(self, request):
        """
        Obtiene el porcentaje de ocupación de un usuario en un rango de fechas
        
        Parámetros query:
        - network_user (obligatorio): Usuario a consultar
        - fecha_desde (opcional): Fecha inicio en formato YYYY-MM-DD (por defecto: día 1 del mes actual)
        - fecha_hasta (opcional): Fecha fin en formato YYYY-MM-DD (por defecto: día actual)
        """
        from datetime import datetime, time
        
        # Obtener parámetros
        network_user = request.query_params.get('network_user')
        
        if not network_user:
            return Response({
                'success': False,
                'message': 'El parámetro network_user es obligatorio'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar que el usuario existe
        try:
            user = EUser.objects.get(network_user=network_user)
        except EUser.DoesNotExist:
            return Response({
                'success': False,
                'message': f'El usuario {network_user} no existe'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Configurar fechas
        now = timezone.now()
        
        # Fecha desde: día 1 del mes actual a las 00:00:00
        fecha_desde_str = request.query_params.get('fecha_desde')
        if fecha_desde_str:
            try:
                fecha_desde = datetime.strptime(fecha_desde_str, '%Y-%m-%d')
                fecha_desde = timezone.make_aware(datetime.combine(fecha_desde.date(), time.min))
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'Formato de fecha_desde inválido. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            fecha_desde = timezone.make_aware(datetime(now.year, now.month, 1, 0, 0, 0))
        
        # Fecha hasta: día actual a las 23:59:59
        fecha_hasta_str = request.query_params.get('fecha_hasta')
        if fecha_hasta_str:
            try:
                fecha_hasta = datetime.strptime(fecha_hasta_str, '%Y-%m-%d')
                fecha_hasta = timezone.make_aware(datetime.combine(fecha_hasta.date(), time.max))
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'Formato de fecha_hasta inválido. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            fecha_hasta = timezone.make_aware(datetime.combine(now.date(), time.max))
        
        # Consultar tiempos reportados por el usuario en el rango de fechas
        reported_times = ReportedTime.objects.filter(
            network_user=network_user,
            date_reported__gte=fecha_desde,
            date_reported__lte=fecha_hasta
        )
        
        # Sumar todos los reported_time
        total_reported_seconds = 0
        for rt in reported_times:
            # Convertir time a segundos
            reported_time = rt.reported_time
            seconds = reported_time.hour * 3600 + reported_time.minute * 60 + reported_time.second
            total_reported_seconds += seconds
        
        # Convertir a horas
        total_reported_hours = round(total_reported_seconds / 3600, 2)
        
        # Obtener horarios laborales
        working_hours = WorkingHours.objects.all()
        
        if not working_hours.exists():
            return Response({
                'success': False,
                'message': 'No hay horarios laborales configurados'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Crear diccionario de horarios por día de la semana
        # Python weekday(): 0=Lunes, 1=Martes, ..., 6=Domingo
        weekday_map = {
            'Lunes': 0,
            'Martes': 1,
            'Miércoles': 2,
            'Jueves': 3,
            'Viernes': 4,
            'Sábado': 5,
            'Domingo': 6
        }
        
        working_schedule = {}
        for wh in working_hours:
            weekday_num = weekday_map.get(wh.week_day)
            if weekday_num is not None:
                # Calcular horas del día
                start = datetime.combine(datetime.today(), wh.start_time)
                end = datetime.combine(datetime.today(), wh.end_time)
                hours_per_day = (end - start).total_seconds() / 3600
                working_schedule[weekday_num] = hours_per_day
        
        # Calcular horas disponibles en el rango de fechas
        total_working_hours = 0
        current_date = fecha_desde.date()
        end_date = fecha_hasta.date()
        
        while current_date <= end_date:
            weekday = current_date.weekday()
            if weekday in working_schedule:
                hours = working_schedule[weekday]
                # Restar 1.5 horas por almuerzo y desayuno
                hours -= 1.5
                total_working_hours += hours
            current_date += timedelta(days=1)
        
        total_working_hours = round(total_working_hours, 2)
        
        # Calcular porcentaje de ocupación
        if total_working_hours > 0:
            porcentaje_ocupacion = round((total_reported_hours / total_working_hours) * 100, 2)
        else:
            porcentaje_ocupacion = 0
        
        return Response({
            'success': True,
            'data': {
                'network_user': network_user,
                'nombre_completo': user.name + ' ' + user.last_name,
                'fecha_desde': fecha_desde.strftime('%Y-%m-%d'),
                'fecha_hasta': fecha_hasta.strftime('%Y-%m-%d'),
                'total_horas_reportadas': total_reported_hours,
                'total_horas_disponibles': total_working_hours,
                'porcentaje_ocupacion': porcentaje_ocupacion
            }
        })


class TicketPriorityViewSet(CustomDeleteMixin, viewsets.ModelViewSet):
    """
    ViewSet para gestionar prioridades de tickets
    """
    queryset = TicketPriority.objects.all()
    serializer_class = TicketPrioritySerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


class ProgramViewSet(CustomDeleteMixin, viewsets.ModelViewSet):
    """
    ViewSet para gestionar programas
    """
    queryset = Program.objects.select_related('client_name').all()
    serializer_class = ProgramSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['client_name']
    search_fields = ['program_name']


class SubProgramViewSet(CustomDeleteMixin, viewsets.ModelViewSet):
    """
    ViewSet para gestionar sub-programas
    """
    queryset = SubProgram.objects.select_related('program_name').all()
    serializer_class = SubProgramSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['program_name']
    search_fields = ['sub_program_name']


class ClosingCodeViewSet(CustomDeleteMixin, viewsets.ModelViewSet):
    """
    ViewSet para gestionar códigos de cierre
    """
    queryset = ClosingCode.objects.all()
    serializer_class = ClosingCodeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['closing_code_name', 'closing_code_description']


class ANSViewSet(CustomDeleteMixin, viewsets.ModelViewSet):
    """
    ViewSet para gestionar ANS
    """
    queryset = ANS.objects.all()
    serializer_class = ANSSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['ans_name', 'ans_description']
    pagination_class = Pagination


class UserViewSet(CustomDeleteMixin, viewsets.ModelViewSet):
    """
    ViewSet para gestionar usuarios
    """
    queryset = User.objects.all()
    serializer_class = TicketUserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['network_user', 'mail']
    lookup_field = 'network_user'


class StatusViewSet(CustomDeleteMixin, viewsets.ModelViewSet):
    """
    ViewSet para gestionar estados
    """
    queryset = Status.objects.all()
    search_fields = ['is-backlog']
    serializer_class = StatusSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


class TicketViewSet(CustomDeleteMixin, viewsets.ModelViewSet):
    """
    ViewSet para gestionar tickets
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TicketFilter
    search_fields = ['ticket_title', 'ticket_description', 'id_ticket']
    ordering_fields = ['id_ticket', 'create_at', 'estimated_closing_date', 'ticket_priority']
    ordering = ['-create_at']
    lookup_field = 'id_ticket'

    def get_queryset(self):
        """
        Filtra tickets según el usuario y sus permisos
        """
        queryset = Ticket.objects.select_related(
            'ticket_service', 'ticket_priority', 'ticket_closing_code',
            'ticket_ans', 'reporter_user', 'status_id', 'sub_program_name'
        ).prefetch_related('note_set', 'reportedtime_set')

        user = self.request.user
        
        # Si es staff, puede ver todos los tickets
        if user.is_staff:
            return queryset
        
        # Usuarios normales solo ven sus tickets o tickets asignados
        return queryset.filter(
            Q(reporter_user__network_user=user.username) |
            Q(assigned_to=user.username)
        )

    def get_serializer_class(self):
        """
        Retorna el serializer apropiado según la acción
        """
        if self.action == 'list':
            return TicketListSerializer
        elif self.action == 'create':
            return TicketCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TicketUpdateSerializer
        return TicketDetailSerializer

    def perform_create(self, serializer):
        """
        Crear ticket con el usuario actual como reporter
        """
        serializer.save()

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """
        Asignar un ticket a un usuario
        """
        ticket = self.get_object()
        serializer = TicketAssignSerializer(data=request.data)
        
        if serializer.is_valid():
            ticket.assigned_to = serializer.validated_data['assigned_to']
            ticket.save()
            
            return Response({
                'success': True,
                'message': f'Ticket asignado a {ticket.assigned_to}',
                'ticket': TicketDetailSerializer(ticket).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """
        Cerrar un ticket
        """
        ticket = self.get_object()
        closing_code_id = request.data.get('closing_code_id')
        
        if not closing_code_id:
            return Response({
                'success': False,
                'message': 'Se requiere un código de cierre'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            closing_code = ClosingCode.objects.get(id_closing_code=closing_code_id)
            closed_status = Status.objects.filter(
                status_name__icontains='cerrado'
            ).first()
            
            if not closed_status:
                return Response({
                    'success': False,
                    'message': 'No se encontró el estado "Cerrado"'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            ticket.ticket_closing_code = closing_code
            ticket.status_id = closed_status
            ticket.closing_date = timezone.now()
            ticket.save()
            
            return Response({
                'success': True,
                'message': 'Ticket cerrado exitosamente',
                'ticket': TicketDetailSerializer(ticket).data
            })
            
        except ClosingCode.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Código de cierre no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def my_tickets(self, request):
        """
        Obtener tickets del usuario actual
        """
        user = request.user
        tickets = self.get_queryset().filter(reporter_user__network_user=user.username)
        
        page = self.paginate_queryset(tickets)
        if page is not None:
            serializer = TicketListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = TicketListSerializer(tickets, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def assigned_to_me(self, request):
        """
        Obtener tickets asignados al usuario actual
        """
        user = request.user
        tickets = self.get_queryset().filter(assigned_to=user.username)
        
        page = self.paginate_queryset(tickets)
        if page is not None:
            serializer = TicketListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = TicketListSerializer(tickets, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Obtener estadísticas de tickets
        """
        queryset = self.get_queryset()
        
        total_tickets = queryset.count()
        open_tickets = queryset.filter(
            status_id__status_name__icontains='abierto'
        ).count()
        closed_tickets = queryset.filter(
            status_id__status_name__icontains='cerrado'
        ).count()
        in_progress_tickets = queryset.filter(
            status_id__status_name__icontains='proceso'
        ).count()
        
        # Estadísticas por prioridad
        by_priority = queryset.values(
            'ticket_priority__priority_name'
        ).annotate(count=Count('id_ticket'))
        
        # Estadísticas por servicio
        by_service = queryset.values(
            'ticket_service__service_name'
        ).annotate(count=Count('id_ticket'))
        
        # Estadísticas por estado
        by_status = queryset.values(
            'status_id__status_name'
        ).annotate(count=Count('id_ticket'))
        
        data = {
            'total_tickets': total_tickets,
            'open_tickets': open_tickets,
            'closed_tickets': closed_tickets,
            'in_progress_tickets': in_progress_tickets,
            'by_priority': {item['ticket_priority__priority_name']: item['count'] for item in by_priority},
            'by_service': {item['ticket_service__service_name']: item['count'] for item in by_service},
            'by_status': {item['status_id__status_name']: item['count'] for item in by_status},
        }
        
        serializer = TicketStatsSerializer(data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='weekly-stats')
    def weekly_stats(self, request):
        """
        Obtiene tickets creados y cerrados día a día en los últimos 7 días (incluyendo hoy).

        Respuesta:
        - datos_diarios: lista con conteo de tickets creados (create_at) y cerrados (closing_date) por día
        """
        day_names = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']

        today = timezone.localdate()
        fecha_hasta = today
        fecha_desde = today - timedelta(days=6)

        datos_diarios = []
        for i in range(7):
            current_date = fecha_desde + timedelta(days=i)

            creados = Ticket.objects.filter(create_at__date=current_date).count()
            cerrados = Ticket.objects.filter(closing_date__date=current_date).count()

            datos_diarios.append({
                'dia': day_names[current_date.weekday()],
                'fecha': current_date.strftime('%Y-%m-%d'),
                'creados': creados,
                'cerrados': cerrados,
            })

        return Response({
            'success': True,
            'data': {
                'periodo': 'ultima_semana',
                'fecha_desde': fecha_desde.strftime('%Y-%m-%d'),
                'fecha_hasta': fecha_hasta.strftime('%Y-%m-%d'),
                'datos_diarios': datos_diarios,
            }
        })

    @action(detail=False, methods=['get'])
    def backlog(self, request):
        """
        Obtener tickets con estado de backlog (is_backlog=True)
        Filtros opcionales:
        - assigned_to: network_user del usuario asignado
        - search: búsqueda por título y/o descripción (LIKE)
        - ticket_id: búsqueda por ID del ticket (LIKE)
        """
        # Filtrar tickets donde el estado tiene is_backlog=True
        queryset = self.get_queryset().filter(status_id__is_backlog=True)
        
        # Aplicar filtro opcional por usuario asignado
        assigned_to = request.query_params.get('assigned_to', None)
        if assigned_to:
            queryset = queryset.filter(assigned_to=assigned_to)
        
        # Aplicar filtro de búsqueda por título y/o descripción
        search = request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(ticket_title__icontains=search) | 
                Q(ticket_description__icontains=search)
            )
        
        # Aplicar filtro por ID del ticket
        ticket_id = request.query_params.get('ticket_id', None)
        if ticket_id:
            queryset = queryset.filter(id_ticket__icontains=ticket_id)
        
        # Ordenar por fecha de creación (más recientes primero)
        queryset = queryset.order_by('-create_at')
        
        # Paginar los resultados
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = TicketDetailSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        # Si no hay paginación configurada, devolver todos los resultados
        serializer = TicketDetailSerializer(queryset, many=True)
        return Response(serializer.data)


class ReportedTimeViewSet(CustomDeleteMixin, viewsets.ModelViewSet):
    """
    ViewSet para gestionar tiempos reportados
    """
    queryset = ReportedTime.objects.select_related('id_ticket', 'network_user').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ReportedTimeFilter
    ordering_fields = ['date_reported', 'create_at']
    ordering = ['-date_reported']

    def get_serializer_class(self):
        if self.action == 'create':
            return ReportedTimeCreateSerializer
        return ReportedTimeSerializer


class NoteViewSet(CustomDeleteMixin, viewsets.ModelViewSet):
    """
    ViewSet para gestionar notas de tickets
    """
    queryset = Note.objects.select_related('id_ticket').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['id_ticket', 'visible_to_client']
    ordering_fields = ['create_at']
    ordering = ['-create_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return NoteCreateSerializer
        return NoteSerializer

    def get_queryset(self):
        """
        Filtra notas según permisos del usuario
        """
        queryset = super().get_queryset()
        user = self.request.user
        
        # Si no es staff, solo puede ver notas visibles para el cliente
        if not user.is_staff:
            queryset = queryset.filter(visible_to_client=True)
        
        return queryset

class WorkingHoursViewSet(CustomDeleteMixin, viewsets.ModelViewSet):
    """
    ViewSet para gestionar horas trabajadas en tickets
    """
   
    queryset = WorkingHours.objects.all()
    serializer_class = WorkingHoursSerializer
    permission_classes = [IsAuthenticated]
    # permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    
        
class ProjectDateViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectDateSerializer
    
    holidays = [];
    weekDays = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    schedules = [];
    start_time = None
    end_time = None
    
    def get_holidays(self):
        return self.holidays;
    
    def set_holidays(self, year):
        year = str(year)
        url = 'https://api-colombia.com/api/v1/Holiday/year/'+ year
        response = requests.get(url, verify=False)
        try:
            if response.status_code == 200:
                self.holidays = [];
                for holiday in response.json():
                    date = holiday.get("date")
                    onlyDate = date.split("T")[0]
                    self.holidays.append( datetime.strptime(onlyDate, "%Y-%m-%d").date())
        except:     
            raise 
       
    def get_schedules(self):
        return self.schedules;
    
    #Trae los horario registrados
    def set_schedules(self):
        schedulesRealized = WorkingHoursSerializer(WorkingHours.objects.all(), many=True)
        self.schedules = schedulesRealized.data
    
    #Valida si un día es habil o no
    def isWorkDay(self, date):
        dateString = date
        day = date.weekday()
        self.set_holidays(date.year)
        self.set_schedules()
        if dateString in self.get_holidays():
            return False
        
        for item in self.get_schedules():
            if item.get("week_day") == self.weekDays[day]:
                return True
        
        return False
    
    # Encuentra el siguiente día habil
    def getNextWorkDay(self, date):
        currentDay = date
        holiday = True
        while holiday:
            nextDay = currentDay + timedelta(days=1)
            if self.isWorkDay(nextDay):
                holiday = False
                break
            currentDay = nextDay;
        
        return nextDay
    
    # combina la fecha con la hora para entregar el formato requerido.
    def combineDateTime(self, date, time):
        dateTime = datetime.combine(date, time)
        dateTime = str(dateTime).replace(" ", "T")
        dateTime = datetime.strptime(dateTime, "%Y-%m-%dT%H:%M:%S") 
        return dateTime
    
    #Encuentra la hora de entra y salida de un dia de las semana.
    def set_times(self, date):
        for item in self.schedules: # Buscar el horario del día actual
            if item.get("week_day") == self.weekDays[date.weekday()]:
                self.start_time = item["start_time"]
                self.end_time = item["end_time"]
    
    @action(detail=False, methods=['post'])
    def findProjectDate(self, request):
        try:
            dateCurrent = datetime.strptime(request.data.get("date_creation"), "%Y-%m-%dT%H:%M:%S")        
            remainigHours = request.data.get("ans")
            timeDateInitial = dateCurrent.time()
            dateCurrent = self.combineDateTime(dateCurrent, timeDateInitial)
            self.set_schedules()
            
            while remainigHours > 0:
                # Si no es día laborable, buscar el siguiente            
                if not self.isWorkDay(dateCurrent.date()): 
                    dateCurrent = self.getNextWorkDay(dateCurrent.date())
                    self.set_times(dateCurrent)
                    dateCurrent = self.combineDateTime(dateCurrent, datetime.strptime(self.start_time, "%H:%M:%S").time())
                    continue 

                self.set_times(dateCurrent)
                    
                dateStarTime = self.combineDateTime(dateCurrent, datetime.strptime(self.start_time, "%H:%M:%S").time())
                # Si el momento actual es menor al hora de inicio de ese mismo día, ajustar a la hora de inicio del mismo día.
                if dateCurrent < dateStarTime: 
                    dateCurrent = dateStarTime
                    
                dateEndTime = self.combineDateTime(dateCurrent, datetime.strptime(self.end_time, "%H:%M:%S").time())
                # si el momento actual es mayor o igual a la hora final dese dia, ajustar a la hora de inicio del siguiente día.
                if dateCurrent >= dateEndTime:
                    self.set_times(dateCurrent)
                    dateCurrent = self.getNextWorkDay(dateCurrent.date())
                    dateCurrent = self.combineDateTime(dateCurrent, datetime.strptime(self.start_time, "%H:%M:%S").time())
                    continue
                            
                timeCurrenteEnd = self.combineDateTime(dateCurrent, datetime.strptime(self.end_time, "%H:%M:%S").time())
                
                # Calculo de el tiempo dispoble hasta final del dia actual 
                avalibleDayTime = (timeCurrenteEnd - dateCurrent).total_seconds() / 3600 
                #Si el tiempo restanten es menor al dispobible se suman las horas al momento actual
                if remainigHours <= avalibleDayTime: 
                    dateCurrent = dateCurrent + timedelta(hours=remainigHours)
                    remainigHours = 0
                    continue
                
                #Se restan la horas disponibles del día para calcular la horas restantes para el siguiente dái
                remainigHours = remainigHours - avalibleDayTime
                
                #Se encuentra el siguiente dpia habil y se le suman las horas restante
                dateCurrent = self.getNextWorkDay(dateCurrent.date())
                self.set_times(dateCurrent)
                dateCurrent = self.combineDateTime(dateCurrent, datetime.strptime(self.start_time, "%H:%M:%S").time())
                    
            return Response({"response": dateCurrent}, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)