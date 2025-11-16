# S3 File Upload/Download API

This Django application provides REST API endpoints for uploading and downloading files to/from AWS S3.

## Setup Instructions

### 1. Configure AWS Credentials

Create a `.env` file in the project root directory with your AWS credentials:

```bash
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_STORAGE_BUCKET_NAME=your_s3_bucket_name
AWS_S3_REGION_NAME=us-east-1
```

**Important:** Make sure your S3 bucket exists and you have proper permissions.

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Migrations (if needed)

```bash
python manage.py migrate
```

### 4. Start the Development Server

```bash
python manage.py runserver
```

## API Endpoints

### 1. API Information
**Endpoint:** `GET /s3/`

Returns information about available endpoints.

```bash
curl http://localhost:8000/s3/
```

### 2. Upload File
**Endpoint:** `POST /s3/upload/`

Upload a file to S3.

```bash
curl -X POST -F "file=@/path/to/your/file.txt" http://localhost:8000/s3/upload/
```

**Response:**
```json
{
    "success": true,
    "message": "File uploaded successfully",
    "file_key": "abc123_file.txt",
    "url": "https://your-bucket.s3.us-east-1.amazonaws.com/abc123_file.txt",
    "original_filename": "file.txt"
}
```

### 3. Download File
**Endpoint:** `GET /s3/download/<file_key>/`

Download a file from S3.

```bash
curl -O http://localhost:8000/s3/download/abc123_file.txt/
```

### 4. Delete File
**Endpoint:** `DELETE /s3/delete/<file_key>/`

Delete a file from S3.

```bash
curl -X DELETE http://localhost:8000/s3/delete/abc123_file.txt/
```

**Response:**
```json
{
    "success": true,
    "message": "File deleted successfully",
    "file_key": "abc123_file.txt"
}
```

### 5. List Files
**Endpoint:** `GET /s3/list/`

List files in the S3 bucket.

```bash
# List all files
curl http://localhost:8000/s3/list/

# List files with prefix
curl http://localhost:8000/s3/list/?prefix=images/

# Limit number of results
curl http://localhost:8000/s3/list/?max_keys=50
```

**Response:**
```json
{
    "success": true,
    "files": [
        {
            "key": "abc123_file.txt",
            "size": 1024,
            "last_modified": "2025-11-16T12:00:00+00:00"
        }
    ],
    "count": 1
}
```

## Testing with Python

You can also test the API using Python:

```python
import requests

# Upload a file
with open('test.txt', 'rb') as f:
    response = requests.post('http://localhost:8000/s3/upload/', files={'file': f})
    print(response.json())

# List files
response = requests.get('http://localhost:8000/s3/list/')
print(response.json())

# Download a file
file_key = 'abc123_test.txt'
response = requests.get(f'http://localhost:8000/s3/download/{file_key}/')
with open('downloaded_file.txt', 'wb') as f:
    f.write(response.content)

# Delete a file
response = requests.delete(f'http://localhost:8000/s3/delete/{file_key}/')
print(response.json())
```

## Features

- **File Upload:** Upload files with automatic unique naming to prevent collisions
- **File Download:** Download files by their S3 key
- **File Deletion:** Remove files from S3
- **File Listing:** Browse files in your S3 bucket with optional filtering
- **Error Handling:** Comprehensive error handling with meaningful error messages
- **Logging:** Built-in logging for debugging and monitoring

## Security Notes

1. **CSRF Protection:** The upload and delete endpoints have CSRF exemption for API access. For production, consider implementing proper API authentication.
2. **Credentials:** Never commit your `.env` file or AWS credentials to version control.
3. **IAM Permissions:** Ensure your AWS credentials have the minimum required permissions:
   - `s3:PutObject` for uploads
   - `s3:GetObject` for downloads
   - `s3:DeleteObject` for deletions
   - `s3:ListBucket` for listing files

## File Structure

```
polls/
├── s3_utils.py      # S3 utility functions (boto3 operations)
├── s3_views.py      # API view handlers
└── s3_urls.py       # URL routing for S3 endpoints
```

## Troubleshooting

**Error: "AWS credentials not found"**
- Make sure your `.env` file is in the project root
- Verify that python-dotenv is installed
- Check that your credentials are correctly set in `.env`

**Error: "S3 bucket name not configured"**
- Ensure `AWS_STORAGE_BUCKET_NAME` is set in your `.env` file

**Error: "Access Denied"**
- Verify your AWS credentials have the necessary S3 permissions
- Check that the bucket exists and is in the correct region

**Error: "NoSuchKey" / "File not found"**
- Verify the file_key is correct
- Check that the file exists in your S3 bucket
