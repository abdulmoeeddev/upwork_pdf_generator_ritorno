from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from io import BytesIO
import document_generator
from ..models.user import User, UserRole
from ..models.proposal import Proposal
from ..services.auth_service import require_roles

documents_bp = Blueprint('documents', __name__)

@documents_bp.route('/proposals/<proposal_id>/preview', methods=['GET'])
@jwt_required()
def preview_proposal(proposal_id):
    try:
        user_id = get_jwt_identity()
        user = User.objects(id=user_id).first()
        
        if user.role == UserRole.BUSINESS_DEVELOPER.value:
            proposal = Proposal.objects(id=proposal_id, business_developer=user_id).first()
        else:
            proposal = Proposal.objects(id=proposal_id).first()
        
        if not proposal:
            return jsonify({'error': 'Proposal not found'}), 404
        
        # Generate Word document
        doc_buffer = document_generator.generate_word_document(proposal.json_content)
        
        return send_file(
            BytesIO(doc_buffer.getvalue()),
            as_attachment=False,
            download_name=f'{proposal.title}_preview.docx',
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@documents_bp.route('/proposals/<proposal_id>/download', methods=['GET'])
@jwt_required()
@require_roles([UserRole.BUSINESS_DEVELOPER])
def download_proposal(proposal_id):
    try:
        user_id = get_jwt_identity()
        
        proposal = Proposal.objects(id=proposal_id, business_developer=user_id).first()
        if not proposal:
            return jsonify({'error': 'Proposal not found'}), 404
        
        if proposal.status != ProposalStatus.APPROVED.value:
            return jsonify({'error': 'Proposal must be approved before download'}), 400
        
        # Generate PDF document
        pdf_buffer = document_generator.generate_pdf_document(proposal.json_content)
        
        return send_file(
            BytesIO(pdf_buffer.getvalue()),
            as_attachment=True,
            download_name=f'{proposal.title}_proposal.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500