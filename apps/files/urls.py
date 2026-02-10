from django.urls import path
from .views import FileManagementView, FileDeleteView

urlpatterns = [
    path('upload/files', FileManagementView.as_view(), name='file-management'),
    path('upload/files/<path:filename>', FileDeleteView.as_view(), name='file-delete'),
]
