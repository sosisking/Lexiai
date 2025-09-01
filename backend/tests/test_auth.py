"""
Tests for the authentication API.
"""

import json
import unittest
from .base import BaseTestCase


class AuthTestCase(BaseTestCase):
    """Test case for authentication API."""
    
    def test_login_success(self):
        """Test successful login."""
        response = self.client.post(
            '/api/v1/auth/login',
            json={
                'email': 'user@example.com',
                'password': 'userpassword'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('access_token', data)
        self.assertIn('user', data)
        self.assertEqual(data['user']['email'], 'user@example.com')
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        response = self.client.post(
            '/api/v1/auth/login',
            json={
                'email': 'user@example.com',
                'password': 'wrongpassword'
            }
        )
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_login_missing_fields(self):
        """Test login with missing fields."""
        response = self.client.post(
            '/api/v1/auth/login',
            json={
                'email': 'user@example.com'
            }
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_register_success(self):
        """Test successful registration."""
        response = self.client.post(
            '/api/v1/auth/register',
            json={
                'email': 'newuser@example.com',
                'password': 'newuserpassword',
                'first_name': 'New',
                'last_name': 'User',
                'organization_name': 'New Organization'
            }
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('access_token', data)
        self.assertIn('user', data)
        self.assertEqual(data['user']['email'], 'newuser@example.com')
    
    def test_register_existing_email(self):
        """Test registration with existing email."""
        response = self.client.post(
            '/api/v1/auth/register',
            json={
                'email': 'user@example.com',
                'password': 'newuserpassword',
                'first_name': 'New',
                'last_name': 'User',
                'organization_name': 'New Organization'
            }
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_register_missing_fields(self):
        """Test registration with missing fields."""
        response = self.client.post(
            '/api/v1/auth/register',
            json={
                'email': 'newuser@example.com',
                'password': 'newuserpassword'
            }
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_me_authenticated(self):
        """Test getting current user when authenticated."""
        token = self._get_user_token()
        headers = self._create_auth_header(token)
        
        response = self.client.get(
            '/api/v1/auth/me',
            headers=headers
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('user', data)
        self.assertEqual(data['user']['email'], 'user@example.com')
    
    def test_me_unauthenticated(self):
        """Test getting current user when unauthenticated."""
        response = self.client.get('/api/v1/auth/me')
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_refresh_token(self):
        """Test refreshing access token."""
        # First login to get a token
        login_response = self.client.post(
            '/api/v1/auth/login',
            json={
                'email': 'user@example.com',
                'password': 'userpassword'
            }
        )
        
        login_data = json.loads(login_response.data)
        token = login_data['access_token']
        headers = self._create_auth_header(token)
        
        # Then refresh the token
        refresh_response = self.client.post(
            '/api/v1/auth/refresh',
            headers=headers
        )
        
        self.assertEqual(refresh_response.status_code, 200)
        refresh_data = json.loads(refresh_response.data)
        self.assertIn('access_token', refresh_data)
        self.assertNotEqual(token, refresh_data['access_token'])
    
    def test_logout(self):
        """Test logging out."""
        token = self._get_user_token()
        headers = self._create_auth_header(token)
        
        response = self.client.post(
            '/api/v1/auth/logout',
            headers=headers
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
        
        # Try to use the token after logout
        me_response = self.client.get(
            '/api/v1/auth/me',
            headers=headers
        )
        
        # Token should be invalidated
        self.assertEqual(me_response.status_code, 401)


if __name__ == '__main__':
    unittest.main()

