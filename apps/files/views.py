import os
from pathlib import Path
from django.conf import settings
from django.http import FileResponse, JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from .serializers import (
    FileUploadSerializer,
    FileUploadResponseSerializer,
    FileDeleteResponseSerializer,
    ErrorResponseSerializer
)


class FileManagementView(APIView):
    """
    Vista para gestionar archivos: subir (POST) y obtener (GET).
    Los archivos se guardan en la carpeta 'uploads' del proyecto.
    """
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Subir archivo",
        description="Sube un archivo al servidor y lo guarda localmente. "
                    "El archivo se recibe uno por uno.",
        request=FileUploadSerializer,
        responses={
            200: FileUploadResponseSerializer,
            400: ErrorResponseSerializer,
        },
        examples=[
            OpenApiExample(
                'Respuesta exitosa',
                value={'filenames': ['1738095123456_abc123_documento.pdf']},
                response_only=True,
                status_codes=['200']
            ),
        ]
    )
    def post(self, request):
        """Subir un archivo al servidor"""
        try:
            # Obtener el archivo del request
            file = request.FILES.get('files')
            ticket_id = request.data.get('ticketId')

            if not file:
                return JsonResponse(
                    {'message': 'No se proporcionó ningún archivo'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Crear la carpeta de uploads si no existe
            upload_dir = Path(settings.UPLOAD_ROOT)
            upload_dir.mkdir(parents=True, exist_ok=True)

            # Si hay ticketId, crear subcarpeta
            if ticket_id:
                upload_dir = upload_dir / f"ticket_{ticket_id}"
                upload_dir.mkdir(parents=True, exist_ok=True)

            # Guardar el archivo con el nombre que viene del frontend
            file_path = upload_dir / file.name
            
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            # Construir el nombre relativo del archivo para retornar
            if ticket_id:
                relative_filename = f"ticket_{ticket_id}/{file.name}"
            else:
                relative_filename = file.name

            return JsonResponse(
                {'filenames': [relative_filename]},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return JsonResponse(
                {'message': f'Error al subir el archivo: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Obtener archivo(s)",
        description="Obtiene uno o varios archivos del servidor. "
                    "Puede recibir un nombre de archivo mediante el parámetro 'filename' "
                    "o múltiples nombres mediante el parámetro 'filenames' (separados por coma).",
        parameters=[
            OpenApiParameter(
                name='filename',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Nombre de un archivo específico',
                required=False,
            ),
            OpenApiParameter(
                name='filenames',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Nombres de archivos separados por coma',
                required=False,
            ),
        ],
        responses={
            200: OpenApiTypes.BINARY,
            400: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        }
    )
    def get(self, request):
        """Obtener archivo(s) del servidor"""
        try:
            # Obtener parámetros
            filename = request.query_params.get('filename')
            filenames = request.query_params.get('filenames')

            if not filename and not filenames:
                return JsonResponse(
                    {'message': 'Debe proporcionar filename o filenames'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Si es un solo archivo
            if filename:
                file_path = Path(settings.UPLOAD_ROOT) / filename
                
                if not file_path.exists():
                    return JsonResponse(
                        {'message': f'El archivo {filename} no existe'},
                        status=status.HTTP_404_NOT_FOUND
                    )

                # Retornar el archivo
                return FileResponse(
                    open(file_path, 'rb'),
                    as_attachment=True,
                    filename=file_path.name
                )

            # Si son múltiples archivos
            if filenames:
                file_list = [f.strip() for f in filenames.split(',')]
                
                # Para múltiples archivos, podríamos crear un ZIP
                # Por ahora, retornamos el primer archivo o un error si no existe
                if len(file_list) == 1:
                    file_path = Path(settings.UPLOAD_ROOT) / file_list[0]
                    
                    if not file_path.exists():
                        return JsonResponse(
                            {'message': f'El archivo {file_list[0]} no existe'},
                            status=status.HTTP_404_NOT_FOUND
                        )

                    return FileResponse(
                        open(file_path, 'rb'),
                        as_attachment=True,
                        filename=file_path.name
                    )
                else:
                    # Para múltiples archivos, crear un ZIP
                    import zipfile
                    from io import BytesIO
                    
                    buffer = BytesIO()
                    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                        for filename in file_list:
                            file_path = Path(settings.UPLOAD_ROOT) / filename
                            if file_path.exists():
                                zip_file.write(file_path, arcname=file_path.name)
                    
                    buffer.seek(0)
                    return FileResponse(
                        buffer,
                        as_attachment=True,
                        filename='archivos.zip',
                        content_type='application/zip'
                    )

        except Exception as e:
            return JsonResponse(
                {'message': f'Error al obtener archivo(s): {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FileDeleteView(APIView):
    """
    Vista para eliminar archivos del servidor.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Eliminar archivo",
        description="Elimina un archivo del servidor",
        parameters=[
            OpenApiParameter(
                name='filename',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description='Nombre del archivo a eliminar',
                required=True,
            ),
        ],
        responses={
            200: FileDeleteResponseSerializer,
            404: ErrorResponseSerializer,
        },
        examples=[
            OpenApiExample(
                'Respuesta exitosa',
                value={'message': 'Archivo eliminado exitosamente'},
                response_only=True,
                status_codes=['200']
            ),
        ]
    )
    def delete(self, request, filename):
        """Eliminar un archivo del servidor"""
        try:
            # Construir la ruta del archivo
            file_path = Path(settings.UPLOAD_ROOT) / filename

            if not file_path.exists():
                return JsonResponse(
                    {'message': f'El archivo {filename} no existe'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Eliminar el archivo
            os.remove(file_path)

            # Si está en una subcarpeta de ticket y quedó vacía, eliminarla
            parent_dir = file_path.parent
            if parent_dir != Path(settings.UPLOAD_ROOT) and not any(parent_dir.iterdir()):
                parent_dir.rmdir()

            return JsonResponse(
                {'message': 'Archivo eliminado exitosamente'},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return JsonResponse(
                {'message': f'Error al eliminar el archivo: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
