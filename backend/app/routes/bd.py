from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.user import User, UserRole
from ..models.proposal import Proposal, ProposalStatus
from ..models.review import Review
from ..services.auth_service import require_roles
from ..services.groq_service import GroqService

bd_bp = Blueprint('bd', __name__)

@bd_bp.route('/proposals', methods=['GET'])
@jwt_required()
@require_roles([UserRole.BUSINESS_DEVELOPER])
def get_my_proposals():
    try:
        user_id = get_jwt_identity()
        status = request.args.get('status')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        
        query = {'business_developer': user_id}
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

@bd_bp.route('/proposals', methods=['POST'])
@jwt_required()
@require_roles([UserRole.BUSINESS_DEVELOPER])
def create_proposal():
    try:
        data = request.get_json()
        title = data.get('title')
        project_description = data.get('project_description')
        
        if not title or not project_description:
            return jsonify({'error': 'Title and project description are required'}), 400
        
        # Call GROQ API to generate JSON template
        groq_service = GroqService()
        json_content = groq_service.generate_proposal_template(project_description)
        
        user_id = get_jwt_identity()
        user = User.objects(id=user_id).first()
        
        proposal = Proposal(
            title=title,
            project_description=project_description,
            json_content=json_content,
            business_developer=user,
            status=ProposalStatus.DRAFT.value
        )
        proposal.save()
        
        return jsonify({'proposal': proposal.to_dict()}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bd_bp.route('/proposals/<proposal_id>', methods=['PUT'])
@jwt_required()
@require_roles([UserRole.BUSINESS_DEVELOPER])
def update_proposal(proposal_id):
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        proposal = Proposal.objects(id=proposal_id, business_developer=user_id).first()
        if not proposal:
            return jsonify({'error': 'Proposal not found'}), 404
        
        if 'title' in data:
            proposal.title = data['title']
        if 'project_description' in data:
            proposal.project_description = data['project_description']
        if 'json_content' in data:
            proposal.json_content = data['json_content']
        
        proposal.updated_at = db.datetime.utcnow()
        proposal.save()
        
        return jsonify({'proposal': proposal.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bd_bp.route('/proposals/<proposal_id>/submit', methods=['POST'])
@jwt_required()
@require_roles([UserRole.BUSINESS_DEVELOPER])
def submit_proposal(proposal_id):
    try:
        user_id = get_jwt_identity()
        
        proposal = Proposal.objects(id=proposal_id, business_developer=user_id).first()
        if not proposal:
            return jsonify({'error': 'Proposal not found'}), 404
        
        proposal.status = ProposalStatus.SUBMITTED.value
        proposal.updated_at = db.datetime.utcnow()
        proposal.save()
        
        return jsonify({'proposal': proposal.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bd_bp.route('/proposals/<proposal_id>/reviews', methods=['GET'])
@jwt_required()
@require_roles([UserRole.BUSINESS_DEVELOPER])
def get_proposal_reviews(proposal_id):
    try:
        user_id = get_jwt_identity()
        
        # Verify proposal belongs to user
        proposal = Proposal.objects(id=proposal_id, business_developer=user_id).first()
        if not proposal:
            return jsonify({'error': 'Proposal not found'}), 404
        
        reviews = Review.objects(proposal=proposal).order_by('-created_at')
        return jsonify({'reviews': [review.to_dict() for review in reviews]}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bd_bp.route('/proposals/<proposal_id>/revise', methods=['POST'])
@jwt_required()
@require_roles([UserRole.BUSINESS_DEVELOPER])
def revise_proposal(proposal_id):
    try:
        data = request.get_json()
        bd_recommendations = data.get('bd_recommendations')
        
        user_id = get_jwt_identity()
        
        proposal = Proposal.objects(id=proposal_id, business_developer=user_id).first()
        if not proposal:
            return jsonify({'error': 'Proposal not found'}), 404
        
        # Get latest review
        latest_review = Review.objects(proposal=proposal).order_by('-created_at').first()
        if not latest_review:
            return jsonify({'error': 'No reviews found for this proposal'}), 400
        
        # Update review with BD response
        latest_review.bd_response = bd_recommendations
        latest_review.save()
        
        # Call GROQ API to regenerate JSON with recommendations
        groq_service = GroqService()
        new_json = groq_service.regenerate_proposal(
            proposal.json_content,
            latest_review.recommendations,
            bd_recommendations
        )
        
        # Update proposal with new JSON and increment version
        proposal.json_content = new_json
        proposal.current_version += 1
        proposal.status = ProposalStatus.REVISION_REQUESTED.value
        proposal.updated_at = db.datetime.utcnow()
        proposal.save()
        
        return jsonify({
            'proposal': proposal.to_dict(),
            'review': latest_review.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500