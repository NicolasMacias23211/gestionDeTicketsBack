from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field


class FileUploadSerializer(serializers.Serializer):
    """Serializer para la subida de archivos"""
    files = serializers.FileField(
        help_text="Archivo a subir"
    )
    ticketId = serializers.IntegerField(
        required=False,
        help_text="ID del ticket asociado (opcional)"
    )


class FileUploadResponseSerializer(serializers.Serializer):
    """Serializer para la respuesta de subida de archivos"""
    filenames = serializers.ListField(
        child=serializers.CharField(),
        help_text="Lista de nombres de archivos guardados"
    )


class FileDeleteResponseSerializer(serializers.Serializer):
    """Serializer para la respuesta de eliminación de archivos"""
    message = serializers.CharField(
        help_text="Mensaje de confirmación"
    )


class ErrorResponseSerializer(serializers.Serializer):
    """Serializer para respuestas de error"""
    message = serializers.CharField(
        help_text="Mensaje de error"
    )
