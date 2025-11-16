"""
Views for S3 file upload and download operations
"""
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .s3_utils import (
    upload_file_to_s3,
    download_file_from_s3,
    delete_file_from_s3,
    list_files_in_s3
)


@csrf_exempt
@require_http_methods(["POST"])
def upload_file(request):
    """
    Upload a file to S3
    
    Expects multipart/form-data with a file field
    
    Example usage with curl:
    curl -X POST -F "file=@/path/to/file.txt" http://localhost:8000/s3/upload/
    
    Returns:
        JSON response with upload status and file details
    """
    if 'file' not in request.FILES:
        return JsonResponse({
            'success': False,
            'error': 'No file provided. Please include a file in the request.'
        }, status=400)
    
    uploaded_file = request.FILES['file']
    
    # Get content type
    content_type = uploaded_file.content_type
    
    # Upload to S3
    result = upload_file_to_s3(
        uploaded_file.file,
        uploaded_file.name,
        content_type
    )
    
    if result['success']:
        return JsonResponse({
            'success': True,
            'message': 'File uploaded successfully',
            'file_key': result['file_key'],
            'url': result['url'],
            'original_filename': result['original_filename']
        }, status=201)
    else:
        return JsonResponse({
            'success': False,
            'error': result.get('error', 'Unknown error occurred')
        }, status=500)


@require_http_methods(["GET"])
def download_file(request, file_key):
    """
    Download a file from S3
    
    Args:
        file_key: The S3 key (filename) of the file to download
    
    Example usage:
    curl -O http://localhost:8000/s3/download/<file_key>/
    
    Returns:
        File content as downloadable response
    """
    result = download_file_from_s3(file_key)
    
    if result['success']:
        response = HttpResponse(
            result['file_content'],
            content_type=result['content_type']
        )
        # Extract original filename from file_key (remove UUID prefix)
        filename = file_key.split('_', 1)[1] if '_' in file_key else file_key
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    else:
        return JsonResponse({
            'success': False,
            'error': result.get('error', 'File not found')
        }, status=404)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_file(request, file_key):
    """
    Delete a file from S3
    
    Args:
        file_key: The S3 key (filename) of the file to delete
    
    Example usage with curl:
    curl -X DELETE http://localhost:8000/s3/delete/<file_key>/
    
    Returns:
        JSON response with deletion status
    """
    result = delete_file_from_s3(file_key)
    
    if result['success']:
        return JsonResponse({
            'success': True,
            'message': 'File deleted successfully',
            'file_key': result['file_key']
        }, status=200)
    else:
        return JsonResponse({
            'success': False,
            'error': result.get('error', 'Unknown error occurred')
        }, status=500)


@require_http_methods(["GET"])
def list_files(request):
    """
    List files in S3 bucket
    
    Query parameters:
        prefix: Filter files by prefix (optional)
        max_keys: Maximum number of files to return (optional, default: 100)
    
    Example usage:
    curl http://localhost:8000/s3/list/
    curl http://localhost:8000/s3/list/?prefix=images/&max_keys=50
    
    Returns:
        JSON response with list of files
    """
    prefix = request.GET.get('prefix', '')
    max_keys = int(request.GET.get('max_keys', 100))
    
    result = list_files_in_s3(prefix, max_keys)
    
    if result['success']:
        return JsonResponse({
            'success': True,
            'files': result['files'],
            'count': result['count']
        }, status=200)
    else:
        return JsonResponse({
            'success': False,
            'error': result.get('error', 'Unknown error occurred')
        }, status=500)


@require_http_methods(["GET"])
def api_info(request):
    """
    API information endpoint
    
    Returns documentation about available endpoints
    """
    info = {
        'name': 'S3 File Management API',
        'version': '1.0',
        'endpoints': {
            'upload': {
                'url': '/s3/upload/',
                'method': 'POST',
                'description': 'Upload a file to S3',
                'example': 'curl -X POST -F "file=@/path/to/file.txt" http://localhost:8000/s3/upload/'
            },
            'download': {
                'url': '/s3/download/<file_key>/',
                'method': 'GET',
                'description': 'Download a file from S3',
                'example': 'curl -O http://localhost:8000/s3/download/<file_key>/'
            },
            'delete': {
                'url': '/s3/delete/<file_key>/',
                'method': 'DELETE',
                'description': 'Delete a file from S3',
                'example': 'curl -X DELETE http://localhost:8000/s3/delete/<file_key>/'
            },
            'list': {
                'url': '/s3/list/',
                'method': 'GET',
                'description': 'List files in S3 bucket',
                'parameters': {
                    'prefix': 'Filter files by prefix (optional)',
                    'max_keys': 'Maximum number of files to return (optional, default: 100)'
                },
                'example': 'curl http://localhost:8000/s3/list/?prefix=images/&max_keys=50'
            }
        }
    }
    return JsonResponse(info, status=200)
