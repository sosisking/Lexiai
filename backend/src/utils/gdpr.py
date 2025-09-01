"""
GDPR compliance utilities for the LexiAI application.
Implements data protection, user consent management, and data export/deletion.
"""

import json
import csv
import os
import datetime
from flask import current_app, jsonify
from sqlalchemy import inspect
from werkzeug.security import generate_password_hash

from src.models.user import User
from src.models.document import Document, DocumentVersion
from src.models.clause import Clause
from src.models.comment import Comment
from src.models.search_query import SearchQuery
from src.models.audit_log import AuditLog
from src.models.document_share import DocumentShare
from src.models.document_summary import DocumentSummary
from src.models.obligation import Obligation
from src.services.storage_service import StorageService


class GDPRService:
    """Service for handling GDPR-related operations."""
    
    @staticmethod
    def anonymize_user_data(user_id):
        """
        Anonymize a user's personal data without deleting their account.
        
        Args:
            user_id: ID of the user to anonymize
            
        Returns:
            dict: Result of the operation
        """
        from src.main import db
        
        try:
            user = User.query.get(user_id)
            if not user:
                return {"success": False, "message": "User not found"}
            
            # Generate anonymized values
            anon_email = f"anonymized_{user_id}@example.com"
            anon_name = f"Anonymized User {user_id}"
            
            # Log the anonymization
            current_app.logger.info(f"Anonymizing user data for user_id: {user_id}")
            
            # Update user record
            user.email = anon_email
            user.full_name = anon_name
            user.phone_number = None
            user.profile_image = None
            user.password_hash = generate_password_hash("ANONYMIZED")
            user.is_active = False
            user.anonymized_at = datetime.datetime.utcnow()
            
            # Save changes
            db.session.commit()
            
            return {"success": True, "message": "User data anonymized successfully"}
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error anonymizing user data: {str(e)}")
            return {"success": False, "message": f"Error: {str(e)}"}
    
    @staticmethod
    def delete_user_data(user_id):
        """
        Delete all user data in compliance with GDPR right to be forgotten.
        
        Args:
            user_id: ID of the user whose data should be deleted
            
        Returns:
            dict: Result of the operation
        """
        from src.main import db
        
        try:
            user = User.query.get(user_id)
            if not user:
                return {"success": False, "message": "User not found"}
            
            # Log the deletion request
            current_app.logger.info(f"Deleting all data for user_id: {user_id}")
            
            # Get storage service
            storage_service = StorageService()
            
            # Delete documents and related data
            documents = Document.query.filter_by(created_by_id=user_id).all()
            for document in documents:
                # Delete document versions and files
                versions = DocumentVersion.query.filter_by(document_id=document.id).all()
                for version in versions:
                    # Delete file from storage
                    if version.file_path:
                        try:
                            storage_service.delete_file(version.file_path)
                        except Exception as e:
                            current_app.logger.error(f"Error deleting file {version.file_path}: {str(e)}")
                    
                    # Delete clauses
                    Clause.query.filter_by(document_version_id=version.id).delete()
                    
                    # Delete summaries
                    DocumentSummary.query.filter_by(document_version_id=version.id).delete()
                    
                    # Delete obligations
                    Obligation.query.filter_by(document_version_id=version.id).delete()
                    
                    db.session.delete(version)
                
                # Delete comments
                Comment.query.filter_by(document_id=document.id).delete()
                
                # Delete shares
                DocumentShare.query.filter_by(document_id=document.id).delete()
                
                # Delete the document
                db.session.delete(document)
            
            # Delete search queries
            SearchQuery.query.filter_by(user_id=user_id).delete()
            
            # Delete audit logs
            AuditLog.query.filter_by(user_id=user_id).delete()
            
            # Delete the user
            db.session.delete(user)
            
            # Commit all changes
            db.session.commit()
            
            return {"success": True, "message": "User data deleted successfully"}
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting user data: {str(e)}")
            return {"success": False, "message": f"Error: {str(e)}"}
    
    @staticmethod
    def export_user_data(user_id):
        """
        Export all user data in compliance with GDPR right to data portability.
        
        Args:
            user_id: ID of the user whose data should be exported
            
        Returns:
            dict: Path to the exported data file
        """
        from src.main import db
        
        try:
            user = User.query.get(user_id)
            if not user:
                return {"success": False, "message": "User not found"}
            
            # Log the export request
            current_app.logger.info(f"Exporting all data for user_id: {user_id}")
            
            # Create export directory if it doesn't exist
            export_dir = os.path.join(current_app.config['TEMP_FOLDER'], 'exports')
            os.makedirs(export_dir, exist_ok=True)
            
            # Create a unique filename
            timestamp = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')
            export_filename = f"user_data_export_{user_id}_{timestamp}.json"
            export_path = os.path.join(export_dir, export_filename)
            
            # Collect user data
            user_data = {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
                },
                "documents": [],
                "comments": [],
                "search_queries": [],
                "audit_logs": []
            }
            
            # Get documents
            documents = Document.query.filter_by(created_by_id=user_id).all()
            for document in documents:
                doc_data = {
                    "id": document.id,
                    "title": document.title,
                    "created_at": document.created_at.isoformat() if document.created_at else None,
                    "updated_at": document.updated_at.isoformat() if document.updated_at else None,
                    "versions": [],
                    "clauses": [],
                    "comments": [],
                    "shares": []
                }
                
                # Get document versions
                versions = DocumentVersion.query.filter_by(document_id=document.id).all()
                for version in versions:
                    doc_data["versions"].append({
                        "id": version.id,
                        "version_number": version.version_number,
                        "file_name": version.file_name,
                        "file_type": version.file_type,
                        "file_size": version.file_size,
                        "created_at": version.created_at.isoformat() if version.created_at else None
                    })
                    
                    # Get clauses
                    clauses = Clause.query.filter_by(document_version_id=version.id).all()
                    for clause in clauses:
                        doc_data["clauses"].append({
                            "id": clause.id,
                            "category_id": clause.category_id,
                            "text": clause.text,
                            "risk_level": clause.risk_level,
                            "risk_description": clause.risk_description
                        })
                
                # Get comments
                comments = Comment.query.filter_by(document_id=document.id).all()
                for comment in comments:
                    doc_data["comments"].append({
                        "id": comment.id,
                        "text": comment.text,
                        "created_at": comment.created_at.isoformat() if comment.created_at else None,
                        "user_id": comment.user_id
                    })
                
                # Get shares
                shares = DocumentShare.query.filter_by(document_id=document.id).all()
                for share in shares:
                    doc_data["shares"].append({
                        "id": share.id,
                        "shared_with_email": share.shared_with_email,
                        "permission_level": share.permission_level,
                        "created_at": share.created_at.isoformat() if share.created_at else None
                    })
                
                user_data["documents"].append(doc_data)
            
            # Get search queries
            queries = SearchQuery.query.filter_by(user_id=user_id).all()
            for query in queries:
                user_data["search_queries"].append({
                    "id": query.id,
                    "query_text": query.query_text,
                    "created_at": query.created_at.isoformat() if query.created_at else None
                })
            
            # Get audit logs
            logs = AuditLog.query.filter_by(user_id=user_id).all()
            for log in logs:
                user_data["audit_logs"].append({
                    "id": log.id,
                    "action": log.action,
                    "resource_type": log.resource_type,
                    "resource_id": log.resource_id,
                    "created_at": log.created_at.isoformat() if log.created_at else None
                })
            
            # Write data to file
            with open(export_path, 'w') as f:
                json.dump(user_data, f, indent=2)
            
            return {
                "success": True, 
                "message": "User data exported successfully",
                "export_path": export_path
            }
            
        except Exception as e:
            current_app.logger.error(f"Error exporting user data: {str(e)}")
            return {"success": False, "message": f"Error: {str(e)}"}
    
    @staticmethod
    def record_consent(user_id, consent_type, consented=True):
        """
        Record user consent for various data processing activities.
        
        Args:
            user_id: ID of the user giving consent
            consent_type: Type of consent (e.g., 'marketing', 'analytics')
            consented: Whether the user consented or not
            
        Returns:
            dict: Result of the operation
        """
        from src.main import db
        from src.models.user_consent import UserConsent
        
        try:
            # Check if consent record exists
            consent = UserConsent.query.filter_by(
                user_id=user_id, 
                consent_type=consent_type
            ).first()
            
            if consent:
                # Update existing consent
                consent.consented = consented
                consent.updated_at = datetime.datetime.utcnow()
            else:
                # Create new consent record
                consent = UserConsent(
                    user_id=user_id,
                    consent_type=consent_type,
                    consented=consented,
                    ip_address=request.remote_addr if 'request' in globals() else None,
                    user_agent=request.user_agent.string if 'request' in globals() and request.user_agent else None
                )
                db.session.add(consent)
            
            # Save changes
            db.session.commit()
            
            return {"success": True, "message": "Consent recorded successfully"}
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error recording consent: {str(e)}")
            return {"success": False, "message": f"Error: {str(e)}"}
    
    @staticmethod
    def get_user_consents(user_id):
        """
        Get all consents for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            dict: User consents
        """
        from src.models.user_consent import UserConsent
        
        try:
            consents = UserConsent.query.filter_by(user_id=user_id).all()
            
            result = {
                "user_id": user_id,
                "consents": []
            }
            
            for consent in consents:
                result["consents"].append({
                    "consent_type": consent.consent_type,
                    "consented": consent.consented,
                    "created_at": consent.created_at.isoformat() if consent.created_at else None,
                    "updated_at": consent.updated_at.isoformat() if consent.updated_at else None
                })
            
            return {"success": True, "data": result}
            
        except Exception as e:
            current_app.logger.error(f"Error getting user consents: {str(e)}")
            return {"success": False, "message": f"Error: {str(e)}"}
    
    @staticmethod
    def generate_privacy_audit_report():
        """
        Generate a privacy audit report for compliance purposes.
        
        Returns:
            dict: Path to the generated report
        """
        from src.main import db
        from src.models.user_consent import UserConsent
        
        try:
            # Create export directory if it doesn't exist
            export_dir = os.path.join(current_app.config['TEMP_FOLDER'], 'reports')
            os.makedirs(export_dir, exist_ok=True)
            
            # Create a unique filename
            timestamp = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')
            report_filename = f"privacy_audit_report_{timestamp}.csv"
            report_path = os.path.join(export_dir, report_filename)
            
            # Get all users and their consents
            users = User.query.all()
            
            # Write report to CSV
            with open(report_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    'User ID', 'Email', 'Registration Date', 'Last Login',
                    'Marketing Consent', 'Analytics Consent', 'Data Sharing Consent',
                    'Data Retention Policy Accepted', 'Terms Accepted'
                ])
                
                for user in users:
                    # Get user consents
                    marketing_consent = UserConsent.query.filter_by(
                        user_id=user.id, consent_type='marketing'
                    ).first()
                    
                    analytics_consent = UserConsent.query.filter_by(
                        user_id=user.id, consent_type='analytics'
                    ).first()
                    
                    data_sharing_consent = UserConsent.query.filter_by(
                        user_id=user.id, consent_type='data_sharing'
                    ).first()
                    
                    retention_policy_consent = UserConsent.query.filter_by(
                        user_id=user.id, consent_type='data_retention'
                    ).first()
                    
                    terms_consent = UserConsent.query.filter_by(
                        user_id=user.id, consent_type='terms'
                    ).first()
                    
                    writer.writerow([
                        user.id,
                        user.email,
                        user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else 'N/A',
                        user.last_login_at.strftime('%Y-%m-%d %H:%M:%S') if user.last_login_at else 'N/A',
                        'Yes' if marketing_consent and marketing_consent.consented else 'No',
                        'Yes' if analytics_consent and analytics_consent.consented else 'No',
                        'Yes' if data_sharing_consent and data_sharing_consent.consented else 'No',
                        'Yes' if retention_policy_consent and retention_policy_consent.consented else 'No',
                        'Yes' if terms_consent and terms_consent.consented else 'No'
                    ])
            
            return {
                "success": True, 
                "message": "Privacy audit report generated successfully",
                "report_path": report_path
            }
            
        except Exception as e:
            current_app.logger.error(f"Error generating privacy audit report: {str(e)}")
            return {"success": False, "message": f"Error: {str(e)}"}


# Create routes for GDPR-related operations
def register_gdpr_routes(app):
    """
    Register GDPR-related routes.
    
    Args:
        app: Flask application instance
    """
    from flask import request, jsonify, send_file
    from src.middleware.auth_middleware import jwt_required, admin_required
    
    @app.route('/api/v1/gdpr/export-data', methods=['POST'])
    @jwt_required
    def export_user_data_route():
        """Export all data for the current user."""
        from flask import g
        
        result = GDPRService.export_user_data(g.user.id)
        
        if result["success"]:
            return send_file(
                result["export_path"],
                as_attachment=True,
                download_name=os.path.basename(result["export_path"])
            )
        else:
            return jsonify(result), 400
    
    @app.route('/api/v1/gdpr/anonymize-data', methods=['POST'])
    @jwt_required
    def anonymize_user_data_route():
        """Anonymize data for the current user."""
        from flask import g
        
        result = GDPRService.anonymize_user_data(g.user.id)
        return jsonify(result), 200 if result["success"] else 400
    
    @app.route('/api/v1/gdpr/delete-data', methods=['POST'])
    @jwt_required
    def delete_user_data_route():
        """Delete all data for the current user."""
        from flask import g
        
        result = GDPRService.delete_user_data(g.user.id)
        return jsonify(result), 200 if result["success"] else 400
    
    @app.route('/api/v1/gdpr/consent', methods=['POST'])
    @jwt_required
    def record_consent_route():
        """Record user consent."""
        from flask import g
        
        data = request.get_json()
        if not data or 'consent_type' not in data or 'consented' not in data:
            return jsonify({
                "success": False,
                "message": "Missing required fields: consent_type, consented"
            }), 400
        
        result = GDPRService.record_consent(
            g.user.id,
            data['consent_type'],
            data['consented']
        )
        
        return jsonify(result), 200 if result["success"] else 400
    
    @app.route('/api/v1/gdpr/consents', methods=['GET'])
    @jwt_required
    def get_user_consents_route():
        """Get all consents for the current user."""
        from flask import g
        
        result = GDPRService.get_user_consents(g.user.id)
        return jsonify(result), 200 if result["success"] else 400
    
    @app.route('/api/v1/gdpr/privacy-audit', methods=['GET'])
    @jwt_required
    @admin_required
    def generate_privacy_audit_report_route():
        """Generate a privacy audit report (admin only)."""
        result = GDPRService.generate_privacy_audit_report()
        
        if result["success"]:
            return send_file(
                result["report_path"],
                as_attachment=True,
                download_name=os.path.basename(result["report_path"])
            )
        else:
            return jsonify(result), 400

