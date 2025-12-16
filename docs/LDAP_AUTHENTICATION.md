# Autenticación basada en LDAP

## 📋 Descripción

Este sistema **NO gestiona contraseñas directamente**. La autenticación se realiza mediante una API externa que valida las credenciales contra LDAP y nos envía los datos del usuario.

## 🔄 Flujo de Autenticación

```
1. Usuario ingresa credenciales en el frontend
2. Frontend envía credenciales a la API de LDAP externa
3. API externa valida contra LDAP
4. Si es válido: API externa envía respuesta a nuestro endpoint /api/auth/login/
5. Nuestro sistema:
   - Crea/actualiza el usuario en la BD (solo para registro)
   - Genera tokens JWT con los datos del LDAP
   - Retorna tokens al frontend
6. Si es inválido: API externa envía error {"general": "Usuario o password incorrectos"}
```

## 📥 Endpoint: POST /api/auth/login/

### Respuesta exitosa de la API externa de LDAP:

```json
{
    "ldap": {
        "user": "nmaciduq",
        "full_name": "NICOLAS  MACIAS DUQUE",
        "position": "ARQUITECTO DE AVA",
        "mail": "nmaciduq@experiencia.emtelco.com.co",
        "document": "1000748711"
    }
}
```

### Respuesta de error (credenciales incorrectas):

```json
{
    "general": "Usuario o password incorrectos"
}
```

### Respuesta de nuestro sistema (éxito):

```json
{
    "success": true,
    "message": "Autenticación exitosa",
    "user": {
        "username": "nmaciduq",
        "full_name": "NICOLAS  MACIAS DUQUE",
        "email": "nmaciduq@experiencia.emtelco.com.co",
        "position": "ARQUITECTO DE AVA",
        "document": "1000748711"
    },
    "tokens": {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
}
```

## 🔑 Tokens JWT

Los tokens incluyen la información del LDAP:

```json
{
    "token_type": "access",
    "exp": 1234567890,
    "iat": 1234567890,
    "jti": "...",
    "user_id": 1,
    "username": "nmaciduq",
    "email": "nmaciduq@experiencia.emtelco.com.co",
    "full_name": "NICOLAS  MACIAS DUQUE",
    "position": "ARQUITECTO DE AVA",
    "document": "1000748711"
}
```

## 👤 Gestión de Usuarios

### Usuario Django (`auth_user`)
- **Propósito**: Registro interno para compatibilidad con Django
- **Contraseña**: Marcada como "unusable" (sin contraseña)
- **Actualización**: Se actualiza automáticamente en cada login
- **Campos**: username, email, first_name, last_name

### Usuario E-SEUS (`e_users`)
- **Propósito**: Vinculación con el sistema de tickets
- **Gestión**: Manual según roles (gestiona/envía tickets)

### Usuario Tickets (`users`)
- **Propósito**: Registro de actividad en tickets
- **Gestión**: Automática al crear/gestionar tickets

## ✅ Endpoints Disponibles

| Endpoint | Método | Descripción | Auth |
|----------|--------|-------------|------|
| `/api/auth/login/` | POST | Recibe datos de LDAP y genera JWT | No |
| `/api/auth/token/refresh/` | POST | Refresca el access token | No |
| `/api/auth/logout/` | POST | Invalida el refresh token | Sí |
| `/api/auth/profile/` | GET | Consulta perfil del usuario | Sí |

## 🔒 Seguridad

1. **No almacenamos contraseñas**: Los usuarios tienen contraseñas "unusable"
2. **Validación externa**: La API de LDAP valida las credenciales
3. **JWT con claims**: Los tokens incluyen toda la info del usuario
4. **Blacklist**: Los refresh tokens se invalidan en logout
5. **Actualización automática**: Los datos del usuario se sincronizan en cada login
