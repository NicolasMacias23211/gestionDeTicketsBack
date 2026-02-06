from django.db import models
from django.utils import timezone


class Client(models.Model):
    """
    Modelo para representar los clientes del sistema
    """
    client_name = models.CharField(
        max_length=45,
        primary_key=True,
        db_column='client-name',
        verbose_name='Nombre del Cliente'
    )

    class Meta:
        db_table = 'clients'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return self.client_name


class Service(models.Model):
    """
    Modelo para representar los servicios disponibles
    """
    id_services = models.AutoField(
        primary_key=True,
        db_column='id-services',
        verbose_name='ID del Servicio'
    )
    service_name = models.CharField(
        max_length=45,
        unique=True,
        null=True,
        blank=True,
        db_column='service-name',
        verbose_name='Nombre del Servicio'
    )
    service_description = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_column='service-description',
        verbose_name='Descripción del Servicio'
    )
    estimated_solution_time = models.TimeField(
        null=True,
        blank=True,
        db_column='estimated-solution-time',
        verbose_name='Tiempo Estimado de Solución'
    )

    class Meta:
        db_table = 'services'
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'

    def __str__(self):
        return self.service_name or f'Servicio {self.id_services}'


class Role(models.Model):
    """
    Modelo para representar los roles de usuarios en el sistema
    """
    rol_name = models.CharField(
        max_length=45,
        primary_key=True,
        db_column='rol-name',
        verbose_name='Nombre del Rol'
    )
    description = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Descripción'
    )
    icon = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Icono'
    )

    class Meta:
        db_table = 'roles'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.rol_name


class EUser(models.Model):
    """
    Modelo para representar usuarios empresariales (e-users)
    """
    network_user = models.CharField(
        max_length=45,
        primary_key=True,
        db_column='network-user',
        verbose_name='Usuario de Red'
    )
    name = models.CharField(
        max_length=45,
        verbose_name='Nombre'
    )
    middle_name = models.CharField(
        max_length=45,
        null=True,
        blank=True,
        db_column='middle-name',
        verbose_name='Segundo Nombre'
    )
    last_name = models.CharField(
        max_length=45,
        db_column='last-name',
        verbose_name='Apellido Paterno'
    )
    second_last_name = models.CharField(
        max_length=45,
        null=True,
        blank=True,
        db_column='second-last-name',
        verbose_name='Apellido Materno'
    )
    email = models.CharField(
        max_length=45,
        null=True,
        blank=True,
        verbose_name='Correo Electrónico'
    )
    phone = models.CharField(
        max_length=45,
        null=True,
        blank=True,
        verbose_name='Teléfono'
    )
    user_client_name = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        db_column='user-client-name',
        verbose_name='Cliente'
    )
    id_services = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        db_column='id-services',
        verbose_name='Servicio'
    )
    rol_name = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        db_column='rol-name',
        verbose_name='Rol'
    )

    class Meta:
        db_table = 'e-users'
        verbose_name = 'Usuario Empresarial'
        verbose_name_plural = 'Usuarios Empresariales'

    def __str__(self):
        return f'{self.name} {self.last_name} ({self.network_user})'


class TicketPriority(models.Model):
    """
    Modelo para representar las prioridades de tickets
    """
    priority_name = models.CharField(
        max_length=45,
        primary_key=True,
        db_column='priority-name',
        verbose_name='Nombre de la Prioridad'
    )
    priority_description = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_column='priority-description',
        verbose_name='Descripción de la Prioridad'
    )

    class Meta:
        db_table = 'ticket-priority'
        verbose_name = 'Prioridad de Ticket'
        verbose_name_plural = 'Prioridades de Tickets'

    def __str__(self):
        return self.priority_name


class Program(models.Model):
    """
    Modelo para representar los programas asociados a clientes
    """
    program_name = models.CharField(
        max_length=45,
        primary_key=True,
        db_column='program-name',
        verbose_name='Nombre del Programa'
    )
    client_name = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        db_column='client-name',
        verbose_name='Cliente'
    )

    class Meta:
        db_table = 'programs'
        verbose_name = 'Programa'
        verbose_name_plural = 'Programas'

    def __str__(self):
        return self.program_name


class SubProgram(models.Model):
    """
    Modelo para representar los sub-programas asociados a programas
    """
    sub_program_name = models.CharField(
        max_length=45,
        primary_key=True,
        db_column='sub-program-name',
        verbose_name='Nombre del Sub-programa'
    )
    program_name = models.ForeignKey(
        Program,
        on_delete=models.PROTECT,
        db_column='program-name',
        verbose_name='Programa'
    )

    class Meta:
        db_table = 'sub-programs'
        verbose_name = 'Sub-programa'
        verbose_name_plural = 'Sub-programas'

    def __str__(self):
        return self.sub_program_name


class ClosingCode(models.Model):
    """
    Modelo para representar los códigos de cierre
    """
    id_closing_code = models.AutoField(
        primary_key=True,
        db_column='id-closing-code',
        verbose_name='ID del Código de Cierre'
    )
    closing_code_name = models.CharField(
        max_length=45,
        unique=True,
        null=True,
        blank=True,
        db_column='closing-code-name',
        verbose_name='Nombre del Código de Cierre'
    )
    closing_code_description = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_column='closing-code-description',
        verbose_name='Descripción del Código de Cierre'
    )

    class Meta:
        db_table = 'closing-codes'
        verbose_name = 'Código de Cierre'
        verbose_name_plural = 'Códigos de Cierre'

    def __str__(self):
        return self.closing_code_name or f'Código {self.id_closing_code}'


class ANS(models.Model):
    """
    Modelo para representar los ANS (Acuerdo de Nivel de Servicio)
    """
    id_ans = models.AutoField(
        primary_key=True,
        db_column='id-ans',
        verbose_name='ID del ANS'
    )
    ans_name = models.CharField(
        max_length=45,
        db_column='ans-name',
        verbose_name='Nombre del ANS'
    )
    ans_description = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_column='ans-description',
        verbose_name='Descripción del ANS'
    )

    class Meta:
        db_table = 'ans'
        verbose_name = 'ANS'
        verbose_name_plural = 'ANS'

    def __str__(self):
        return self.ans_name


class User(models.Model):
    """
    Modelo para representar usuarios básicos del sistema
    """
    network_user = models.CharField(
        max_length=45,
        primary_key=True,
        db_column='network-user',
        verbose_name='Usuario de Red'
    )
    full_name = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        db_column='full-name',
        verbose_name='Nombre Completo'
    )
    mail = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='Correo'
    )
    phone = models.CharField(
        max_length=45,
        null=True,
        blank=True,
        verbose_name='Teléfono'
    )

    class Meta:
        db_table = 'users'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.network_user


class Status(models.Model):
    """
    Modelo para representar los estados de los tickets
    """
    id_status = models.AutoField(
        primary_key=True,
        db_column='id-status',
        verbose_name='ID del Estado'
    )
    status_name = models.CharField(
        max_length=45,
        db_column='status-name',
        verbose_name='Nombre del Estado'
    )
    status_description = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_column='status-description',
        verbose_name='Descripción del Estado'
    )
    is_backlog = models.BooleanField(
        default=False,
        db_column='is-backlog',
        verbose_name='Es Backlog'
    )

    class Meta:
        db_table = 'status'
        verbose_name = 'Estado'
        verbose_name_plural = 'Estados'

    def __str__(self):
        return self.status_name


class Ticket(models.Model):
    """
    Modelo principal para representar los tickets del sistema
    """
    id_ticket = models.AutoField(
        primary_key=True,
        db_column='id-ticket',
        verbose_name='ID del Ticket'
    )
    ticket_title = models.CharField(
        max_length=45,
        db_column='ticket-title',
        verbose_name='Título del Ticket'
    )
    ticket_description = models.CharField(
        max_length=250,
        db_column='ticket-description',
        verbose_name='Descripción del Ticket'
    )
    ticket_attachments = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        db_column='ticket-attachments',
        verbose_name='Adjuntos del Ticket'
    )
    ticket_service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        db_column='ticket-service',
        verbose_name='Servicio'
    )
    ticket_priority = models.ForeignKey(
        TicketPriority,
        on_delete=models.PROTECT,
        db_column='ticket-priority',
        verbose_name='Prioridad'
    )
    ticket_closing_code = models.ForeignKey(
        ClosingCode,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column='ticket--closing-code',
        verbose_name='Código de Cierre'
    )
    ticket_ans = models.ForeignKey(
        ANS,
        on_delete=models.PROTECT,
        db_column='ticket-ans',
        verbose_name='ANS'
    )
    reporter_user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        db_column='reporter-user',
        verbose_name='Usuario Reportador'
    )
    create_at = models.DateTimeField(
        default=timezone.now,
        db_column='create-at',
        verbose_name='Fecha de Creación'
    )
    update_at = models.DateTimeField(
        auto_now=True,
        db_column='update-at',
        verbose_name='Fecha de Actualización'
    )
    assigned_to = models.ForeignKey(
        EUser,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column='assigned-to',
        verbose_name='Asignado a',
        related_name='assigned_tickets'
    )
    closing_date = models.DateTimeField(
        null=True,
        blank=True,
        db_column='closing date',
        verbose_name='Fecha de Cierre'
    )
    estimated_closing_date = models.DateTimeField(
        null=True,
        blank=True,
        db_column='estimated-closing-date',
        verbose_name='Fecha Estimada de Cierre'
    )
    status_id = models.ForeignKey(
        Status,
        on_delete=models.PROTECT,
        db_column='status-id',
        verbose_name='Estado'
    )
    sub_program_name = models.ForeignKey(
        SubProgram,
        on_delete=models.PROTECT,
        db_column='sub-program-name',
        verbose_name='Sub-programa'
    )

    class Meta:
        db_table = 'tickets'
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'

    def __str__(self):
        return f'Ticket #{self.id_ticket} - {self.ticket_title}'


class ReportedTime(models.Model):
    """
    Modelo para representar los tiempos reportados en tickets
    """
    id_reported_times = models.AutoField(
        primary_key=True,
        db_column='id-reported-times',
        verbose_name='ID del Tiempo Reportado'
    )
    date_reported = models.DateTimeField(
        db_column='date-reported',
        verbose_name='Fecha Reportada'
    )
    reported_time = models.TimeField(
        db_column='reported-time',
        verbose_name='Tiempo Reportado'
    )
    id_ticket = models.ForeignKey(
        Ticket,
        on_delete=models.PROTECT,
        db_column='id-ticket',
        verbose_name='Ticket'
    )
    network_user = models.ForeignKey(
        EUser,
        on_delete=models.PROTECT,
        db_column='network-user',
        verbose_name='Usuario de Red',
        help_text='Usuario que reporta el tiempo',
        null=True,
        blank=True
    )
    create_at = models.DateTimeField(
        default=timezone.now,
        db_column='create-at',
        verbose_name='Fecha de Creación'
    )
    update_at = models.DateTimeField(
        auto_now=True,
        db_column='update-at',
        verbose_name='Fecha de Actualización'
    )

    class Meta:
        db_table = 'reported-times'
        verbose_name = 'Tiempo Reportado'
        verbose_name_plural = 'Tiempos Reportados'

    def __str__(self):
        return f'Tiempo #{self.id_reported_times} - Ticket {self.id_ticket.id_ticket}'


class Note(models.Model):
    """
    Modelo para representar las notas asociadas a tickets
    """
    id_note = models.AutoField(
        primary_key=True,
        db_column='id-note',
        verbose_name='ID de la Nota'
    )
    note = models.TextField(
        verbose_name='Nota'
    )
    visible_to_client = models.BooleanField(
        default=False,
        db_column='visible-to-client',
        verbose_name='Visible para el Cliente'
    )
    network_user = models.ForeignKey(
        EUser,
        on_delete=models.PROTECT,
        db_column='network-user',
        verbose_name='Usuario',
        help_text='Usuario que escribe la nota',
        null=True,
        blank=True
    )
    create_at = models.DateTimeField(
        default=timezone.now,
        db_column='create-at',
        verbose_name='Fecha de Creación'
    )
    update_at = models.DateTimeField(
        auto_now=True,
        db_column='update-at',
        verbose_name='Fecha de Actualización'
    )
    id_ticket = models.ForeignKey(
        Ticket,
        on_delete=models.PROTECT,
        db_column='id-ticket',
        verbose_name='Ticket'
    )

    class Meta:
        db_table = 'notes'
        verbose_name = 'Nota'
        verbose_name_plural = 'Notas'

    def __str__(self):
        return f'Nota #{self.id_note} - Ticket {self.id_ticket.id_ticket}'

class WorkingHours(models.Model):
    id_working_hours = models.AutoField(
        primary_key=True,
        db_column='id-working-hours',
        verbose_name='ID de Horas Laborales'
    )
    week_day = models.CharField(
        max_length=15,
        db_column='week-day',
        verbose_name='Día de la Semana',
        unique=True
    )
    start_time = models.TimeField(
        db_column='start-time',
        verbose_name='Hora de Inicio'
    )
    end_time = models.TimeField(
        db_column='end-time',
        verbose_name='Hora de Fin'
    )
    
    class Meta:
        db_table = 'working-hours'
        verbose_name = 'Horas Laborales'
        verbose_name_plural = 'Horas Laborales'

    def __str__(self):
        return f'Horas Laborales #{self.id_working_hours} - {self.week_day}'