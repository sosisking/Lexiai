from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from src.models.user import User
from src.models.organization import OrganizationUser

def admin_required():
    """
    Decorator to require admin role for a route.
    Must be used after @jwt_required() decorator.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user or not user.is_admin():
                return jsonify({'error': 'Admin privileges required'}), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper


def organization_access_required(role=None):
    """
    Decorator to require organization access for a route.
    Must be used after @jwt_required() decorator.
    
    Args:
        role (str, optional): Required role in the organization ('owner', 'admin', 'member').
                             If None, any role is allowed.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            
            # Get organization_id from URL parameters
            organization_id = kwargs.get('organization_id')
            if not organization_id:
                return jsonify({'error': 'Organization ID is required'}), 400
            
            # Check if user is a member of the organization
            org_user = OrganizationUser.query.filter_by(
                organization_id=organization_id,
                user_id=user_id
            ).first()
            
            if not org_user:
                return jsonify({'error': 'Unauthorized access to this organization'}), 403
            
            # Check if user has the required role
            if role:
                if role == 'owner' and org_user.role != 'owner':
                    return jsonify({'error': 'Owner privileges required'}), 403
                elif role == 'admin' and not org_user.is_admin():
                    return jsonify({'error': 'Admin privileges required'}), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper


def document_access_required(permission=None):
    """
    Decorator to require document access for a route.
    Must be used after @jwt_required() decorator.
    
    Args:
        permission (str, optional): Required permission level ('read', 'comment', 'edit').
                                   If None, 'read' permission is required.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            from src.models.document import Document
            from src.models.document_share import DocumentShare
            
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            
            # Get document_id from URL parameters
            document_id = kwargs.get('document_id')
            if not document_id:
                return jsonify({'error': 'Document ID is required'}), 400
            
            # Get the document
            document = Document.query.get(document_id)
            if not document:
                return jsonify({'error': 'Document not found'}), 404
            
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
                return jsonify({'error': 'Unauthorized access to this document'}), 403
            
            # Check permission level if specified
            if permission:
                if permission == 'edit':
                    # For edit permission, user must either be an admin in the organization or have edit permission on the document
                    if not (org_user and org_user.is_admin()) and not (document_share and document_share.can_edit()):
                        return jsonify({'error': 'Edit permission required'}), 403
                elif permission == 'comment':
                    # For comment permission, user must either be a member of the organization or have comment permission on the document
                    if not org_user and not (document_share and document_share.can_comment()):
                        return jsonify({'error': 'Comment permission required'}), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper

