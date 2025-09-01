"""
Tests for the AI analysis API.
"""

import json
import unittest
import io
import os
from unittest.mock import patch, MagicMock
from .base import BaseTestCase


class AITestCase(BaseTestCase):
    """Test case for AI analysis API."""
    
    def setUp(self):
        """Set up test environment."""
        super().setUp()
        
        # Create a test PDF file
        self.test_pdf_path = os.path.join(self.app.config['TEMP_FOLDER'], 'test.pdf')
        with open(self.test_pdf_path, 'wb') as f:
            f.write(b'%PDF-1.5\n%Test PDF file')
        
        # Upload a document for testing
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
        
        result = json.loads(response.data)
        self.document_id = result['document']['id']
    
    def tearDown(self):
        """Tear down test environment."""
        # Remove test PDF file
        if os.path.exists(self.test_pdf_path):
            os.unlink(self.test_pdf_path)
        
        super().tearDown()
    
    @patch('src.services.ai_service.OpenAI')
    def test_analyze_document(self, mock_openai):
        """Test analyzing a document."""
        # Mock OpenAI response
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message = MagicMock()
        mock_completion.choices[0].message.content = json.dumps({
            'clauses': [
                {
                    'category': 'Termination',
                    'text': 'Either party may terminate this Agreement upon 30 days written notice.',
                    'risk_level': 'medium',
                    'risk_description': 'Short termination period may not provide sufficient time to transition services.'
                }
            ],
            'summary': {
                'overview': 'This is a service agreement between two parties.',
                'parties': ['Party A', 'Party B'],
                'key_terms': ['Term: 1 year', 'Payment: Monthly'],
                'important_dates': ['Effective Date: January 1, 2023'],
                'notable_provisions': ['Short termination period']
            },
            'obligations': [
                {
                    'party': 'Customer',
                    'description': 'Pay monthly service fee',
                    'deadline': '15th of each month',
                    'consequence': 'Late fee of 1.5% per month on outstanding balance'
                }
            ]
        })
        
        mock_openai_instance = MagicMock()
        mock_openai_instance.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_openai_instance
        
        token = self._get_user_token()
        headers = self._create_auth_header(token)
        
        response = self.client.post(
            f'/api/v1/ai/analyze/{self.document_id}',
            headers=headers
        )
        
        self.assertEqual(response.status_code, 202)
        result = json.loads(response.data)
        self.assertIn('message', result)
        self.assertIn('task_id', result)
    
    @patch('src.services.ai_service.OpenAI')
    def test_search_document(self, mock_openai):
        """Test searching a document."""
        # Mock OpenAI response
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message = MagicMock()
        mock_completion.choices[0].message.content = json.dumps({
            'answer': 'The termination period is 30 days.',
            'context': 'Either party may terminate this Agreement upon 30 days written notice.',
            'explanation': 'The contract specifies a 30-day termination period with written notice.'
        })
        
        mock_openai_instance = MagicMock()
        mock_openai_instance.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_openai_instance
        
        token = self._get_user_token()
        headers = self._create_auth_header(token)
        
        query_data = {
            'query': 'What is the termination period?'
        }
        
        response = self.client.post(
            f'/api/v1/ai/search/{self.document_id}',
            headers=headers,
            json=query_data
        )
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertIn('result', result)
        self.assertIn('answer', result['result'])
        self.assertIn('context', result['result'])
        self.assertIn('explanation', result['result'])
    
    def test_get_analysis_status(self):
        """Test getting analysis status."""
        token = self._get_user_token()
        headers = self._create_auth_header(token)
        
        # First start an analysis
        with patch('src.services.ai_service.OpenAI'):
            response = self.client.post(
                f'/api/v1/ai/analyze/{self.document_id}',
                headers=headers
            )
            
            result = json.loads(response.data)
            task_id = result['task_id']
        
        # Then check the status
        response = self.client.get(
            f'/api/v1/ai/status/{task_id}',
            headers=headers
        )
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertIn('status', result)
        self.assertIn(result['status'], ['pending', 'processing', 'completed', 'failed'])
    
    def test_get_clauses(self):
        """Test getting document clauses."""
        token = self._get_user_token()
        headers = self._create_auth_header(token)
        
        response = self.client.get(
            f'/api/v1/ai/clauses/{self.document_id}',
            headers=headers
        )
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertIn('clauses', result)
    
    def test_get_summary(self):
        """Test getting document summary."""
        token = self._get_user_token()
        headers = self._create_auth_header(token)
        
        response = self.client.get(
            f'/api/v1/ai/summary/{self.document_id}',
            headers=headers
        )
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertIn('summary', result)
    
    def test_get_obligations(self):
        """Test getting document obligations."""
        token = self._get_user_token()
        headers = self._create_auth_header(token)
        
        response = self.client.get(
            f'/api/v1/ai/obligations/{self.document_id}',
            headers=headers
        )
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertIn('obligations', result)
    
    def test_get_search_history(self):
        """Test getting search history."""
        token = self._get_user_token()
        headers = self._create_auth_header(token)
        
        response = self.client.get(
            f'/api/v1/ai/search-history/{self.document_id}',
            headers=headers
        )
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertIn('search_history', result)


if __name__ == '__main__':
    unittest.main()

