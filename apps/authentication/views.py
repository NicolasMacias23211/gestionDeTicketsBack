from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema

from .serializers import (
    LDAPAuthSerializer,
    UserSerializer,
    LogoutSerializer
)


class LDAPAuthView(APIView):
    """
    Vista para autenticación basada en respuesta de API LDAP externa.
    
    Esta vista NO gestiona usuarios ni contraseñas directamente.
    Recibe los datos del LDAP desde otra API y genera tokens JWT.
    
    Flujo:
    1. Otra API valida las credenciales contra LDAP
    2. Esa API envía la respuesta aquí
    3. Creamos/actualizamos el usuario en nuestra BD (solo para registro)
    4. Generamos y retornamos tokens JWT
    """
    permission_classes = (AllowAny,)
    serializer_class = LDAPAuthSerializer
    
    @extend_schema(
        request=LDAPAuthSerializer,
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'message': {'type': 'string'},
                    'user': {
                        'type': 'object',
                        'properties': {
                            'username': {'type': 'string'},
                            'full_name': {'type': 'string'},
                            'email': {'type': 'string'},
                            'position': {'type': 'string'},
                            'document': {'type': 'string'},
                        }
                    },
                    'tokens': {
                        'type': 'object',
                        'properties': {
                            'refresh': {'type': 'string'},
                            'access': {'type': 'string'},
                        }
                    }
                }
            },
            400: {
                'type': 'object',
                'properties': {
                    'general': {'type': 'string'}
                }
            }
        },
        description="Autenticación mediante datos de LDAP. Recibe la respuesta de la API externa de LDAP y genera tokens JWT."
    )
    def post(self, request):
        # Verificar si viene el error de credenciales incorrectas
        if 'general' in request.data:
            return Response(
                {'general': request.data['general']},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = LDAPAuthSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'general': 'Datos de LDAP inválidos o incompletos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            ldap_data = serializer.validated_data['ldap']
            
            # Crear o actualizar usuario (sin contraseña)
            user = serializer.create_or_update_user(ldap_data)
            
            # Generar tokens JWT
            tokens = serializer.generate_tokens(user, ldap_data)
            
            return Response({
                'success': True,
                'message': 'Autenticación exitosa',
                'user': {
                    'username': ldap_data['user'],
                    'full_name': ldap_data['full_name'],
                    'email': ldap_data['mail'],
                    'position': ldap_data['position'],
                    'document': ldap_data['document'],
                },
                'tokens': tokens
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'general': f'Error al procesar autenticación: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LogoutView(APIView):
    """
    Vista para cerrar sesión (blacklist del refresh token)
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = LogoutSerializer

    @extend_schema(
        request=LogoutSerializer,
        responses={
            205: {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'message': {'type': 'string'}
                }
            }
        }
    )
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response({
                    'success': False,
                    'message': 'Se requiere el refresh token'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response({
                'success': True,
                'message': 'Sesión cerrada exitosamente'
            }, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Vista para ver el perfil del usuario autenticado.
    
    Nota: La información del usuario proviene del LDAP y se actualiza
    automáticamente en cada login. Esta vista es solo de consulta.
    """
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        """
        Deshabilitamos la actualización ya que los datos vienen del LDAP
        """
        return Response({
            'success': False,
            'message': 'Los datos del usuario son gestionados por LDAP y no pueden modificarse directamente'
        }, status=status.HTTP_403_FORBIDDEN)
    
    def partial_update(self, request, *args, **kwargs):
        """
        Deshabilitamos la actualización parcial
        """
        return self.update(request, *args, **kwargs)
