import threading
from flask import current_app
from src.models import db
from src.models.document import Document
from src.services.ai_service import AIService

class TaskService:
    """Service for handling background tasks."""
    
    @staticmethod
    def process_document_async(document_id):
        """
        Process a document asynchronously.
        
        Args:
            document_id (int): The document ID
            
        Returns:
            bool: True if task was started, False otherwise
        """
        try:
            # Start a new thread for document processing
            thread = threading.Thread(
                target=TaskService._process_document,
                args=(document_id,)
            )
            thread.daemon = True
            thread.start()
            return True
        except Exception as e:
            current_app.logger.error(f"Error starting document processing task: {str(e)}")
            return False
    
    @staticmethod
    def _process_document(document_id):
        """
        Process a document.
        
        Args:
            document_id (int): The document ID
        """
        # Create a new application context
        with current_app.app_context():
            try:
                # Get document
                document = Document.query.get(document_id)
                if not document:
                    current_app.logger.error(f"Document not found: {document_id}")
                    return
                
                # Update document status
                document.status = 'processing'
                db.session.commit()
                
                # Process document
                success = AIService.analyze_document(document_id)
                
                # Update document status
                if success:
                    document.status = 'analyzed'
                else:
                    document.status = 'error'
                db.session.commit()
            
            except Exception as e:
                current_app.logger.error(f"Error processing document: {str(e)}")
                
                # Update document status
                try:
                    document = Document.query.get(document_id)
                    if document:
                        document.status = 'error'
                        db.session.commit()
                except:
                    pass

