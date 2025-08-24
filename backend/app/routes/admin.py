from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User, UserRole
from app.models.proposal import Proposal, ProposalStatus
from app.models.review import Review
from app.services.auth_service import require_roles, get_current_user
from app.services.groq_service import GroqService
from datetime import datetime
import secrets
import string

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/proposals', methods=['GET'])
@jwt_required()
@require_roles([UserRole.ADMIN])
def get_proposals():
    """Get all proposals with filtering and pagination"""
    try:
        status = request.args.get('status')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        search = request.args.get('search', '').strip()
        
        # Validate pagination
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 10
        
        # Build query
        query = {}
        if status and status in [s.value for s in ProposalStatus]:
            query['status'] = status
        
        if search:
            # Search in title and project description
            query['$or'] = [
                {'title__icontains': search},
                {'project_description__icontains': search}
            ]
        
        # Get proposals with pagination
        skip = (page - 1) * limit
        proposals = Proposal.objects(**query).order_by('-created_at').skip(skip).limit(limit)
        total = Proposal.objects(**query).count()
        
        # Calculate pagination info
        total_pages = (total + limit - 1) // limit
        has_next = page < total_pages
        has_prev = page > 1
        
        return jsonify({
            'proposals': [prop.to_dict() for prop in proposals],
            'pagination': {
                'total': total,
                'page': page,
                'limit': limit,
                'total_pages': total_pages,
                'has_next': has_next,
                'has_prev': has_prev
            }
        }), 200
        
    except ValueError as e:
        return jsonify({'error': f'Invalid parameter: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to get proposals: {str(e)}'}), 500

@admin_bp.route('/proposals/<proposal_id>', methods=['GET'])
@jwt_required()
@require_roles([UserRole.ADMIN])
def get_proposal_details(proposal_id):
    """Get detailed proposal information"""
    try:
        proposal = Proposal.objects(id=proposal_id).first()
        if not proposal:
            return jsonify({'error': 'Proposal not found'}), 404
        
        # Get reviews for this proposal
        reviews = Review.objects(proposal=proposal).order_by('-created_at')
        
        return jsonify({
            'proposal': proposal.to_dict(),
            'reviews': [review.to_dict() for review in reviews]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get proposal details: {str(e)}'}), 500

@admin_bp.route('/proposals/<proposal_id>/review', methods=['POST'])
@jwt_required()
@require_roles([UserRole.ADMIN])
def review_proposal(proposal_id):
    """Submit a review for a proposal"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        comments = data.get('comments', '').strip()
        status = data.get('status', '').strip()
        recommendations = data.get('recommendations', '').strip()
        
        if not comments or not status:
            return jsonify({'error': 'Comments and status are required'}), 400
        
        # Validate status
        valid_statuses = ['approved', 'rejected', 'revision_requested']
        if status not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400
        
        proposal = Proposal.objects(id=proposal_id).first()
        if not proposal:
            return jsonify({'error': 'Proposal not found'}), 404
        
        reviewer = get_current_user()
        if not reviewer:
            return jsonify({'error': 'Reviewer not found'}), 404
        
        # Create review
        review = Review(
            proposal=proposal,
            reviewer=reviewer,
            comments=comments,
            status=status,
            recommendations=recommendations
        )
        review.save()
        
        # Update proposal status based on review
        if status == 'approved':
            proposal.status = ProposalStatus.APPROVED.value
        elif status == 'rejected':
            proposal.status = ProposalStatus.REJECTED.value
        elif status == 'revision_requested':
            proposal.status = ProposalStatus.REVISION_REQUESTED.value
        
        proposal.updated_at = datetime.utcnow()
        proposal.save()
        
        return jsonify({
            'message': 'Review submitted successfully',
            'review': review.to_dict(),
            'proposal': proposal.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Failed to submit review: {str(e)}'}), 500

@admin_bp.route('/users/bd', methods=['POST'])
@jwt_required()
@require_roles([UserRole.ADMIN])
def create_bd_user():
    """Create a new Business Developer user"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        
        if not username or not email:
            return jsonify({'error': 'Username and email are required'}), 400
        
        # Generate random password
        password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
        
        # Check if user already exists
        if User.objects(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        if User.objects(email=email).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create user
        user = User(
            username=username,
            email=email,
            role=UserRole.BUSINESS_DEVELOPER.value
        )
        user.set_password(password)
        user.save()
        
        return jsonify({
            'message': 'Business Developer created successfully',
            'user': user.to_dict(),
            'temporary_password': password  # Return plain password only once for admin to share
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Failed to create BD user: {str(e)}'}), 500

@admin_bp.route('/users/bd', methods=['GET'])
@jwt_required()
@require_roles([UserRole.ADMIN])
def get_bd_users():
    """Get all Business Developer users"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        search = request.args.get('search', '').strip()
        
        # Validate pagination
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 10
        
        # Build query
        query = {'role': UserRole.BUSINESS_DEVELOPER.value}
        if search:
            query['$or'] = [
                {'username__icontains': search},
                {'email__icontains': search}
            ]
        
        # Get users with pagination
        skip = (page - 1) * limit
        users = User.objects(**query).order_by('-created_at').skip(skip).limit(limit)
        total = User.objects(**query).count()
        
        # Calculate pagination info
        total_pages = (total + limit - 1) // limit
        has_next = page < total_pages
        has_prev = page > 1
        
        return jsonify({
            'users': [user.to_dict() for user in users],
            'pagination': {
                'total': total,
                'page': page,
                'limit': limit,
                'total_pages': total_pages,
                'has_next': has_next,
                'has_prev': has_prev
            }
        }), 200
        
    except ValueError as e:
        return jsonify({'error': f'Invalid parameter: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to get BD users: {str(e)}'}), 500

@admin_bp.route('/users/<user_id>/toggle-status', methods=['PUT'])
@jwt_required()
@require_roles([UserRole.ADMIN])
def toggle_user_status(user_id):
    """Toggle user active status"""
    try:
        user = User.objects(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Don't allow deactivating admin users
        if user.role == UserRole.ADMIN.value:
            return jsonify({'error': 'Cannot deactivate admin users'}), 400
        
        user.is_active = not user.is_active
        user.save()
        
        status = "activated" if user.is_active else "deactivated"
        return jsonify({
            'message': f'User {status} successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to toggle user status: {str(e)}'}), 500

@admin_bp.route('/dashboard/stats', methods=['GET'])
@jwt_required()
@require_roles([UserRole.ADMIN])
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        # Get proposal counts by status
        proposal_stats = {}
        for status in ProposalStatus:
            count = Proposal.objects(status=status.value).count()
            proposal_stats[status.value] = count
        
        # Get user counts
        total_users = User.objects().count()
        bd_users = User.objects(role=UserRole.BUSINESS_DEVELOPER.value).count()
        admin_users = User.objects(role=UserRole.ADMIN.value).count()
        active_users = User.objects(is_active=True).count()
        
        # Get recent activity
        recent_proposals = Proposal.objects().order_by('-created_at').limit(5)
        recent_reviews = Review.objects().order_by('-created_at').limit(5)
        
        return jsonify({
            'proposal_stats': proposal_stats,
            'user_stats': {
                'total_users': total_users,
                'bd_users': bd_users,
                'admin_users': admin_users,
                'active_users': active_users
            },
            'recent_activity': {
                'recent_proposals': [p.to_dict() for p in recent_proposals],
                'recent_reviews': [r.to_dict() for r in recent_reviews]
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get dashboard stats: {str(e)}'}), 500