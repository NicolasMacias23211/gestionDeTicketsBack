from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken


class LDAPAuthSerializer(serializers.Serializer):
    """
    Serializer para recibir los datos del LDAP desde la API externa
    """
    ldap = serializers.DictField(
        child=serializers.CharField(),
        help_text="Datos del usuario desde LDAP"
    )
    
    def validate_ldap(self, value):
        """
        Valida que el diccionario LDAP contenga los campos requeridos
        """
        required_fields = ['user', 'full_name', 'position', 'mail', 'document']
        missing_fields = [field for field in required_fields if field not in value]
        
        if missing_fields:
            raise serializers.ValidationError(
                f"Faltan campos requeridos en ldap: {', '.join(missing_fields)}"
            )
        
        return value
    
    def create_or_update_user(self, ldap_data):
        """
        Crea o actualiza el usuario en base a los datos del LDAP
        No gestiona contraseñas, solo mantiene registro del usuario
        """
        username = ldap_data['user']
        email = ldap_data['mail']
        
        # Extraer nombre y apellido del full_name
        full_name_parts = ldap_data['full_name'].strip().split()
        first_name = full_name_parts[0] if full_name_parts else ''
        last_name = ' '.join(full_name_parts[1:]) if len(full_name_parts) > 1 else ''
        
        # Buscar o crear el usuario (sin contraseña)
        user, created = User.objects.update_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
            }
        )
        
        # No establecemos contraseña ya que no la gestionamos
        if created:
            user.set_unusable_password()
            user.save()
        
        return user
    
    def generate_tokens(self, user, ldap_data):
        """
        Genera los tokens JWT con información del LDAP
        """
        refresh = RefreshToken.for_user(user)
        
        # Agregar información del LDAP al token
        refresh['username'] = ldap_data['user']
        refresh['email'] = ldap_data['mail']
        refresh['full_name'] = ldap_data['full_name']
        refresh['position'] = ldap_data['position']
        refresh['document'] = ldap_data['document']
        
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo de Usuario
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
        read_only_fields = ('id', 'date_joined')


class LogoutSerializer(serializers.Serializer):
    """
    Serializer para el endpoint de logout
    """
    refresh_token = serializers.CharField(
        required=True,
        help_text="Refresh token a invalidar"
    )
