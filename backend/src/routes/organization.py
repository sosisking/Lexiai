from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models import db
from src.models.user import User
from src.models.organization import Organization, OrganizationUser

organization_bp = Blueprint('organization', __name__)

@organization_bp.route('', methods=['GET'])
@jwt_required()
def get_organizations():
    """Get all organizations for the current user."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get all organizations where the user is a member
    org_users = OrganizationUser.query.filter_by(user_id=current_user_id).all()
    organizations = [org_user.organization for org_user in org_users]
    
    return jsonify({
        'organizations': [org.to_dict() for org in organizations]
    }), 200


@organization_bp.route('/<int:organization_id>', methods=['GET'])
@jwt_required()
def get_organization(organization_id):
    """Get a specific organization."""
    current_user_id = get_jwt_identity()
    
    # Check if organization exists
    organization = Organization.query.get(organization_id)
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    # Check if user is a member of the organization
    org_user = OrganizationUser.query.filter_by(
        organization_id=organization_id,
        user_id=current_user_id
    ).first()
    
    if not org_user:
        return jsonify({'error': 'Unauthorized access'}), 403
    
    return jsonify({
        'organization': organization.to_dict(),
        'role': org_user.role
    }), 200


@organization_bp.route('', methods=['POST'])
@jwt_required()
def create_organization():
    """Create a new organization."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.json
    
    # Validate required fields
    if not data or not data.get('name'):
        return jsonify({'error': 'Organization name is required'}), 400
    
    # Create new organization
    organization = Organization(name=data['name'])
    db.session.add(organization)
    db.session.flush()  # Flush to get the organization ID
    
    # Add current user as owner
    org_user = OrganizationUser(
        organization_id=organization.id,
        user_id=current_user_id,
        role='owner'
    )
    db.session.add(org_user)
    db.session.commit()
    
    return jsonify({
        'message': 'Organization created successfully',
        'organization': organization.to_dict()
    }), 201


@organization_bp.route('/<int:organization_id>', methods=['PUT'])
@jwt_required()
def update_organization(organization_id):
    """Update a specific organization."""
    current_user_id = get_jwt_identity()
    
    # Check if organization exists
    organization = Organization.query.get(organization_id)
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    # Check if user is an admin or owner of the organization
    org_user = OrganizationUser.query.filter_by(
        organization_id=organization_id,
        user_id=current_user_id
    ).first()
    
    if not org_user or not org_user.is_admin():
        return jsonify({'error': 'Unauthorized access'}), 403
    
    data = request.json
    
    # Update organization fields
    if 'name' in data:
        organization.name = data['name']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Organization updated successfully',
        'organization': organization.to_dict()
    }), 200


@organization_bp.route('/<int:organization_id>', methods=['DELETE'])
@jwt_required()
def delete_organization(organization_id):
    """Delete a specific organization."""
    current_user_id = get_jwt_identity()
    
    # Check if organization exists
    organization = Organization.query.get(organization_id)
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    # Check if user is an owner of the organization
    org_user = OrganizationUser.query.filter_by(
        organization_id=organization_id,
        user_id=current_user_id,
        role='owner'
    ).first()
    
    if not org_user:
        return jsonify({'error': 'Unauthorized access'}), 403
    
    db.session.delete(organization)
    db.session.commit()
    
    return jsonify({
        'message': 'Organization deleted successfully'
    }), 200


@organization_bp.route('/<int:organization_id>/users', methods=['GET'])
@jwt_required()
def get_organization_users(organization_id):
    """Get all users in an organization."""
    current_user_id = get_jwt_identity()
    
    # Check if organization exists
    organization = Organization.query.get(organization_id)
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    # Check if user is a member of the organization
    org_user = OrganizationUser.query.filter_by(
        organization_id=organization_id,
        user_id=current_user_id
    ).first()
    
    if not org_user:
        return jsonify({'error': 'Unauthorized access'}), 403
    
    # Get all users in the organization
    org_users = OrganizationUser.query.filter_by(organization_id=organization_id).all()
    users = []
    
    for ou in org_users:
        user = User.query.get(ou.user_id)
        if user:
            user_dict = user.to_dict()
            user_dict['role'] = ou.role
            users.append(user_dict)
    
    return jsonify({
        'users': users
    }), 200


@organization_bp.route('/<int:organization_id>/users', methods=['POST'])
@jwt_required()
def add_organization_user(organization_id):
    """Add a user to an organization."""
    current_user_id = get_jwt_identity()
    
    # Check if organization exists
    organization = Organization.query.get(organization_id)
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    # Check if user is an admin or owner of the organization
    org_user = OrganizationUser.query.filter_by(
        organization_id=organization_id,
        user_id=current_user_id
    ).first()
    
    if not org_user or not org_user.is_admin():
        return jsonify({'error': 'Unauthorized access'}), 403
    
    data = request.json
    
    # Validate required fields
    if not data or not data.get('user_id') or not data.get('role'):
        return jsonify({'error': 'User ID and role are required'}), 400
    
    # Check if user exists
    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check if user is already in the organization
    existing_org_user = OrganizationUser.query.filter_by(
        organization_id=organization_id,
        user_id=data['user_id']
    ).first()
    
    if existing_org_user:
        return jsonify({'error': 'User is already in the organization'}), 409
    
    # Add user to organization
    new_org_user = OrganizationUser(
        organization_id=organization_id,
        user_id=data['user_id'],
        role=data['role']
    )
    db.session.add(new_org_user)
    db.session.commit()
    
    return jsonify({
        'message': 'User added to organization successfully',
        'organization_user': new_org_user.to_dict()
    }), 201


@organization_bp.route('/<int:organization_id>/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_organization_user(organization_id, user_id):
    """Update a user's role in an organization."""
    current_user_id = get_jwt_identity()
    
    # Check if organization exists
    organization = Organization.query.get(organization_id)
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    # Check if user is an admin or owner of the organization
    org_user = OrganizationUser.query.filter_by(
        organization_id=organization_id,
        user_id=current_user_id
    ).first()
    
    if not org_user or not org_user.is_admin():
        return jsonify({'error': 'Unauthorized access'}), 403
    
    # Check if target user is in the organization
    target_org_user = OrganizationUser.query.filter_by(
        organization_id=organization_id,
        user_id=user_id
    ).first()
    
    if not target_org_user:
        return jsonify({'error': 'User is not in the organization'}), 404
    
    data = request.json
    
    # Validate required fields
    if not data or not data.get('role'):
        return jsonify({'error': 'Role is required'}), 400
    
    # Prevent changing the role of the last owner
    if target_org_user.role == 'owner' and data['role'] != 'owner':
        owners_count = OrganizationUser.query.filter_by(
            organization_id=organization_id,
            role='owner'
        ).count()
        
        if owners_count <= 1:
            return jsonify({'error': 'Cannot change the role of the last owner'}), 400
    
    # Update user's role
    target_org_user.role = data['role']
    db.session.commit()
    
    return jsonify({
        'message': 'User role updated successfully',
        'organization_user': target_org_user.to_dict()
    }), 200


@organization_bp.route('/<int:organization_id>/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def remove_organization_user(organization_id, user_id):
    """Remove a user from an organization."""
    current_user_id = get_jwt_identity()
    
    # Check if organization exists
    organization = Organization.query.get(organization_id)
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    # Check if user is an admin or owner of the organization
    org_user = OrganizationUser.query.filter_by(
        organization_id=organization_id,
        user_id=current_user_id
    ).first()
    
    if not org_user or not org_user.is_admin():
        return jsonify({'error': 'Unauthorized access'}), 403
    
    # Check if target user is in the organization
    target_org_user = OrganizationUser.query.filter_by(
        organization_id=organization_id,
        user_id=user_id
    ).first()
    
    if not target_org_user:
        return jsonify({'error': 'User is not in the organization'}), 404
    
    # Prevent removing the last owner
    if target_org_user.role == 'owner':
        owners_count = OrganizationUser.query.filter_by(
            organization_id=organization_id,
            role='owner'
        ).count()
        
        if owners_count <= 1:
            return jsonify({'error': 'Cannot remove the last owner'}), 400
    
    # Remove user from organization
    db.session.delete(target_org_user)
    db.session.commit()
    
    return jsonify({
        'message': 'User removed from organization successfully'
    }), 200

