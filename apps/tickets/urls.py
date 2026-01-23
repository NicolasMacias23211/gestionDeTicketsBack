from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ClientViewSet, ServiceViewSet, RoleViewSet, EUserViewSet,
    TicketPriorityViewSet, ProgramViewSet, SubProgramViewSet,
    ClosingCodeViewSet, ANSViewSet, UserViewSet, StatusViewSet,
    TicketViewSet, ReportedTimeViewSet, NoteViewSet, WorkingHoursViewSet
)

app_name = 'tickets'

# Crear el router y registrar los viewsets
router = DefaultRouter()
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'eusers', EUserViewSet, basename='euser')
router.register(r'priorities', TicketPriorityViewSet, basename='priority')
router.register(r'programs', ProgramViewSet, basename='program')
router.register(r'subprograms', SubProgramViewSet, basename='subprogram')
router.register(r'closing-codes', ClosingCodeViewSet, basename='closing-code')
router.register(r'ans', ANSViewSet, basename='ans')
router.register(r'users', UserViewSet, basename='user')
router.register(r'status', StatusViewSet, basename='status')
router.register(r'tickets', TicketViewSet, basename='ticket')
router.register(r'reported-times', ReportedTimeViewSet, basename='reported-time')
router.register(r'notes', NoteViewSet, basename='note')
router.register(r'working-hours', WorkingHoursViewSet, basename='working-hours')

urlpatterns = [
    path('', include(router.urls)),
]
