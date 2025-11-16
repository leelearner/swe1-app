"""
URL configuration for S3 file operations
"""
from django.urls import path
from . import s3_views

app_name = 's3'

urlpatterns = [
    # API info endpoint
    path('', s3_views.api_info, name='api_info'),
    
    # File operations
    path('upload/', s3_views.upload_file, name='upload'),
    path('download/<str:file_key>/', s3_views.download_file, name='download'),
    path('delete/<str:file_key>/', s3_views.delete_file, name='delete'),
    path('list/', s3_views.list_files, name='list'),
]
