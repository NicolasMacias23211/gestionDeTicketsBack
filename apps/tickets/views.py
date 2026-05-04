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
    WorkingHoursSerializer, ProjectDateSerializer, TicketReporteGeneralSerializer,
    TicketReporteDriverSerializer
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
    permission_classes = [IsAuthenticated]
    # permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


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

    @action(detail=False, methods=['get'], url_path='dashboard-stats')
    def dashboard_stats(self, request):
        """
        Obtiene estadísticas personales del dashboard para un usuario específico.

        Parámetros query:
        - assigned_to (obligatorio): network_user del usuario a consultar

        Respuesta:
        - assigned: Total de tickets asignados activos (sin fecha de cierre)
        - in_progress: Tickets activos cuyo estado tiene un valor de ordering
        - completed_this_month: Tickets completados en el mes actual (cumplimiento=True)
        - overdue: Tickets vencidos en el mes actual (cumplimiento=False)
        """
        assigned_to = request.query_params.get('assigned_to')

        if not assigned_to:
            return Response({
                'success': False,
                'message': 'El parámetro assigned_to es obligatorio'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Verificar que el usuario existe
        if not EUser.objects.filter(network_user=assigned_to).exists():
            return Response({
                'success': False,
                'message': f'El usuario {assigned_to} no existe'
            }, status=status.HTTP_404_NOT_FOUND)

        now = timezone.now()
        first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # assigned: tickets activos (sin closing_date) asignados a este usuario
        assigned = Ticket.objects.filter(
            closing_date__isnull=True,
            assigned_to=assigned_to
        ).count()

        # in_progress: tickets activos de este usuario cuyo status tiene ordering con valor
        in_progress = Ticket.objects.filter(
            closing_date__isnull=True,
            assigned_to=assigned_to,
            status_id__ordering__isnull=False
        ).count()

        # completed_this_month: tickets de este usuario cerrados este mes con cumplimiento=True
        completed_this_month = Ticket.objects.filter(
            assigned_to=assigned_to,
            closing_date__gte=first_day_of_month,
            closing_date__lte=now,
            cumplimiento=True
        ).count()

        # overdue: tickets de este usuario cerrados este mes con cumplimiento=False
        overdue = Ticket.objects.filter(
            assigned_to=assigned_to,
            closing_date__gte=first_day_of_month,
            closing_date__lte=now,
            cumplimiento=False
        ).count()

        return Response({
            'success': True,
            'data': {
                'assigned': assigned,
                'in_progress': in_progress,
                'completed_this_month': completed_this_month,
                'overdue': overdue,
            }
        })

    @action(detail=False, methods=['get'], url_path='reporte-general')
    def reporte_general(self, request):
        """
        Reporte general de tickets en un rango de fechas.

        Parámetros query:
        - fecha_desde (obligatorio): YYYY-MM-DD — inicio del rango (por create_at)
        - fecha_hasta (obligatorio): YYYY-MM-DD — fin del rango (inclusive)
        - cliente      (opcional): nombre exacto del cliente
        - id_servicio  (opcional): ID del tipo de servicio
        - network_user (opcional): network_user del EUser asignado
        - cumple       (opcional): true / false — si se omite devuelve todos
        """
        from datetime import datetime, time as dt_time

        fecha_desde_str = request.query_params.get('fecha_desde')
        fecha_hasta_str = request.query_params.get('fecha_hasta')

        if not fecha_desde_str or not fecha_hasta_str:
            return Response({
                'success': False,
                'message': 'Los parámetros fecha_desde y fecha_hasta son obligatorios'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            fecha_desde = timezone.make_aware(
                datetime.combine(datetime.strptime(fecha_desde_str, '%Y-%m-%d').date(), dt_time.min)
            )
            fecha_hasta = timezone.make_aware(
                datetime.combine(datetime.strptime(fecha_hasta_str, '%Y-%m-%d').date(), dt_time.max)
            )
        except ValueError:
            return Response({
                'success': False,
                'message': 'Formato de fecha inválido. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)

        queryset = Ticket.objects.select_related(
            'ticket_service',
            'assigned_to',
            'sub_program_name__program_name__client_name',
        ).prefetch_related('reportedtime_set').filter(
            create_at__gte=fecha_desde,
            create_at__lte=fecha_hasta,
        )

        cliente = request.query_params.get('cliente')
        if cliente:
            queryset = queryset.filter(
                sub_program_name__program_name__client_name__client_name=cliente
            )

        id_servicio = request.query_params.get('id_servicio')
        if id_servicio:
            try:
                queryset = queryset.filter(ticket_service__id_services=int(id_servicio))
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'id_servicio debe ser un número entero'
                }, status=status.HTTP_400_BAD_REQUEST)

        network_user = request.query_params.get('network_user')
        if network_user:
            queryset = queryset.filter(assigned_to__network_user=network_user)

        cumple_str = request.query_params.get('cumple')
        if cumple_str is not None:
            if cumple_str.lower() == 'true':
                queryset = queryset.filter(cumplimiento=True)
            elif cumple_str.lower() == 'false':
                queryset = queryset.filter(cumplimiento=False)
            else:
                return Response({
                    'success': False,
                    'message': 'El parámetro cumple debe ser "true" o "false"'
                }, status=status.HTTP_400_BAD_REQUEST)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = TicketReporteGeneralSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = TicketReporteGeneralSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='reporte-driver')
    def reporte_driver(self, request):
        """
        Reporte driver: tickets agrupados por usuario E-User y cliente con métricas de ocupación.

        Parámetros query:
        - fecha_desde  (obligatorio): YYYY-MM-DD — inicio del rango (por date_reported)
        - fecha_hasta  (obligatorio): YYYY-MM-DD — fin del rango (inclusive)
        - cliente      (opcional): nombre exacto del cliente
        - network_user (opcional): network_user del EUser asignado al ticket
        """
        from datetime import datetime, date as dt_date
        from collections import defaultdict

        fecha_desde_str = request.query_params.get('fecha_desde')
        fecha_hasta_str = request.query_params.get('fecha_hasta')

        if not fecha_desde_str or not fecha_hasta_str:
            return Response(
                {'detail': 'Los parámetros fecha_desde y fecha_hasta son obligatorios'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            fecha_desde = datetime.strptime(fecha_desde_str, '%Y-%m-%d').date()
            fecha_hasta = datetime.strptime(fecha_hasta_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'detail': 'Formato de fecha inválido. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )

        def time_to_seconds(t):
            return t.hour * 3600 + t.minute * 60 + t.second

        def seconds_to_str(total_seconds):
            hours, remainder = divmod(int(total_seconds), 3600)
            minutes, seconds = divmod(remainder, 60)
            return f'{hours:02}:{minutes:02}:{seconds:02}'

        # All reported times in the period for tickets that have an assigned user.
        # Filtered by the ticket's assigned_to (not the reporter) so that
        # user_total_seconds spans all clients correctly.
        rt_qs = ReportedTime.objects.filter(
            date_reported__date__gte=fecha_desde,
            date_reported__date__lte=fecha_hasta,
            id_ticket__assigned_to__isnull=False,
        ).select_related(
            'id_ticket',
            'id_ticket__assigned_to',
            'id_ticket__sub_program_name__program_name__client_name',
        )

        network_user_filter = request.query_params.get('network_user')
        if network_user_filter:
            rt_qs = rt_qs.filter(
                id_ticket__assigned_to__network_user=network_user_filter
            )

        # Single-pass aggregation
        ticket_seconds = defaultdict(int)           # ticket_id -> seconds
        user_client_seconds = defaultdict(int)      # (network_user, client) -> seconds
        user_total_seconds = defaultdict(int)       # network_user -> seconds
        ticket_info = {}                            # ticket_id -> Ticket instance
        tickets_for_combo = defaultdict(set)        # (network_user, client) -> {ticket_ids}

        for rt in rt_qs:
            ticket = rt.id_ticket
            euser = ticket.assigned_to
            if not euser:
                continue
            try:
                client_name = ticket.sub_program_name.program_name.client_name.client_name
            except AttributeError:
                continue

            nu = euser.network_user
            secs = time_to_seconds(rt.reported_time)

            ticket_seconds[ticket.id_ticket] += secs
            user_client_seconds[(nu, client_name)] += secs
            user_total_seconds[nu] += secs
            ticket_info[ticket.id_ticket] = ticket
            tickets_for_combo[(nu, client_name)].add(ticket.id_ticket)

        # Apply optional client filter to output only (not to aggregations so that
        # user_total_seconds always reflects all clients)
        cliente_filter = request.query_params.get('cliente')
        if cliente_filter:
            combos = {k: v for k, v in tickets_for_combo.items() if k[1] == cliente_filter}
        else:
            combos = tickets_for_combo

        results = []
        for (nu, client_name), ticket_ids in combos.items():
            t_uc = user_client_seconds[(nu, client_name)]
            t_total = user_total_seconds[nu]
            porcentaje = round((t_uc / t_total) * 100, 1) if t_total > 0 else 0.0

            for ticket_id in ticket_ids:
                ticket = ticket_info[ticket_id]
                euser = ticket.assigned_to
                parts = [euser.name]
                if euser.middle_name:
                    parts.append(euser.middle_name)
                parts.append(euser.last_name)
                if euser.second_last_name:
                    parts.append(euser.second_last_name)

                results.append({
                    'euser_nombre': ' '.join(parts),
                    'network_user': nu,
                    'cliente': client_name,
                    'id_ticket': ticket_id,
                    'ticket_title': ticket.ticket_title,
                    'fecha_creacion': ticket.create_at,
                    'fecha_cierre': ticket.closing_date,
                    'fecha_estimada_cierre': ticket.estimated_closing_date,
                    'tiempo_ticket': seconds_to_str(ticket_seconds[ticket_id]),
                    'tiempo_usuario_cliente': seconds_to_str(t_uc),
                    'porcentaje_cliente': porcentaje,
                    'tiempo_total_usuario': seconds_to_str(t_total),
                    'cumple': ticket.cumplimiento,
                })

        results.sort(key=lambda x: (x['network_user'], x['cliente'], x['id_ticket']))

        page = self.paginate_queryset(results)
        if page is not None:
            serializer = TicketReporteDriverSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = TicketReporteDriverSerializer(results, many=True)
        return Response(serializer.data)

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

    @action(detail=False, methods=['get'], url_path='recent-activity')
    def recent_activity(self, request):
        """
        Obtiene las últimas notas de los tickets asignados a un usuario.

        Parámetros query:
        - assigned_to (obligatorio): network_user del usuario
        - limit (opcional): cantidad de notas a retornar (por defecto 5)
        """
        assigned_to = request.query_params.get('assigned_to')

        if not assigned_to:
            return Response({
                'success': False,
                'message': 'El parámetro assigned_to es obligatorio'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Verificar que el usuario existe
        if not EUser.objects.filter(network_user=assigned_to).exists():
            return Response({
                'success': False,
                'message': f'El usuario {assigned_to} no existe'
            }, status=status.HTTP_404_NOT_FOUND)

        # Limit con valor por defecto de 5
        try:
            limit = int(request.query_params.get('limit', 5))
        except (ValueError, TypeError):
            limit = 5

        # 1 mes calendario hacia atrás desde hoy
        now = timezone.now()
        one_month_ago = now - timedelta(days=30)

        # Notas del último mes en tickets asignados a este usuario
        notes = (
            Note.objects
            .select_related('id_ticket', 'network_user')
            .filter(
                id_ticket__assigned_to=assigned_to,
                create_at__gte=one_month_ago,
                create_at__lte=now
            )
            .order_by('-create_at')[:limit]
        )

        data = []
        for note in notes:
            # Construir full_name del autor de la nota
            full_name = ''
            if note.network_user:
                parts = [note.network_user.name]
                if note.network_user.middle_name:
                    parts.append(note.network_user.middle_name)
                parts.append(note.network_user.last_name)
                if note.network_user.second_last_name:
                    parts.append(note.network_user.second_last_name)
                full_name = ' '.join(parts)

            data.append({
                'id_note': note.id_note,
                'note_preview': note.note[:100] + ('...' if len(note.note) > 100 else ''),
                'id_ticket': note.id_ticket.id_ticket,
                'ticket_title': note.id_ticket.ticket_title,
                'network_user': note.network_user.network_user if note.network_user else None,
                'full_name': full_name,
                'create_at': note.create_at,
            })

        return Response({
            'success': True,
            'data': data
        })

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