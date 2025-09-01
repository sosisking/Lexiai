import os
import uuid
import boto3
from flask import current_app
from werkzeug.utils import secure_filename

class StorageService:
    """Service for handling file storage operations."""
    
    @staticmethod
    def get_storage_type():
        """Get the storage type from configuration."""
        return current_app.config.get('STORAGE_TYPE', 'local')
    
    @staticmethod
    def save_file(file, file_type=None):
        """
        Save a file to storage.
        
        Args:
            file: The file object to save
            file_type (str, optional): The file type. Defaults to None.
            
        Returns:
            tuple: (str, int) - (file_path, file_size)
        """
        storage_type = StorageService.get_storage_type()
        
        if storage_type == 's3':
            return StorageService._save_to_s3(file, file_type)
        else:
            return StorageService._save_to_local(file, file_type)
    
    @staticmethod
    def _save_to_local(file, file_type=None):
        """
        Save a file to local storage.
        
        Args:
            file: The file object to save
            file_type (str, optional): The file type. Defaults to None.
            
        Returns:
            tuple: (str, int) - (file_path, file_size)
        """
        # Create upload directory if it doesn't exist
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Generate a secure filename
        original_filename = secure_filename(file.filename)
        ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
        
        if not ext and file_type:
            ext = file_type.lower()
        
        # Generate a unique filename
        unique_filename = f"{uuid.uuid4().hex}.{ext}"
        file_path = os.path.join(upload_folder, unique_filename)
        
        # Save the file
        file.save(file_path)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        return file_path, file_size
    
    @staticmethod
    def _save_to_s3(file, file_type=None):
        """
        Save a file to S3 storage.
        
        Args:
            file: The file object to save
            file_type (str, optional): The file type. Defaults to None.
            
        Returns:
            tuple: (str, int) - (file_path, file_size)
        """
        # Get S3 configuration
        s3_bucket = current_app.config.get('S3_BUCKET')
        s3_region = current_app.config.get('S3_REGION', 'us-east-1')
        
        # Create S3 client
        s3 = boto3.client(
            's3',
            region_name=s3_region,
            aws_access_key_id=current_app.config.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=current_app.config.get('AWS_SECRET_ACCESS_KEY')
        )
        
        # Generate a secure filename
        original_filename = secure_filename(file.filename)
        ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
        
        if not ext and file_type:
            ext = file_type.lower()
        
        # Generate a unique filename
        unique_filename = f"{uuid.uuid4().hex}.{ext}"
        
        # Upload to S3
        file_size = file.tell()
        file.seek(0)
        s3.upload_fileobj(file, s3_bucket, unique_filename)
        
        # Return S3 path
        file_path = f"s3://{s3_bucket}/{unique_filename}"
        
        return file_path, file_size
    
    @staticmethod
    def get_file(file_path):
        """
        Get a file from storage.
        
        Args:
            file_path (str): The file path
            
        Returns:
            tuple: (file_content, file_type)
        """
        if file_path.startswith('s3://'):
            return StorageService._get_from_s3(file_path)
        else:
            return StorageService._get_from_local(file_path)
    
    @staticmethod
    def _get_from_local(file_path):
        """
        Get a file from local storage.
        
        Args:
            file_path (str): The file path
            
        Returns:
            tuple: (file_content, file_type)
        """
        if not os.path.exists(file_path):
            return None, None
        
        # Get file type from extension
        ext = file_path.rsplit('.', 1)[1].lower() if '.' in file_path else ''
        file_type = ext
        
        # Read file content
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        return file_content, file_type
    
    @staticmethod
    def _get_from_s3(file_path):
        """
        Get a file from S3 storage.
        
        Args:
            file_path (str): The file path
            
        Returns:
            tuple: (file_content, file_type)
        """
        # Parse S3 path
        s3_path = file_path.replace('s3://', '')
        bucket_name, object_key = s3_path.split('/', 1)
        
        # Create S3 client
        s3 = boto3.client(
            's3',
            region_name=current_app.config.get('S3_REGION', 'us-east-1'),
            aws_access_key_id=current_app.config.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=current_app.config.get('AWS_SECRET_ACCESS_KEY')
        )
        
        # Get file from S3
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        file_content = response['Body'].read()
        
        # Get file type from extension
        ext = object_key.rsplit('.', 1)[1].lower() if '.' in object_key else ''
        file_type = ext
        
        return file_content, file_type
    
    @staticmethod
    def delete_file(file_path):
        """
        Delete a file from storage.
        
        Args:
            file_path (str): The file path
            
        Returns:
            bool: True if successful, False otherwise
        """
        if file_path.startswith('s3://'):
            return StorageService._delete_from_s3(file_path)
        else:
            return StorageService._delete_from_local(file_path)
    
    @staticmethod
    def _delete_from_local(file_path):
        """
        Delete a file from local storage.
        
        Args:
            file_path (str): The file path
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not os.path.exists(file_path):
            return False
        
        try:
            os.remove(file_path)
            return True
        except Exception as e:
            current_app.logger.error(f"Error deleting file: {str(e)}")
            return False
    
    @staticmethod
    def _delete_from_s3(file_path):
        """
        Delete a file from S3 storage.
        
        Args:
            file_path (str): The file path
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Parse S3 path
        s3_path = file_path.replace('s3://', '')
        bucket_name, object_key = s3_path.split('/', 1)
        
        # Create S3 client
        s3 = boto3.client(
            's3',
            region_name=current_app.config.get('S3_REGION', 'us-east-1'),
            aws_access_key_id=current_app.config.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=current_app.config.get('AWS_SECRET_ACCESS_KEY')
        )
        
        try:
            s3.delete_object(Bucket=bucket_name, Key=object_key)
            return True
        except Exception as e:
            current_app.logger.error(f"Error deleting file from S3: {str(e)}")
            return False

