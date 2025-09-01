from flask import Blueprint, jsonify, request, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import io
from src.models import db
from src.models.document import Document
from src.models.document_share import DocumentShare
from src.services.document_service import DocumentService
from src.services.task_service import TaskService
from src.middleware.auth_middleware import organization_access_required, document_access_required
from src.middleware.logging_middleware import log_audit_event

document_bp = Blueprint('document', __name__)

@document_bp.route('/organizations/<int:organization_id>/documents', methods=['GET'])
@jwt_required()
@organization_access_required()
def get_organization_documents(organization_id):
    """Get all documents for an organization."""
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    
    # Query documents
    query = Document.query.filter_by(organization_id=organization_id)
    
    # Apply search filter
    if search:
        query = query.filter(Document.title.ilike(f'%{search}%'))
    
    # Paginate results
    documents = query.order_by(Document.created_at.desc()).paginate(page=page, per_page=per_page)
    
    # Format response
    result = {
        'documents': [doc.to_dict() for doc in documents.items],
        'pagination': {
            'page': documents.page,
            'per_page': documents.per_page,
            'total_pages': documents.pages,
            'total_items': documents.total
        }
    }
    
    return jsonify(result), 200


@document_bp.route('/organizations/<int:organization_id>/documents', methods=['POST'])
@jwt_required()
@organization_access_required()
def upload_document(organization_id):
    """Upload a document to an organization."""
    current_user_id = get_jwt_identity()
    
    # Check if file is provided
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    # Check if file is empty
    if file.filename == '':
        return jsonify({'error': 'Empty file provided'}), 400
    
    # Get document metadata
    title = request.form.get('title')
    description = request.form.get('description')
    
    # Validate required fields
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    
    # Upload document
    document, error = DocumentService.upload_document(
        file=file,
        title=title,
        organization_id=organization_id,
        user_id=current_user_id,
        description=description
    )
    
    if not document:
        return jsonify({'error': error}), 400
    
    # Queue document for analysis
    TaskService.process_document_async(document.id)
    
    # Log audit event
    log_audit_event('upload', 'document', document.id, {'title': title})
    
    return jsonify({
        'message': 'Document uploaded successfully',
        'document': document.to_dict()
    }), 201


@document_bp.route('/documents/<int:document_id>', methods=['GET'])
@jwt_required()
@document_access_required()
def get_document(document_id):
    """Get a document."""
    current_user_id = get_jwt_identity()
    
    # Get document
    document, error = DocumentService.get_document(document_id, current_user_id)
    
    if not document:
        return jsonify({'error': error}), 404
    
    return jsonify({
        'document': document.to_dict()
    }), 200


@document_bp.route('/documents/<int:document_id>/content', methods=['GET'])
@jwt_required()
@document_access_required()
def get_document_content(document_id):
    """Get document content."""
    current_user_id = get_jwt_identity()
    
    # Get document content
    content, file_type, error = DocumentService.get_document_content(document_id, current_user_id)
    
    if not content:
        return jsonify({'error': error}), 404
    
    # Get document for filename
    document, _ = DocumentService.get_document(document_id, current_user_id)
    
    # Set content type based on file type
    content_types = {
        'pdf': 'application/pdf',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'txt': 'text/plain'
    }
    content_type = content_types.get(file_type, 'application/octet-stream')
    
    # Create in-memory file
    file_io = io.BytesIO(content)
    
    # Return file
    return send_file(
        file_io,
        mimetype=content_type,
        as_attachment=True,
        download_name=f"{document.title}.{file_type}"
    )


@document_bp.route('/documents/<int:document_id>', methods=['PUT'])
@jwt_required()
@document_access_required(permission='edit')
def update_document(document_id):
    """Update a document."""
    current_user_id = get_jwt_identity()
    
    # Get document metadata
    title = request.form.get('title')
    description = request.form.get('description')
    
    # Check if file is provided
    file = request.files.get('file')
    
    # Update document
    document, error = DocumentService.update_document(
        document_id=document_id,
        user_id=current_user_id,
        title=title,
        description=description,
        file=file
    )
    
    if not document:
        return jsonify({'error': error}), 400
    
    # Log audit event
    log_audit_event('update', 'document', document_id, {'title': title})
    
    return jsonify({
        'message': 'Document updated successfully',
        'document': document.to_dict()
    }), 200


@document_bp.route('/documents/<int:document_id>', methods=['DELETE'])
@jwt_required()
@document_access_required(permission='edit')
def delete_document(document_id):
    """Delete a document."""
    current_user_id = get_jwt_identity()
    
    # Delete document
    success, error = DocumentService.delete_document(document_id, current_user_id)
    
    if not success:
        return jsonify({'error': error}), 400
    
    # Log audit event
    log_audit_event('delete', 'document', document_id)
    
    return jsonify({
        'message': 'Document deleted successfully'
    }), 200


@document_bp.route('/documents/<int:document_id>/share', methods=['POST'])
@jwt_required()
@document_access_required(permission='edit')
def share_document(document_id):
    """Share a document with a user."""
    current_user_id = get_jwt_identity()
    data = request.json
    
    # Validate required fields
    if not data or not data.get('user_id'):
        return jsonify({'error': 'User ID is required'}), 400
    
    # Share document
    document_share, error = DocumentService.share_document(
        document_id=document_id,
        user_id=current_user_id,
        target_user_id=data['user_id'],
        permission_level=data.get('permission_level', 'read')
    )
    
    if not document_share:
        return jsonify({'error': error}), 400
    
    # Log audit event
    log_audit_event('share', 'document', document_id, {'target_user_id': data['user_id']})
    
    return jsonify({
        'message': 'Document shared successfully',
        'document_share': document_share.to_dict()
    }), 201


@document_bp.route('/documents/<int:document_id>/share/<int:user_id>', methods=['DELETE'])
@jwt_required()
@document_access_required(permission='edit')
def unshare_document(document_id, user_id):
    """Unshare a document with a user."""
    current_user_id = get_jwt_identity()
    
    # Unshare document
    success, error = DocumentService.unshare_document(
        document_id=document_id,
        user_id=current_user_id,
        target_user_id=user_id
    )
    
    if not success:
        return jsonify({'error': error}), 400
    
    # Log audit event
    log_audit_event('unshare', 'document', document_id, {'target_user_id': user_id})
    
    return jsonify({
        'message': 'Document unshared successfully'
    }), 200


@document_bp.route('/documents/<int:document_id>/shares', methods=['GET'])
@jwt_required()
@document_access_required(permission='edit')
def get_document_shares(document_id):
    """Get all shares for a document."""
    # Get document shares
    shares = DocumentShare.query.filter_by(document_id=document_id).all()
    
    # Format response
    result = [share.to_dict() for share in shares]
    
    return jsonify({
        'shares': result
    }), 200


@document_bp.route('/users/me/shared-documents', methods=['GET'])
@jwt_required()
def get_shared_documents():
    """Get all documents shared with the current user."""
    current_user_id = get_jwt_identity()
    
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Get document shares
    shares = DocumentShare.query.filter_by(user_id=current_user_id).paginate(page=page, per_page=per_page)
    
    # Get documents
    documents = []
    for share in shares.items:
        document = Document.query.get(share.document_id)
        if document:
            doc_dict = document.to_dict()
            doc_dict['permission_level'] = share.permission_level
            documents.append(doc_dict)
    
    # Format response
    result = {
        'documents': documents,
        'pagination': {
            'page': shares.page,
            'per_page': shares.per_page,
            'total_pages': shares.pages,
            'total_items': shares.total
        }
    }
    
    return jsonify(result), 200

