from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from io import BytesIO
from app.services.document_service import DocumentService
from app.models.user import User, UserRole
from app.models.proposal import Proposal, ProposalStatus
from app.services.auth_service import require_roles, get_current_user

documents_bp = Blueprint('documents', __name__)

@documents_bp.route('/proposals/<proposal_id>/preview/word', methods=['GET'])
@jwt_required()
def preview_proposal_word(proposal_id):
    """Generate Word document preview for proposal"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check access permissions
        if user.role == UserRole.BUSINESS_DEVELOPER.value:
            proposal = Proposal.objects(id=proposal_id, business_developer=user.id).first()
        else:  # Admin can access all proposals
            proposal = Proposal.objects(id=proposal_id).first()
        
        if not proposal:
            return jsonify({'error': 'Proposal not found'}), 404
        
        # Generate Word document
        try:
            doc_buffer = DocumentService.generate_word_document(
                proposal.json_content, 
                proposal.title
            )
            
            return send_file(
                doc_buffer,
                as_attachment=False,
                download_name=f'{proposal.title}_preview.docx',
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
        except Exception as e:
            return jsonify({'error': f'Failed to generate Word document: {str(e)}'}), 500
        
    except Exception as e:
        return jsonify({'error': f'Document generation failed: {str(e)}'}), 500

@documents_bp.route('/proposals/<proposal_id>/preview/pdf', methods=['GET'])
@jwt_required()
def preview_proposal_pdf(proposal_id):
    """Generate PDF document preview for proposal"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check access permissions
        if user.role == UserRole.BUSINESS_DEVELOPER.value:
            proposal = Proposal.objects(id=proposal_id, business_developer=user.id).first()
        else:  # Admin can access all proposals
            proposal = Proposal.objects(id=proposal_id).first()
        
        if not proposal:
            return jsonify({'error': 'Proposal not found'}), 404
        
        # Generate PDF document
        try:
            pdf_buffer = DocumentService.generate_pdf_document(
                proposal.json_content, 
                proposal.title
            )
            
            return send_file(
                pdf_buffer,
                as_attachment=False,
                download_name=f'{proposal.title}_preview.pdf',
                mimetype='application/pdf'
            )
        except Exception as e:
            return jsonify({'error': f'Failed to generate PDF document: {str(e)}'}), 500
        
    except Exception as e:
        return jsonify({'error': f'Document generation failed: {str(e)}'}), 500

@documents_bp.route('/proposals/<proposal_id>/download/word', methods=['GET'])
@jwt_required()
@require_roles([UserRole.BUSINESS_DEVELOPER])
def download_proposal_word(proposal_id):
    """Download Word document for approved proposal"""
    try:
        user_id = get_jwt_identity()
        
        proposal = Proposal.objects(id=proposal_id, business_developer=user_id).first()
        if not proposal:
            return jsonify({'error': 'Proposal not found'}), 404
        
        # Check if proposal is approved for download
        if proposal.status != ProposalStatus.APPROVED.value:
            return jsonify({'error': 'Only approved proposals can be downloaded'}), 400
        
        # Generate Word document
        try:
            doc_buffer = DocumentService.generate_word_document(
                proposal.json_content, 
                proposal.title
            )
            
            return send_file(
                doc_buffer,
                as_attachment=True,
                download_name=f'{proposal.title}_final.docx',
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
        except Exception as e:
            return jsonify({'error': f'Failed to generate Word document: {str(e)}'}), 500
        
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@documents_bp.route('/proposals/<proposal_id>/download/pdf', methods=['GET'])
@jwt_required()
@require_roles([UserRole.BUSINESS_DEVELOPER])
def download_proposal_pdf(proposal_id):
    """Download PDF document for approved proposal"""
    try:
        user_id = get_jwt_identity()
        
        proposal = Proposal.objects(id=proposal_id, business_developer=user_id).first()
        if not proposal:
            return jsonify({'error': 'Proposal not found'}), 404
        
        # Check if proposal is approved for download
        if proposal.status != ProposalStatus.APPROVED.value:
            return jsonify({'error': 'Only approved proposals can be downloaded'}), 400
        
        # Generate PDF document
        try:
            pdf_buffer = DocumentService.generate_pdf_document(
                proposal.json_content, 
                proposal.title
            )
            
            return send_file(
                pdf_buffer,
                as_attachment=True,
                download_name=f'{proposal.title}_final.pdf',
                mimetype='application/pdf'
            )
        except Exception as e:
            return jsonify({'error': f'Failed to generate PDF document: {str(e)}'}), 500
        
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@documents_bp.route('/proposals/<proposal_id>/template', methods=['GET'])
@jwt_required()
def get_proposal_template(proposal_id):
    """Get proposal JSON template for editing"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check access permissions
        if user.role == UserRole.BUSINESS_DEVELOPER.value:
            proposal = Proposal.objects(id=proposal_id, business_developer=user.id).first()
        else:  # Admin can access all proposals
            proposal = Proposal.objects(id=proposal_id).first()
        
        if not proposal:
            return jsonify({'error': 'Proposal not found'}), 404
        
        return jsonify({
            'template': proposal.json_content,
            'proposal_info': {
                'id': str(proposal.id),
                'title': proposal.title,
                'status': proposal.status,
                'version': proposal.current_version
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get template: {str(e)}'}), 500

@documents_bp.route('/proposals/<proposal_id>/template', methods=['PUT'])
@jwt_required()
@require_roles([UserRole.BUSINESS_DEVELOPER])
def update_proposal_template(proposal_id):
    """Update proposal JSON template"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        template = data.get('template')
        if not template or not isinstance(template, dict):
            return jsonify({'error': 'Valid template JSON is required'}), 400
        
        user_id = get_jwt_identity()
        
        proposal = Proposal.objects(id=proposal_id, business_developer=user_id).first()
        if not proposal:
            return jsonify({'error': 'Proposal not found'}), 404
        
        # Check if proposal can be edited
        editable_statuses = [ProposalStatus.DRAFT.value, ProposalStatus.REVISION_REQUESTED.value]
        if proposal.status not in editable_statuses:
            return jsonify({'error': 'Proposal cannot be edited in current status'}), 400
        
        # Update the template
        proposal.json_content = template
        proposal.save()
        
        return jsonify({
            'message': 'Template updated successfully',
            'template': proposal.json_content
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to update template: {str(e)}'}), 500

@documents_bp.route('/templates/default', methods=['GET'])
@jwt_required()
def get_default_template():
    """Get default proposal template structure"""
    try:
        default_template = {
            "introduction": "Thank you for posting this project. I have carefully reviewed your requirements and I am excited to work on this project.",
            "understanding": "Based on your project description, I understand that you need...",
            "proposed_solution": {
                "approach": "I will follow a systematic approach to deliver high-quality results:",
                "methodology": "My methodology includes thorough planning, regular communication, and quality assurance.",
                "deliverables": "You will receive complete, tested, and documented solution."
            },
            "timeline": {
                "phase_1": "Analysis and Planning - 2 days",
                "phase_2": "Implementation - 7-10 days", 
                "phase_3": "Testing and Refinement - 2-3 days",
                "phase_4": "Final Delivery - 1 day"
            },
            "budget": {
                "total": "Competitive pricing based on project scope",
                "payment_terms": "Milestone-based payments preferred",
                "value_proposition": "Quality work at reasonable rates"
            },
            "why_choose_us": "With extensive experience and commitment to quality, I ensure timely delivery and excellent communication throughout the project.",
            "portfolio_examples": "I have successfully completed similar projects with 100% client satisfaction. Portfolio examples available upon request.",
            "questions": "I would like to discuss the project requirements in more detail. Are there any specific preferences or constraints I should be aware of?"
        }
        
        return jsonify({
            'template': default_template
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get default template: {str(e)}'}), 500