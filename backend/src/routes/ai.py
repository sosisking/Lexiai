from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models import db
from src.models.document import Document
from src.models.clause import Clause, ClauseCategory
from src.models.document_summary import DocumentSummary
from src.models.obligation import Obligation
from src.models.search_query import SearchQuery
from src.services.ai_service import AIService
from src.services.task_service import TaskService
from src.middleware.auth_middleware import document_access_required
from src.middleware.logging_middleware import log_audit_event

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/documents/<int:document_id>/analyze', methods=['POST'])
@jwt_required()
@document_access_required(permission='edit')
def analyze_document(document_id):
    """Analyze a document using AI."""
    # Get document
    document = Document.query.get(document_id)
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    
    # Check if document is already being analyzed
    if document.status == 'processing':
        return jsonify({'error': 'Document is already being processed'}), 400
    
    # Update document status
    document.status = 'queued'
    db.session.commit()
    
    # Queue document for analysis
    success = TaskService.process_document_async(document_id)
    
    if not success:
        document.status = 'error'
        db.session.commit()
        return jsonify({'error': 'Failed to queue document for analysis'}), 500
    
    # Log audit event
    log_audit_event('analyze', 'document', document_id)
    
    return jsonify({
        'message': 'Document analysis started',
        'document': document.to_dict()
    }), 202


@ai_bp.route('/documents/<int:document_id>/clauses', methods=['GET'])
@jwt_required()
@document_access_required()
def get_document_clauses(document_id):
    """Get all clauses for a document."""
    # Get query parameters
    category_id = request.args.get('category_id', type=int)
    risk_level = request.args.get('risk_level')
    
    # Query clauses
    query = Clause.query.filter_by(document_id=document_id)
    
    # Apply filters
    if category_id:
        query = query.filter_by(category_id=category_id)
    if risk_level:
        query = query.filter_by(risk_level=risk_level)
    
    # Get clauses
    clauses = query.all()
    
    # Format response
    result = [clause.to_dict() for clause in clauses]
    
    return jsonify({
        'clauses': result
    }), 200


@ai_bp.route('/documents/<int:document_id>/summary', methods=['GET'])
@jwt_required()
@document_access_required()
def get_document_summary(document_id):
    """Get summary for a document."""
    # Get summary
    summary = DocumentSummary.query.filter_by(document_id=document_id).first()
    
    if not summary:
        return jsonify({'error': 'Summary not found'}), 404
    
    return jsonify({
        'summary': summary.to_dict()
    }), 200


@ai_bp.route('/documents/<int:document_id>/obligations', methods=['GET'])
@jwt_required()
@document_access_required()
def get_document_obligations(document_id):
    """Get all obligations for a document."""
    # Get obligations
    obligations = Obligation.query.filter_by(document_id=document_id).all()
    
    # Format response
    result = [obligation.to_dict() for obligation in obligations]
    
    return jsonify({
        'obligations': result
    }), 200


@ai_bp.route('/documents/<int:document_id>/search', methods=['POST'])
@jwt_required()
@document_access_required()
def search_document(document_id):
    """Search a document for a specific query."""
    data = request.json
    
    # Validate required fields
    if not data or not data.get('query'):
        return jsonify({'error': 'Query is required'}), 400
    
    # Search document
    result = AIService.search_document(document_id, data['query'])
    
    if not result:
        return jsonify({'error': 'Failed to search document'}), 500
    
    # Log audit event
    log_audit_event('search', 'document', document_id, {'query': data['query']})
    
    return jsonify({
        'result': result
    }), 200


@ai_bp.route('/documents/<int:document_id>/search-history', methods=['GET'])
@jwt_required()
@document_access_required()
def get_search_history(document_id):
    """Get search history for a document."""
    # Get search history
    searches = SearchQuery.query.filter_by(document_id=document_id).order_by(SearchQuery.created_at.desc()).all()
    
    # Format response
    result = [search.to_dict() for search in searches]
    
    return jsonify({
        'searches': result
    }), 200


@ai_bp.route('/clause-categories', methods=['GET'])
@jwt_required()
def get_clause_categories():
    """Get all clause categories."""
    # Get categories
    categories = ClauseCategory.query.all()
    
    # Format response
    result = [category.to_dict() for category in categories]
    
    return jsonify({
        'categories': result
    }), 200

