"""
Tests for the document API.
"""

import json
import unittest
import io
import os
from .base import BaseTestCase


class DocumentTestCase(BaseTestCase):
    """Test case for document API."""
    
    def setUp(self):
        """Set up test environment."""
        super().setUp()
        
        # Create a test PDF file
        self.test_pdf_path = os.path.join(self.app.config['TEMP_FOLDER'], 'test.pdf')
        with open(self.test_pdf_path, 'wb') as f:
            f.write(b'%PDF-1.5\n%Test PDF file')
    
    def tearDown(self):
        """Tear down test environment."""
        # Remove test PDF file
        if os.path.exists(self.test_pdf_path):
            os.unlink(self.test_pdf_path)
        
        super().tearDown()
    
    def test_upload_document_success(self):
        """Test successful document upload."""
        token = self._get_user_token()
        headers = self._create_auth_header(token)
        
        # Create test file data
        with open(self.test_pdf_path, 'rb') as f:
            file_data = f.read()
        
        data = {
            'title': 'Test Document',
            'file': (io.BytesIO(file_data), 'test.pdf')
        }
        
        response = self.client.post(
            '/api/v1/documents',
            headers=headers,
            data=data,
            content_type='multipart/form-data'
        )
        
        self.assertEqual(response.status_code, 201)
        result = json.loads(response.data)
        self.assertIn('document', result)
        self.assertEqual(result['document']['title'], 'Test Document')
    
    def test_upload_document_no_file(self):
        """Test document upload with no file."""
        token = self._get_user_token()
        headers = self._create_auth_header(token)
        
        data = {
            'title': 'Test Document'
        }
        
        response = self.client.post(
            '/api/v1/documents',
            headers=headers,
            data=data,
            content_type='multipart/form-data'
        )
        
        self.assertEqual(response.status_code, 400)
        result = json.loads(response.data)
        self.assertIn('error', result)
    
    def test_upload_document_invalid_file_type(self):
        """Test document upload with invalid file type."""
        token = self._get_user_token()
        headers = self._create_auth_header(token)
        
        # Create test file data
        file_data = b'This is not a valid document file'
        
        data = {
            'title': 'Test Document',
            'file': (io.BytesIO(file_data), 'test.exe')
        }
        
        response = self.client.post(
            '/api/v1/documents',
            headers=headers,
            data=data,
            content_type='multipart/form-data'
        )
        
        self.assertEqual(response.status_code, 400)
        result = json.loads(response.data)
        self.assertIn('error', result)
    
    def test_get_documents(self):
        """Test getting all documents."""
        # First upload a document
        self.test_upload_document_success()
        
        token = self._get_user_token()
        headers = self._create_auth_header(token)
        
        response = self.client.get(
            '/api/v1/documents',
            headers=headers
        )
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertIn('documents', result)
        self.assertGreaterEqual(len(result['documents']), 1)
    
    def test_get_document_by_id(self):
        """Test getting a document by ID."""
        # First upload a document
        self.test_upload_document_success()
        
        token = self._get_user_token()
        headers = self._create_auth_header(token)
        
        # Get all documents to find the ID
        response = self.client.get(
            '/api/v1/documents',
            headers=headers
        )
        
        result = json.loads(response.data)
        document_id = result['documents'][0]['id']
        
        # Get the document by ID
        response = self.client.get(
            f'/api/v1/documents/{document_id}',
            headers=headers
        )
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertIn('document', result)
        self.assertEqual(result['document']['id'], document_id)
    
    def test_get_nonexistent_document(self):
        """Test getting a nonexistent document."""
        token = self._get_user_token()
        headers = self._create_auth_header(token)
        
        response = self.client.get(
            '/api/v1/documents/999',
            headers=headers
        )
        
        self.assertEqual(response.status_code, 404)
        result = json.loads(response.data)
        self.assertIn('error', result)
    
    def test_update_document(self):
        """Test updating a document."""
        # First upload a document
        self.test_upload_document_success()
        
        token = self._get_user_token()
        headers = self._create_auth_header(token)
        
        # Get all documents to find the ID
        response = self.client.get(
            '/api/v1/documents',
            headers=headers
        )
        
        result = json.loads(response.data)
        document_id = result['documents'][0]['id']
        
        # Update the document
        update_data = {
            'title': 'Updated Document Title'
        }
        
        response = self.client.put(
            f'/api/v1/documents/{document_id}',
            headers=headers,
            json=update_data
        )
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertIn('document', result)
        self.assertEqual(result['document']['title'], 'Updated Document Title')
    
    def test_delete_document(self):
        """Test deleting a document."""
        # First upload a document
        self.test_upload_document_success()
        
        token = self._get_user_token()
        headers = self._create_auth_header(token)
        
        # Get all documents to find the ID
        response = self.client.get(
            '/api/v1/documents',
            headers=headers
        )
        
        result = json.loads(response.data)
        document_id = result['documents'][0]['id']
        
        # Delete the document
        response = self.client.delete(
            f'/api/v1/documents/{document_id}',
            headers=headers
        )
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertIn('message', result)
        
        # Try to get the deleted document
        response = self.client.get(
            f'/api/v1/documents/{document_id}',
            headers=headers
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_share_document(self):
        """Test sharing a document."""
        # First upload a document
        self.test_upload_document_success()
        
        token = self._get_user_token()
        headers = self._create_auth_header(token)
        
        # Get all documents to find the ID
        response = self.client.get(
            '/api/v1/documents',
            headers=headers
        )
        
        result = json.loads(response.data)
        document_id = result['documents'][0]['id']
        
        # Share the document
        share_data = {
            'email': 'shared@example.com',
            'permission': 'view'
        }
        
        response = self.client.post(
            f'/api/v1/documents/{document_id}/share',
            headers=headers,
            json=share_data
        )
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertIn('message', result)
        
        # Get document shares
        response = self.client.get(
            f'/api/v1/documents/{document_id}/shares',
            headers=headers
        )
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertIn('shares', result)
        self.assertEqual(len(result['shares']), 1)
        self.assertEqual(result['shares'][0]['shared_with_email'], 'shared@example.com')


if __name__ == '__main__':
    unittest.main()

