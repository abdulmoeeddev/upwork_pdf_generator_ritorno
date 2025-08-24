from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.user import User, UserRole
from ..models.proposal import Proposal, ProposalStatus
from ..models.review import Review
from ..services.auth_service import require_roles
from ..services.groq_service import GroqService

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/proposals', methods=['GET'])
@jwt_required()
@require_roles([UserRole.ADMIN])
def get_proposals():
    try:
        status = request.args.get('status')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        
        query = {}
        if status:
            query['status'] = status
        
        proposals = Proposal.objects(**query).order_by('-created_at').skip((page-1)*limit).limit(limit)
        total = Proposal.objects(**query).count()
        
        return jsonify({
            'proposals': [prop.to_dict() for prop in proposals],
            'total': total,
            'page': page,
            'limit': limit
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/proposals/<proposal_id>/review', methods=['POST'])
@jwt_required()
@require_roles([UserRole.ADMIN])
def review_proposal(proposal_id):
    try:
        data = request.get_json()
        comments = data.get('comments')
        status = data.get('status')
        recommendations = data.get('recommendations')
        
        if not comments or not status:
            return jsonify({'error': 'Comments and status are required'}), 400
        
        proposal = Proposal.objects(id=proposal_id).first()
        if not proposal:
            return jsonify({'error': 'Proposal not found'}), 404
        
        reviewer_id = get_jwt_identity()
        reviewer = User.objects(id=reviewer_id).first()
        
        # Create review
        review = Review(
            proposal=proposal,
            reviewer=reviewer,
            comments=comments,
            status=status,
            recommendations=recommendations
        )
        review.save()
        
        # Update proposal status
        proposal.status = status
        proposal.updated_at = db.datetime.utcnow()
        proposal.save()
        
        return jsonify({
            'review': review.to_dict(),
            'proposal': proposal.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/bd', methods=['POST'])
@jwt_required()
@require_roles([UserRole.ADMIN])
def create_bd_user():
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        
        if not username or not email:
            return jsonify({'error': 'Username and email are required'}), 400
        
        # Generate random password
        import secrets
        import string
        password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
        
        # Check if user already exists
        if User.objects(username=username).first() or User.objects(email=email).first():
            return jsonify({'error': 'User already exists'}), 400
        
        # Create user
        user = User(
            username=username,
            email=email,
            role=UserRole.BUSINESS_DEVELOPER.value
        )
        user.set_password(password)
        user.save()
        
        return jsonify({
            'user': user.to_dict(),
            'password': password  # Return plain password only once for admin to share
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/bd', methods=['GET'])
@jwt_required()
@require_roles([UserRole.ADMIN])
def get_bd_users():
    try:
        users = User.objects(role=UserRole.BUSINESS_DEVELOPER.value)
        return jsonify({'users': [user.to_dict() for user in users]}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500