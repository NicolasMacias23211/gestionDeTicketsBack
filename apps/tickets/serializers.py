from rest_framework import serializers
from django.utils import timezone
from .models import (
    Client, Service, Role, EUser, TicketPriority, Program, SubProgram,
    ClosingCode, ANS, User, Status, Ticket, ReportedTime, Note, WorkingHours
)


class ClientSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Client"""
    class Meta:
        model = Client
        fields = '__all__'


class ServiceSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Service"""
    class Meta:
        model = Service
        fields = '__all__'
        read_only_fields = ['id_services']


class RoleSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Role"""
    class Meta:
        model = Role
        fields = '__all__'
        read_only_fields = ['id_rol']


class EUserSerializer(serializers.ModelSerializer):
    """Serializer para el modelo EUser"""
    user_client_name_display = serializers.CharField(
        source='user_client_name.client_name', read_only=True
    )
    service_name_display = serializers.CharField(
        source='id_services.service_name', read_only=True
    )
    rol_name_display = serializers.CharField(
        source='rol_name.rol_name', read_only=True
    )
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = EUser
        fields = '__all__'

    def get_full_name(self, obj) -> str:
        """Retorna el nombre completo del usuario"""
        parts = [obj.name]
        if obj.middle_name:
            parts.append(obj.middle_name)
        parts.append(obj.last_name)
        if obj.second_last_name:
            parts.append(obj.second_last_name)
        return ' '.join(parts)


class EUserCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear usuarios empresariales"""
    class Meta:
        model = EUser
        fields = '__all__'


class TicketPrioritySerializer(serializers.ModelSerializer):
    """Serializer para el modelo TicketPriority"""
    class Meta:
        model = TicketPriority
        fields = '__all__'
        read_only_fields = ['id_priority']


class ProgramSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Program"""
    client_name_display = serializers.CharField(
        source='client_name.client_name', read_only=True
    )

    class Meta:
        model = Program
        fields = '__all__'
        read_only_fields = ['id_program']


class SubProgramSerializer(serializers.ModelSerializer):
    """Serializer para el modelo SubProgram"""
    program_name_display = serializers.CharField(
        source='program_name.program_name', read_only=True
    )

    class Meta:
        model = SubProgram
        fields = '__all__'
        read_only_fields = ['id_sub_program']


class ClosingCodeSerializer(serializers.ModelSerializer):
    """Serializer para el modelo ClosingCode"""
    class Meta:
        model = ClosingCode
        fields = '__all__'
        read_only_fields = ['id_closing_code']
        read_only_fields = ['id_closing_code']


class ANSSerializer(serializers.ModelSerializer):
    """Serializer para el modelo ANS"""
    class Meta:
        model = ANS
        fields = '__all__'
        read_only_fields = ['id_ans']


class TicketUserSerializer(serializers.ModelSerializer):
    """Serializer para el modelo User (interno de tickets)"""
    class Meta:
        model = User
        fields = '__all__'


class StatusSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Status"""
    class Meta:
        model = Status
        fields = '__all__'
        read_only_fields = ['id_status']


class NoteSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Note"""
    class Meta:
        model = Note
        fields = '__all__'
        read_only_fields = ['id_note']


class NoteCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear notas"""
    class Meta:
        model = Note
        fields = ('note', 'visible_to_client', 'id_ticket', 'network_user')


class ReportedTimeSerializer(serializers.ModelSerializer):
    """Serializer para el modelo ReportedTime"""
    ticket_title = serializers.CharField(
        source='id_ticket.ticket_title', read_only=True
    )

    class Meta:
        model = ReportedTime
        fields = '__all__'
        read_only_fields = ['id_reported_times']


class ReportedTimeCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear tiempos reportados"""
    class Meta:
        model = ReportedTime
        fields = ('date_reported', 'reported_time', 'id_ticket', 'network_user')


class TicketListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar tickets"""
    service_name = serializers.CharField(
        source='ticket_service.service_name', read_only=True
    )
    priority_name = serializers.CharField(
        source='ticket_priority.priority_name', read_only=True
    )
    status_name = serializers.CharField(
        source='status_id.status_name', read_only=True
    )
    reporter_user_name = serializers.CharField(
        source='reporter_user.network_user', read_only=True
    )

    class Meta:
        model = Ticket
        fields = [
            'id_ticket', 'ticket_title', 'ticket_service', 'ticket_priority',
            'status_id', 'service_name', 'priority_name', 'status_name',
            'reporter_user_name', 'assigned_to', 'create_at',
            'estimated_closing_date', 'closing_date', 'cumplimiento', 'ticket_description', 'sub_program_name', 'ticket_ans'
        ]


class TicketDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para tickets"""
    service = ServiceSerializer(source='ticket_service', read_only=True)
    priority = TicketPrioritySerializer(source='ticket_priority', read_only=True)
    closing_code = ClosingCodeSerializer(source='ticket_closing_code', read_only=True)
    ans = ANSSerializer(source='ticket_ans', read_only=True)
    reporter = TicketUserSerializer(source='reporter_user', read_only=True)
    status = StatusSerializer(source='status_id', read_only=True)
    sub_program = SubProgramSerializer(source='sub_program_name', read_only=True)
    notes = NoteSerializer(many=True, read_only=True, source='note_set')
    reported_times = ReportedTimeSerializer(many=True, read_only=True, source='reportedtime_set')

    class Meta:
        model = Ticket
        fields = '__all__'


class TicketCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear tickets"""
    class Meta:
        model = Ticket
        fields = [
            'id_ticket', 'ticket_title', 'ticket_description', 'ticket_attachments',
            'ticket_service', 'ticket_priority', 'ticket_ans',
            'reporter_user', 'sub_program_name', 'status_id', 'assigned_to',
            'cumplimiento', 'closing_date'
        ]
        read_only_fields = ['id_ticket']

    def create(self, validated_data):
        """Crear ticket con valores iniciales"""
        return Ticket.objects.create(**validated_data)


class TicketUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar tickets"""
    class Meta:
        model = Ticket
        fields = [
            'ticket_title', 'ticket_description', 'ticket_attachments',
            'ticket_priority', 'assigned_to', 'status_id',
            'ticket_closing_code', 'closing_date', 'estimated_closing_date',
            'ticket_service', 'ticket_ans', 'sub_program_name', 'cumplimiento'
        ]

    def update(self, instance, validated_data):
        """Actualizar ticket con lógica personalizada"""
        # Si se está cerrando el ticket, establecer la fecha de cierre
        if validated_data.get('status_id'):
            status = validated_data['status_id']
            if status.status_name.lower() in ['cerrado', 'closed', 'resuelto', 'resolved']:
                validated_data['closing_date'] = timezone.now()
        
        return super().update(instance, validated_data)


class TicketAssignSerializer(serializers.Serializer):
    """Serializer para asignar tickets"""
    assigned_to = serializers.CharField(max_length=45, required=True)

    def validate_assigned_to(self, value):
        """Validar que el usuario asignado exista"""
        if not value:
            raise serializers.ValidationError("El usuario asignado es requerido")
        return value


class TicketStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas de tickets"""
    total_tickets = serializers.IntegerField()
    open_tickets = serializers.IntegerField()
    closed_tickets = serializers.IntegerField()
    in_progress_tickets = serializers.IntegerField()
    by_priority = serializers.DictField()
    by_service = serializers.DictField()
    by_status = serializers.DictField()


class WorkingHoursSerializer(serializers.ModelSerializer):
    """Serializer para horas trabajadas en tickets"""
    class Meta:
        model = WorkingHours
        fields = '__all__'
        read_only_fields = ['id_working_hours']
        

class ProjectDateSerializer(serializers.Serializer):
    ans = serializers.IntegerField()
    date_creation = serializers.CharField(
        help_text="Formato requerido: YYYY-MM-DDTHH:MM:SS",
    )


class TicketReporteDriverSerializer(serializers.Serializer):
    """Serializer para el reporte driver de tickets (por usuario y cliente)"""
    euser_nombre = serializers.CharField()
    network_user = serializers.CharField()
    cliente = serializers.CharField()
    id_ticket = serializers.IntegerField()
    ticket_title = serializers.CharField()
    fecha_creacion = serializers.DateTimeField()
    fecha_cierre = serializers.DateTimeField(allow_null=True)
    fecha_estimada_cierre = serializers.DateTimeField(allow_null=True)
    tiempo_ticket = serializers.CharField()
    tiempo_usuario_cliente = serializers.CharField()
    porcentaje_cliente = serializers.FloatField()
    tiempo_total_usuario = serializers.CharField()
    cumple = serializers.BooleanField(allow_null=True)


class TicketReporteGeneralSerializer(serializers.ModelSerializer):
    """Serializer para el reporte general de tickets"""
    fecha_creacion = serializers.DateTimeField(source='create_at')
    cliente = serializers.SerializerMethodField()
    tipo_servicio = serializers.CharField(source='ticket_service.service_name', default=None)
    tiempo_total = serializers.SerializerMethodField()
    euser_nombre = serializers.SerializerMethodField()
    cumple = serializers.BooleanField(source='cumplimiento')
    fecha_cierre = serializers.DateTimeField(source='closing_date')
    fecha_estimada_cierre = serializers.DateTimeField(source='estimated_closing_date')

    class Meta:
        model = Ticket
        fields = [
            'id_ticket', 'fecha_creacion', 'cliente', 'tipo_servicio',
            'tiempo_total', 'euser_nombre', 'cumple', 'fecha_cierre',
            'fecha_estimada_cierre',
        ]

    def get_cliente(self, obj) -> str | None:
        try:
            return obj.sub_program_name.program_name.client_name.client_name
        except AttributeError:
            return None

    def get_tiempo_total(self, obj) -> str:
        total_seconds = 0
        for rt in obj.reportedtime_set.all():
            t = rt.reported_time
            total_seconds += t.hour * 3600 + t.minute * 60 + t.second
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f'{hours:02}:{minutes:02}:{seconds:02}'

    def get_euser_nombre(self, obj) -> str | None:
        euser = obj.assigned_to
        if not euser:
            return None
        parts = [euser.name]
        if euser.middle_name:
            parts.append(euser.middle_name)
        parts.append(euser.last_name)
        if euser.second_last_name:
            parts.append(euser.second_last_name)
        return ' '.join(parts)
