from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User, UserRole
from app.models.proposal import Proposal, ProposalStatus
from app.models.review import Review
from app.services.auth_service import require_roles, get_current_user
from app.services.groq_service import GroqService
from datetime import datetime

bd_bp = Blueprint('bd', __name__)

@bd_bp.route('/proposals', methods=['GET'])
@jwt_required()
@require_roles([UserRole.BUSINESS_DEVELOPER])
def get_my_proposals():
    """Get current user's proposals with filtering and pagination"""
    try:
        user_id = get_jwt_identity()
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
        query = {'business_developer': user_id}
        if status and status in [s.value for s in ProposalStatus]:
            query['status'] = status
        
        if search:
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

@bd_bp.route('/proposals/<proposal_id>', methods=['GET'])
@jwt_required()
@require_roles([UserRole.BUSINESS_DEVELOPER])
def get_proposal_details(proposal_id):
    """Get detailed proposal information"""
    try:
        user_id = get_jwt_identity()
        
        proposal = Proposal.objects(id=proposal_id, business_developer=user_id).first()
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

@bd_bp.route('/proposals', methods=['POST'])
@jwt_required()
@require_roles([UserRole.BUSINESS_DEVELOPER])
def create_proposal():
    """Create a new proposal"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        title = data.get('title', '').strip()
        project_description = data.get('project_description', '').strip()
        
        if not title or not project_description:
            return jsonify({'error': 'Title and project description are required'}), 400
        
        if len(title) > 200:
            return jsonify({'error': 'Title must be less than 200 characters'}), 400
        
        if len(project_description) < 50:
            return jsonify({'error': 'Project description must be at least 50 characters'}), 400
        
        # Get current user
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Call GROQ API to generate JSON template
        try:
            groq_service = GroqService()
            json_content = groq_service.generate_proposal_template(project_description)
        except Exception as e:
            print(f"GROQ service error: {e}")
            # Use a basic template if GROQ fails
            json_content = {
                "introduction": "Thank you for posting this project...",
                "understanding": "Based on your requirements...",
                "proposed_solution": "I will deliver a comprehensive solution...",
                "timeline": "To be discussed",
                "budget": "Competitive pricing",
                "why_choose_us": "Experience and dedication"
            }
        
        # Create proposal
        proposal = Proposal(
            title=title,
            project_description=project_description,
            json_content=json_content,
            business_developer=user,
            status=ProposalStatus.DRAFT.value
        )
        proposal.save()
        
        return jsonify({
            'message': 'Proposal created successfully',
            'proposal': proposal.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Failed to create proposal: {str(e)}'}), 500

@bd_bp.route('/proposals/<proposal_id>', methods=['PUT'])
@jwt_required()
@require_roles([UserRole.BUSINESS_DEVELOPER])
def update_proposal(proposal_id):
    """Update an existing proposal"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        user_id = get_jwt_identity()
        
        proposal = Proposal.objects(id=proposal_id, business_developer=user_id).first()
        if not proposal:
            return jsonify({'error': 'Proposal not found'}), 404
        
        # Check if proposal can be edited
        if proposal.status not in [ProposalStatus.DRAFT.value, ProposalStatus.REVISION_REQUESTED.value]:
            return jsonify({'error': 'Proposal cannot be edited in current status'}), 400
        
        # Update fields
        if 'title' in data:
            title = data['title'].strip()
            if title:
                if len(title) > 200:
                    return jsonify({'error': 'Title must be less than 200 characters'}), 400
                proposal.title = title
        
        if 'project_description' in data:
            project_description = data['project_description'].strip()
            if project_description:
                if len(project_description) < 50:
                    return jsonify({'error': 'Project description must be at least 50 characters'}), 400
                proposal.project_description = project_description
        
        if 'json_content' in data:
            json_content = data['json_content']
            if isinstance(json_content, dict):
                proposal.json_content = json_content
        
        proposal.updated_at = datetime.utcnow()
        proposal.save()
        
        return jsonify({
            'message': 'Proposal updated successfully',
            'proposal': proposal.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to update proposal: {str(e)}'}), 500

@bd_bp.route('/proposals/<proposal_id>/submit', methods=['POST'])
@jwt_required()
@require_roles([UserRole.BUSINESS_DEVELOPER])
def submit_proposal(proposal_id):
    """Submit proposal for review"""
    try:
        user_id = get_jwt_identity()
        
        proposal = Proposal.objects(id=proposal_id, business_developer=user_id).first()
        if not proposal:
            return jsonify({'error': 'Proposal not found'}), 404
        
        # Check if proposal can be submitted
        if proposal.status not in [ProposalStatus.DRAFT.value, ProposalStatus.REVISION_REQUESTED.value]:
            return jsonify({'error': 'Proposal cannot be submitted in current status'}), 400
        
        # Validate proposal has required content
        if not proposal.json_content or not isinstance(proposal.json_content, dict):
            return jsonify({'error': 'Proposal content is incomplete'}), 400
        
        proposal.status = ProposalStatus.SUBMITTED.value
        proposal.updated_at = datetime.utcnow()
        proposal.save()
        
        return jsonify({
            'message': 'Proposal submitted for review',
            'proposal': proposal.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to submit proposal: {str(e)}'}), 500

@bd_bp.route('/proposals/<proposal_id>/reviews', methods=['GET'])
@jwt_required()
@require_roles([UserRole.BUSINESS_DEVELOPER])
def get_proposal_reviews(proposal_id):
    """Get all reviews for a proposal"""
    try:
        user_id = get_jwt_identity()
        
        # Verify proposal belongs to user
        proposal = Proposal.objects(id=proposal_id, business_developer=user_id).first()
        if not proposal:
            return jsonify({'error': 'Proposal not found'}), 404
        
        reviews = Review.objects(proposal=proposal).order_by('-created_at')
        return jsonify({
            'reviews': [review.to_dict() for review in reviews]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get reviews: {str(e)}'}), 500

@bd_bp.route('/proposals/<proposal_id>/revise', methods=['POST'])
@jwt_required()
@require_roles([UserRole.BUSINESS_DEVELOPER])
def revise_proposal(proposal_id):
    """Revise proposal based on feedback"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        bd_recommendations = data.get('bd_recommendations', '').strip()
        
        if not bd_recommendations:
            return jsonify({'error': 'BD recommendations are required'}), 400
        
        user_id = get_jwt_identity()
        
        proposal = Proposal.objects(id=proposal_id, business_developer=user_id).first()
        if not proposal:
            return jsonify({'error': 'Proposal not found'}), 404
        
        # Check if proposal is in revision_requested status
        if proposal.status != ProposalStatus.REVISION_REQUESTED.value:
            return jsonify({'error': 'Proposal is not pending revision'}), 400
        
        # Get latest review
        latest_review = Review.objects(proposal=proposal).order_by('-created_at').first()
        if not latest_review:
            return jsonify({'error': 'No reviews found for this proposal'}), 400
        
        # Update review with BD response
        latest_review.bd_response = bd_recommendations
        latest_review.updated_at = datetime.utcnow()
        latest_review.save()
        
        # Call GROQ API to regenerate JSON with recommendations
        try:
            groq_service = GroqService()
            new_json = groq_service.regenerate_proposal(
                proposal.json_content,
                latest_review.recommendations or "",
                bd_recommendations
            )
        except Exception as e:
            print(f"GROQ service error during revision: {e}")
            # If GROQ fails, keep current JSON but add revision notes
            new_json = proposal.json_content.copy()
            new_json['revision_notes'] = f"Revised based on feedback: {bd_recommendations}"
        
        # Update proposal with new JSON and increment version
        proposal.json_content = new_json
        proposal.current_version += 1
        proposal.status = ProposalStatus.DRAFT.value  # Reset to draft for further editing
        proposal.updated_at = datetime.utcnow()
        proposal.save()
        
        return jsonify({
            'message': 'Proposal revised successfully',
            'proposal': proposal.to_dict(),
            'review': latest_review.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to revise proposal: {str(e)}'}), 500

@bd_bp.route('/proposals/<proposal_id>/duplicate', methods=['POST'])
@jwt_required()
@require_roles([UserRole.BUSINESS_DEVELOPER])
def duplicate_proposal(proposal_id):
    """Create a copy of an existing proposal"""
    try:
        user_id = get_jwt_identity()
        
        original_proposal = Proposal.objects(id=proposal_id, business_developer=user_id).first()
        if not original_proposal:
            return jsonify({'error': 'Proposal not found'}), 404
        
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Create new proposal with copied content
        new_proposal = Proposal(
            title=f"Copy of {original_proposal.title}",
            project_description=original_proposal.project_description,
            json_content=original_proposal.json_content.copy(),
            business_developer=user,
            status=ProposalStatus.DRAFT.value
        )
        new_proposal.save()
        
        return jsonify({
            'message': 'Proposal duplicated successfully',
            'proposal': new_proposal.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Failed to duplicate proposal: {str(e)}'}), 500

@bd_bp.route('/proposals/<proposal_id>', methods=['DELETE'])
@jwt_required()
@require_roles([UserRole.BUSINESS_DEVELOPER])
def delete_proposal(proposal_id):
    """Delete a proposal (only if it's in draft status)"""
    try:
        user_id = get_jwt_identity()
        
        proposal = Proposal.objects(id=proposal_id, business_developer=user_id).first()
        if not proposal:
            return jsonify({'error': 'Proposal not found'}), 404
        
        # Only allow deletion of draft proposals
        if proposal.status != ProposalStatus.DRAFT.value:
            return jsonify({'error': 'Only draft proposals can be deleted'}), 400
        
        # Delete associated reviews first
        Review.objects(proposal=proposal).delete()
        
        # Delete the proposal
        proposal.delete()
        
        return jsonify({
            'message': 'Proposal deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to delete proposal: {str(e)}'}), 500

@bd_bp.route('/dashboard/stats', methods=['GET'])
@jwt_required()
@require_roles([UserRole.BUSINESS_DEVELOPER])
def get_bd_dashboard_stats():
    """Get dashboard statistics for business developer"""
    try:
        user_id = get_jwt_identity()
        
        # Get proposal counts by status
        proposal_stats = {}
        for status in ProposalStatus:
            count = Proposal.objects(business_developer=user_id, status=status.value).count()
            proposal_stats[status.value] = count
        
        # Get recent proposals
        recent_proposals = Proposal.objects(business_developer=user_id).order_by('-created_at').limit(5)
        
        # Get recent reviews
        user_proposals = Proposal.objects(business_developer=user_id)
        recent_reviews = Review.objects(proposal__in=user_proposals).order_by('-created_at').limit(5)
        
        # Get pending actions
        pending_revisions = Proposal.objects(
            business_developer=user_id, 
            status=ProposalStatus.REVISION_REQUESTED.value
        ).count()
        
        return jsonify({
            'proposal_stats': proposal_stats,
            'recent_proposals': [p.to_dict() for p in recent_proposals],
            'recent_reviews': [r.to_dict() for r in recent_reviews],
            'pending_actions': {
                'pending_revisions': pending_revisions
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get dashboard stats: {str(e)}'}), 500