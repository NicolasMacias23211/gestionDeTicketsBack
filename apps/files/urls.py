from django.urls import path
from .views import FileUploadView, FileRetrieveView, FileDeleteView

urlpatterns = [
    path('upload/files', FileUploadView.as_view(), name='file-upload'),
    path('upload/files/<path:filename>', FileDeleteView.as_view(), name='file-delete'),
    path('upload/files', FileRetrieveView.as_view(), name='file-retrieve'),
]
