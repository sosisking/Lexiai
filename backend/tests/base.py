"""
Base test case for LexiAI backend tests.
"""

import os
import unittest
import tempfile
import json
from datetime import datetime, timedelta

from src.main import create_app, db
from src.models.user import User
from src.models.organization import Organization, OrganizationUser
from src.models.subscription import Subscription, SubscriptionPlan


class BaseTestCase(unittest.TestCase):
    """Base test case for all tests."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary database
        self.db_fd, self.db_path = tempfile.mkstemp()
        
        # Configure the application for testing
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': f'sqlite:///{self.db_path}',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'JWT_SECRET_KEY': 'test-secret-key',
            'JWT_ACCESS_TOKEN_EXPIRES': timedelta(hours=1),
            'UPLOAD_FOLDER': tempfile.mkdtemp(),
            'TEMP_FOLDER': tempfile.mkdtemp(),
            'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB
            'STRIPE_SECRET_KEY': 'test-stripe-key',
            'STRIPE_PUBLISHABLE_KEY': 'test-stripe-publishable-key',
            'STRIPE_WEBHOOK_SECRET': 'test-stripe-webhook-secret',
            'OPENAI_API_KEY': 'test-openai-key',
        })
        
        # Create a test client
        self.client = self.app.test_client()
        
        # Create the database and tables
        with self.app.app_context():
            db.create_all()
            self._create_test_data()
    
    def tearDown(self):
        """Tear down test environment."""
        # Close the database file and remove it
        os.close(self.db_fd)
        os.unlink(self.db_path)
        
        # Remove temporary upload folder
        os.rmdir(self.app.config['UPLOAD_FOLDER'])
        os.rmdir(self.app.config['TEMP_FOLDER'])
    
    def _create_test_data(self):
        """Create test data for the database."""
        # Create test users
        admin_user = User(
            email='admin@example.com',
            password='adminpassword',
            first_name='Admin',
            last_name='User',
            role='admin'
        )
        
        regular_user = User(
            email='user@example.com',
            password='userpassword',
            first_name='Regular',
            last_name='User',
            role='user'
        )
        
        db.session.add(admin_user)
        db.session.add(regular_user)
        db.session.commit()
        
        # Create test organization
        org = Organization(
            name='Test Organization',
            created_by_id=regular_user.id
        )
        db.session.add(org)
        db.session.commit()
        
        # Add users to organization
        org_admin = OrganizationUser(
            organization_id=org.id,
            user_id=regular_user.id,
            role='owner'
        )
        
        org_member = OrganizationUser(
            organization_id=org.id,
            user_id=admin_user.id,
            role='member'
        )
        
        db.session.add(org_admin)
        db.session.add(org_member)
        
        # Create subscription plan
        plan = SubscriptionPlan(
            name='Standard',
            price=100,
            billing_interval='month',
            stripe_price_id='price_test123',
            features={
                'max_documents': 100,
                'max_users': 10,
                'advanced_ai': False
            }
        )
        db.session.add(plan)
        db.session.commit()
        
        # Create subscription
        subscription = Subscription(
            user_id=regular_user.id,
            organization_id=org.id,
            plan_id=plan.id,
            status='active',
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=30),
            stripe_subscription_id='sub_test123',
            stripe_customer_id='cus_test123'
        )
        db.session.add(subscription)
        db.session.commit()
    
    def _get_admin_token(self):
        """Get a JWT token for the admin user."""
        response = self.client.post(
            '/api/v1/auth/login',
            json={
                'email': 'admin@example.com',
                'password': 'adminpassword'
            }
        )
        data = json.loads(response.data)
        return data['access_token']
    
    def _get_user_token(self):
        """Get a JWT token for the regular user."""
        response = self.client.post(
            '/api/v1/auth/login',
            json={
                'email': 'user@example.com',
                'password': 'userpassword'
            }
        )
        data = json.loads(response.data)
        return data['access_token']
    
    def _create_auth_header(self, token):
        """Create an Authorization header with the given token."""
        return {'Authorization': f'Bearer {token}'}

