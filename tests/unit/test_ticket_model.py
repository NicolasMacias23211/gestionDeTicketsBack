"""
Tests de ejemplo para el modelo Ticket
"""
import pytest
from django.utils import timezone
from apps.tickets.models import (
    Client, Service, Ticket, Status, User, ANS,
    TicketPriority, SubProgram, Program
)


@pytest.mark.django_db
class TestTicketModel:
    """
    Tests para el modelo Ticket
    """
    
    @pytest.fixture
    def setup_data(self):
        """
        Configurar datos de prueba
        """
        # Crear cliente
        client = Client.objects.create(client_name='Test Client')
        
        # Crear programa
        program = Program.objects.create(
            program_name='Test Program',
            client_name=client
        )
        
        # Crear sub-programa
        subprogram = SubProgram.objects.create(
            sub_program_name='Test SubProgram',
            program_name=program
        )
        
        # Crear servicio
        service = Service.objects.create(
            id_services=1,
            service_name='Test Service'
        )
        
        # Crear prioridad
        priority = TicketPriority.objects.create(
            priority_name='Alta',
            priority_description='Prioridad alta'
        )
        
        # Crear ANS
        ans = ANS.objects.create(
            id_ans=1,
            ans_name='ANS Test'
        )
        
        # Crear usuario
        user = User.objects.create(
            network_user='testuser',
            mail='test@example.com'
        )
        
        # Crear estado
        status = Status.objects.create(
            status_id=1,
            status_name='Abierto'
        )
        
        return {
            'service': service,
            'priority': priority,
            'ans': ans,
            'user': user,
            'status': status,
            'subprogram': subprogram
        }
    
    def test_create_ticket(self, setup_data):
        """
        Test de creación de ticket
        """
        ticket = Ticket.objects.create(
            id_ticket=1,
            ticket_title='Test Ticket',
            ticket_description='This is a test ticket',
            ticket_service=setup_data['service'],
            ticket_priority=setup_data['priority'],
            ticket_ans=setup_data['ans'],
            reporter_user=setup_data['user'],
            status_id=setup_data['status'],
            sub_program_name=setup_data['subprogram']
        )
        
        assert ticket.id_ticket == 1
        assert ticket.ticket_title == 'Test Ticket'
        assert str(ticket) == 'Ticket #1 - Test Ticket'
    
    def test_ticket_str_method(self, setup_data):
        """
        Test del método __str__ del ticket
        """
        ticket = Ticket.objects.create(
            id_ticket=2,
            ticket_title='Another Ticket',
            ticket_description='Description',
            ticket_service=setup_data['service'],
            ticket_priority=setup_data['priority'],
            ticket_ans=setup_data['ans'],
            reporter_user=setup_data['user'],
            status_id=setup_data['status'],
            sub_program_name=setup_data['subprogram']
        )
        
        assert str(ticket) == 'Ticket #2 - Another Ticket'
