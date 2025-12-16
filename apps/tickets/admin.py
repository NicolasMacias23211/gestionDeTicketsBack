from django.contrib import admin
from .models import (
    Client, Service, Role, EUser, TicketPriority, Program, SubProgram,
    ClosingCode, ANS, User, Status, Ticket, ReportedTime, Note
)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['client_name']
    search_fields = ['client_name']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['id_services', 'service_name', 'estimated_solution_time']
    search_fields = ['service_name']
    list_filter = ['estimated_solution_time']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['rol_name', 'description']
    search_fields = ['rol_name']


@admin.register(EUser)
class EUserAdmin(admin.ModelAdmin):
    list_display = ['network_user', 'name', 'last_name', 'email', 'user_client_name', 'rol_name']
    search_fields = ['network_user', 'name', 'last_name', 'email']
    list_filter = ['user_client_name', 'rol_name', 'id_services']


@admin.register(TicketPriority)
class TicketPriorityAdmin(admin.ModelAdmin):
    list_display = ['priority_name', 'priority_description']
    search_fields = ['priority_name']


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ['program_name', 'client_name']
    search_fields = ['program_name']
    list_filter = ['client_name']


@admin.register(SubProgram)
class SubProgramAdmin(admin.ModelAdmin):
    list_display = ['sub_program_name', 'program_name']
    search_fields = ['sub_program_name']
    list_filter = ['program_name']


@admin.register(ClosingCode)
class ClosingCodeAdmin(admin.ModelAdmin):
    list_display = ['id_closing_code', 'closing_code_name', 'closing_code_description']
    search_fields = ['closing_code_name']


@admin.register(ANS)
class ANSAdmin(admin.ModelAdmin):
    list_display = ['id_ans', 'ans_name', 'ans_description']
    search_fields = ['ans_name']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['network_user', 'mail', 'phone']
    search_fields = ['network_user', 'mail']


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ['id_status', 'status_name', 'status_description']
    search_fields = ['status_name']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = [
        'id_ticket', 'ticket_title', 'ticket_priority', 'status_id', 
        'reporter_user', 'assigned_to', 'create_at'
    ]
    search_fields = ['ticket_title', 'ticket_description', 'id_ticket']
    list_filter = [
        'ticket_priority', 'status_id', 'ticket_service', 
        'create_at', 'sub_program_name'
    ]
    date_hierarchy = 'create_at'
    readonly_fields = ['create_at', 'update_at']


@admin.register(ReportedTime)
class ReportedTimeAdmin(admin.ModelAdmin):
    list_display = ['id_reported_times', 'id_ticket', 'date_reported', 'reported_time']
    search_fields = ['id_ticket__ticket_title']
    list_filter = ['date_reported']
    date_hierarchy = 'date_reported'
    readonly_fields = ['create_at', 'update_at']


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['id_note', 'id_ticket', 'visible_to_client', 'create_at']
    search_fields = ['note', 'id_ticket__ticket_title']
    list_filter = ['visible_to_client', 'create_at']
    date_hierarchy = 'create_at'
    readonly_fields = ['create_at', 'update_at']
