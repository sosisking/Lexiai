import stripe
from flask import current_app
from datetime import datetime
from src.models import db
from src.models.subscription import Subscription
from src.models.user import User

class BillingService:
    """Service for handling Stripe billing operations."""
    
    @staticmethod
    def init_stripe():
        """Initialize Stripe with API key."""
        stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
    
    @staticmethod
    def create_customer(user):
        """
        Create a Stripe customer for a user.
        
        Args:
            user (User): The user to create a customer for
            
        Returns:
            str: The Stripe customer ID
        """
        BillingService.init_stripe()
        
        customer = stripe.Customer.create(
            email=user.email,
            name=user.full_name,
            metadata={
                'user_id': user.id
            }
        )
        
        return customer.id
    
    @staticmethod
    def create_subscription(user, plan_id, payment_method_id=None):
        """
        Create a subscription for a user.
        
        Args:
            user (User): The user to create a subscription for
            plan_id (str): The Stripe plan ID
            payment_method_id (str, optional): The payment method ID
            
        Returns:
            dict: The subscription details
        """
        BillingService.init_stripe()
        
        # Get or create customer
        subscription_record = Subscription.query.filter_by(user_id=user.id).first()
        
        if subscription_record and subscription_record.stripe_customer_id:
            customer_id = subscription_record.stripe_customer_id
        else:
            customer_id = BillingService.create_customer(user)
            
            # Create or update subscription record
            if not subscription_record:
                subscription_record = Subscription(
                    user_id=user.id,
                    stripe_customer_id=customer_id,
                    plan_type='free',
                    status='active'
                )
                db.session.add(subscription_record)
            else:
                subscription_record.stripe_customer_id = customer_id
            
            db.session.commit()
        
        # Attach payment method to customer if provided
        if payment_method_id:
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=customer_id
            )
            
            # Set as default payment method
            stripe.Customer.modify(
                customer_id,
                invoice_settings={
                    'default_payment_method': payment_method_id
                }
            )
        
        # Create subscription
        stripe_subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[
                {'price': plan_id}
            ],
            expand=['latest_invoice.payment_intent']
        )
        
        # Update subscription record
        subscription_record.stripe_subscription_id = stripe_subscription.id
        subscription_record.plan_type = 'premium'  # Update based on plan_id in a real implementation
        subscription_record.status = stripe_subscription.status
        subscription_record.current_period_start = datetime.fromtimestamp(stripe_subscription.current_period_start)
        subscription_record.current_period_end = datetime.fromtimestamp(stripe_subscription.current_period_end)
        db.session.commit()
        
        return {
            'subscription_id': stripe_subscription.id,
            'status': stripe_subscription.status,
            'current_period_end': stripe_subscription.current_period_end,
            'client_secret': stripe_subscription.latest_invoice.payment_intent.client_secret if hasattr(stripe_subscription, 'latest_invoice') and hasattr(stripe_subscription.latest_invoice, 'payment_intent') else None
        }
    
    @staticmethod
    def cancel_subscription(subscription_id):
        """
        Cancel a subscription.
        
        Args:
            subscription_id (str): The Stripe subscription ID
            
        Returns:
            dict: The canceled subscription details
        """
        BillingService.init_stripe()
        
        # Cancel at period end
        stripe_subscription = stripe.Subscription.modify(
            subscription_id,
            cancel_at_period_end=True
        )
        
        # Update subscription record
        subscription_record = Subscription.query.filter_by(stripe_subscription_id=subscription_id).first()
        if subscription_record:
            subscription_record.status = 'canceled'
            db.session.commit()
        
        return {
            'subscription_id': stripe_subscription.id,
            'status': stripe_subscription.status,
            'cancel_at': stripe_subscription.cancel_at,
            'current_period_end': stripe_subscription.current_period_end
        }
    
    @staticmethod
    def update_subscription(subscription_id, plan_id):
        """
        Update a subscription plan.
        
        Args:
            subscription_id (str): The Stripe subscription ID
            plan_id (str): The new Stripe plan ID
            
        Returns:
            dict: The updated subscription details
        """
        BillingService.init_stripe()
        
        # Get subscription
        stripe_subscription = stripe.Subscription.retrieve(subscription_id)
        
        # Update subscription items
        stripe.SubscriptionItem.modify(
            stripe_subscription['items']['data'][0].id,
            price=plan_id
        )
        
        # Retrieve updated subscription
        updated_subscription = stripe.Subscription.retrieve(subscription_id)
        
        # Update subscription record
        subscription_record = Subscription.query.filter_by(stripe_subscription_id=subscription_id).first()
        if subscription_record:
            subscription_record.plan_type = 'premium'  # Update based on plan_id in a real implementation
            subscription_record.current_period_end = datetime.fromtimestamp(updated_subscription.current_period_end)
            db.session.commit()
        
        return {
            'subscription_id': updated_subscription.id,
            'status': updated_subscription.status,
            'current_period_end': updated_subscription.current_period_end
        }
    
    @staticmethod
    def handle_webhook_event(payload, signature):
        """
        Handle Stripe webhook events.
        
        Args:
            payload (bytes): The webhook payload
            signature (str): The webhook signature
            
        Returns:
            dict: The processed event
        """
        BillingService.init_stripe()
        
        webhook_secret = current_app.config['STRIPE_WEBHOOK_SECRET']
        
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
        except ValueError as e:
            # Invalid payload
            return {'error': str(e)}, 400
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return {'error': str(e)}, 400
        
        # Handle specific event types
        if event['type'] == 'customer.subscription.updated':
            subscription = event['data']['object']
            BillingService._handle_subscription_updated(subscription)
        elif event['type'] == 'customer.subscription.deleted':
            subscription = event['data']['object']
            BillingService._handle_subscription_deleted(subscription)
        elif event['type'] == 'invoice.payment_succeeded':
            invoice = event['data']['object']
            BillingService._handle_payment_succeeded(invoice)
        elif event['type'] == 'invoice.payment_failed':
            invoice = event['data']['object']
            BillingService._handle_payment_failed(invoice)
        
        return {'status': 'success', 'event_type': event['type']}
    
    @staticmethod
    def _handle_subscription_updated(subscription):
        """Handle subscription updated event."""
        subscription_record = Subscription.query.filter_by(stripe_subscription_id=subscription.id).first()
        if subscription_record:
            subscription_record.status = subscription.status
            subscription_record.current_period_start = datetime.fromtimestamp(subscription.current_period_start)
            subscription_record.current_period_end = datetime.fromtimestamp(subscription.current_period_end)
            db.session.commit()
    
    @staticmethod
    def _handle_subscription_deleted(subscription):
        """Handle subscription deleted event."""
        subscription_record = Subscription.query.filter_by(stripe_subscription_id=subscription.id).first()
        if subscription_record:
            subscription_record.status = 'canceled'
            db.session.commit()
    
    @staticmethod
    def _handle_payment_succeeded(invoice):
        """Handle payment succeeded event."""
        if invoice.subscription:
            subscription_record = Subscription.query.filter_by(stripe_subscription_id=invoice.subscription).first()
            if subscription_record:
                subscription_record.status = 'active'
                db.session.commit()
    
    @staticmethod
    def _handle_payment_failed(invoice):
        """Handle payment failed event."""
        if invoice.subscription:
            subscription_record = Subscription.query.filter_by(stripe_subscription_id=invoice.subscription).first()
            if subscription_record:
                subscription_record.status = 'past_due'
                db.session.commit()
    
    @staticmethod
    def get_subscription_plans():
        """
        Get available subscription plans.
        
        Returns:
            list: List of available plans
        """
        # In a real implementation, these would be fetched from Stripe
        # For the MVP, we'll return hardcoded plans
        return [
            {
                'id': 'price_monthly',
                'name': 'Monthly Subscription',
                'price': 100,
                'interval': 'month',
                'features': [
                    'Unlimited document uploads',
                    'AI contract review',
                    'Clause extraction and classification',
                    'Risk highlighting',
                    'Natural language search',
                    'Collaboration features'
                ]
            },
            {
                'id': 'price_yearly',
                'name': 'Yearly Subscription',
                'price': 1000,
                'interval': 'year',
                'features': [
                    'Unlimited document uploads',
                    'AI contract review',
                    'Clause extraction and classification',
                    'Risk highlighting',
                    'Natural language search',
                    'Collaboration features',
                    '2 months free'
                ]
            }
        ]

