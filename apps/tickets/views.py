from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from django.utils import timezone

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
    WorkingHoursSerializer
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

    def get_serializer_class(self):
        if self.action == 'create':
            return EUserCreateSerializer
        return EUserSerializer


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


class UserViewSet(CustomDeleteMixin, viewsets.ModelViewSet):
    """
    ViewSet para gestionar usuarios
    """
    queryset = User.objects.all()
    serializer_class = TicketUserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['network_user', 'mail']


class StatusViewSet(CustomDeleteMixin, viewsets.ModelViewSet):
    """
    ViewSet para gestionar estados
    """
    queryset = Status.objects.all()
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
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    
    @action(detail=False, methods=['get'])
    def backlog(self, request):
        pass