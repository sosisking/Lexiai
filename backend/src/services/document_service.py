import os
from flask import current_app
from werkzeug.utils import secure_filename
from src.models import db
from src.models.document import Document, DocumentVersion
from src.models.document_share import DocumentShare
from src.services.storage_service import StorageService
from src.utils.validators import validate_file_type, validate_file_size

class DocumentService:
    """Service for handling document operations."""
    
    @staticmethod
    def upload_document(file, title, organization_id, user_id, description=None):
        """
        Upload a document.
        
        Args:
            file: The file object to upload
            title (str): The document title
            organization_id (int): The organization ID
            user_id (int): The user ID
            description (str, optional): The document description. Defaults to None.
            
        Returns:
            tuple: (Document, str) - (document, error_message)
        """
        # Validate file type
        filename = secure_filename(file.filename)
        valid, message = validate_file_type(filename)
        if not valid:
            return None, message
        
        # Validate file size
        valid, message = validate_file_size(file)
        if not valid:
            return None, message
        
        # Get file type
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        file_type = ext
        
        # Save file
        try:
            file_path, file_size = StorageService.save_file(file, file_type)
        except Exception as e:
            current_app.logger.error(f"Error saving file: {str(e)}")
            return None, f"Error saving file: {str(e)}"
        
        # Create document
        document = Document(
            organization_id=organization_id,
            uploaded_by_user_id=user_id,
            title=title,
            description=description,
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            status='processing'
        )
        
        # Add document to database
        db.session.add(document)
        db.session.flush()  # Flush to get the document ID
        
        # Create initial document version
        version = DocumentVersion(
            document_id=document.id,
            version_number=1,
            file_path=file_path,
            created_by_user_id=user_id
        )
        db.session.add(version)
        
        # Commit changes
        db.session.commit()
        
        # Queue document for processing
        DocumentService.queue_document_for_processing(document.id)
        
        return document, None
    
    @staticmethod
    def queue_document_for_processing(document_id):
        """
        Queue a document for processing.
        
        Args:
            document_id (int): The document ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        # In a real implementation, this would add the document to a queue for processing
        # For the MVP, we'll just update the status to 'processed'
        document = Document.query.get(document_id)
        if not document:
            return False
        
        document.status = 'processed'
        db.session.commit()
        
        return True
    
    @staticmethod
    def get_document(document_id, user_id):
        """
        Get a document.
        
        Args:
            document_id (int): The document ID
            user_id (int): The user ID
            
        Returns:
            tuple: (Document, str) - (document, error_message)
        """
        from src.models.organization import OrganizationUser
        
        # Get document
        document = Document.query.get(document_id)
        if not document:
            return None, "Document not found"
        
        # Check if user is a member of the document's organization
        org_user = OrganizationUser.query.filter_by(
            organization_id=document.organization_id,
            user_id=user_id
        ).first()
        
        # Check if user has direct share access to the document
        document_share = DocumentShare.query.filter_by(
            document_id=document_id,
            user_id=user_id
        ).first()
        
        # User must either be in the organization or have direct share access
        if not org_user and not document_share:
            return None, "Unauthorized access to this document"
        
        return document, None
    
    @staticmethod
    def get_document_content(document_id, user_id):
        """
        Get document content.
        
        Args:
            document_id (int): The document ID
            user_id (int): The user ID
            
        Returns:
            tuple: (bytes, str, str) - (content, file_type, error_message)
        """
        # Get document
        document, error = DocumentService.get_document(document_id, user_id)
        if not document:
            return None, None, error
        
        # Get file content
        content, file_type = StorageService.get_file(document.file_path)
        if not content:
            return None, None, "Error retrieving document content"
        
        return content, file_type, None
    
    @staticmethod
    def update_document(document_id, user_id, title=None, description=None, file=None):
        """
        Update a document.
        
        Args:
            document_id (int): The document ID
            user_id (int): The user ID
            title (str, optional): The new title. Defaults to None.
            description (str, optional): The new description. Defaults to None.
            file (file, optional): The new file. Defaults to None.
            
        Returns:
            tuple: (Document, str) - (document, error_message)
        """
        from src.models.organization import OrganizationUser
        
        # Get document
        document = Document.query.get(document_id)
        if not document:
            return None, "Document not found"
        
        # Check if user is an admin in the document's organization
        org_user = OrganizationUser.query.filter_by(
            organization_id=document.organization_id,
            user_id=user_id
        ).first()
        
        # Check if user has edit access to the document
        document_share = DocumentShare.query.filter_by(
            document_id=document_id,
            user_id=user_id,
            permission_level='edit'
        ).first()
        
        # User must either be an admin in the organization or have edit permission on the document
        if not (org_user and org_user.is_admin()) and not document_share:
            return None, "Unauthorized access to edit this document"
        
        # Update document fields
        if title:
            document.title = title
        if description is not None:
            document.description = description
        
        # Update file if provided
        if file:
            # Validate file type
            filename = secure_filename(file.filename)
            valid, message = validate_file_type(filename)
            if not valid:
                return None, message
            
            # Validate file size
            valid, message = validate_file_size(file)
            if not valid:
                return None, message
            
            # Get file type
            ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
            file_type = ext
            
            # Save file
            try:
                file_path, file_size = StorageService.save_file(file, file_type)
            except Exception as e:
                current_app.logger.error(f"Error saving file: {str(e)}")
                return None, f"Error saving file: {str(e)}"
            
            # Update document
            document.file_path = file_path
            document.file_type = file_type
            document.file_size = file_size
            document.status = 'processing'
            
            # Create new document version
            latest_version = DocumentVersion.query.filter_by(document_id=document_id).order_by(DocumentVersion.version_number.desc()).first()
            version_number = latest_version.version_number + 1 if latest_version else 1
            
            version = DocumentVersion(
                document_id=document_id,
                version_number=version_number,
                file_path=file_path,
                created_by_user_id=user_id
            )
            db.session.add(version)
            
            # Queue document for processing
            DocumentService.queue_document_for_processing(document_id)
        
        # Commit changes
        db.session.commit()
        
        return document, None
    
    @staticmethod
    def delete_document(document_id, user_id):
        """
        Delete a document.
        
        Args:
            document_id (int): The document ID
            user_id (int): The user ID
            
        Returns:
            tuple: (bool, str) - (success, error_message)
        """
        from src.models.organization import OrganizationUser
        
        # Get document
        document = Document.query.get(document_id)
        if not document:
            return False, "Document not found"
        
        # Check if user is an admin in the document's organization
        org_user = OrganizationUser.query.filter_by(
            organization_id=document.organization_id,
            user_id=user_id
        ).first()
        
        # User must be an admin in the organization
        if not org_user or not org_user.is_admin():
            return False, "Unauthorized access to delete this document"
        
        # Delete document file
        StorageService.delete_file(document.file_path)
        
        # Delete document versions
        for version in document.versions:
            if version.file_path != document.file_path:
                StorageService.delete_file(version.file_path)
        
        # Delete document from database
        db.session.delete(document)
        db.session.commit()
        
        return True, None
    
    @staticmethod
    def share_document(document_id, user_id, target_user_id, permission_level='read'):
        """
        Share a document with a user.
        
        Args:
            document_id (int): The document ID
            user_id (int): The user ID
            target_user_id (int): The target user ID
            permission_level (str, optional): The permission level. Defaults to 'read'.
            
        Returns:
            tuple: (DocumentShare, str) - (document_share, error_message)
        """
        from src.models.organization import OrganizationUser
        from src.models.user import User
        
        # Get document
        document = Document.query.get(document_id)
        if not document:
            return None, "Document not found"
        
        # Check if user is an admin in the document's organization
        org_user = OrganizationUser.query.filter_by(
            organization_id=document.organization_id,
            user_id=user_id
        ).first()
        
        # Check if user has edit access to the document
        document_share = DocumentShare.query.filter_by(
            document_id=document_id,
            user_id=user_id,
            permission_level='edit'
        ).first()
        
        # User must either be an admin in the organization or have edit permission on the document
        if not (org_user and org_user.is_admin()) and not document_share:
            return None, "Unauthorized access to share this document"
        
        # Check if target user exists
        target_user = User.query.get(target_user_id)
        if not target_user:
            return None, "Target user not found"
        
        # Check if document is already shared with target user
        existing_share = DocumentShare.query.filter_by(
            document_id=document_id,
            user_id=target_user_id
        ).first()
        
        if existing_share:
            # Update permission level
            existing_share.permission_level = permission_level
            db.session.commit()
            return existing_share, None
        
        # Create new share
        new_share = DocumentShare(
            document_id=document_id,
            user_id=target_user_id,
            permission_level=permission_level
        )
        db.session.add(new_share)
        db.session.commit()
        
        return new_share, None
    
    @staticmethod
    def unshare_document(document_id, user_id, target_user_id):
        """
        Unshare a document with a user.
        
        Args:
            document_id (int): The document ID
            user_id (int): The user ID
            target_user_id (int): The target user ID
            
        Returns:
            tuple: (bool, str) - (success, error_message)
        """
        from src.models.organization import OrganizationUser
        
        # Get document
        document = Document.query.get(document_id)
        if not document:
            return False, "Document not found"
        
        # Check if user is an admin in the document's organization
        org_user = OrganizationUser.query.filter_by(
            organization_id=document.organization_id,
            user_id=user_id
        ).first()
        
        # Check if user has edit access to the document
        document_share = DocumentShare.query.filter_by(
            document_id=document_id,
            user_id=user_id,
            permission_level='edit'
        ).first()
        
        # User must either be an admin in the organization or have edit permission on the document
        if not (org_user and org_user.is_admin()) and not document_share:
            return False, "Unauthorized access to unshare this document"
        
        # Check if document is shared with target user
        existing_share = DocumentShare.query.filter_by(
            document_id=document_id,
            user_id=target_user_id
        ).first()
        
        if not existing_share:
            return False, "Document is not shared with this user"
        
        # Delete share
        db.session.delete(existing_share)
        db.session.commit()
        
        return True, None

