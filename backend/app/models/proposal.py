from . import db
from enum import Enum

class ProposalStatus(Enum):
    DRAFT = 'draft'
    SUBMITTED = 'submitted'
    UNDER_REVIEW = 'under_review'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    REVISION_REQUESTED = 'revision_requested'

class Proposal(db.Document):
    title = db.StringField(required=True)
    project_description = db.StringField(required=True)
    json_content = db.DictField(required=True)  # GROQ-generated JSON template
    status = db.StringField(
        required=True, 
        choices=[status.value for status in ProposalStatus],
        default=ProposalStatus.DRAFT.value
    )
    business_developer = db.ReferenceField('User', required=True)
    current_version = db.IntField(default=1)
    created_at = db.DateTimeField(default=db.datetime.utcnow)
    updated_at = db.DateTimeField(default=db.datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'title': self.title,
            'project_description': self.project_description,
            'json_content': self.json_content,
            'status': self.status,
            'business_developer': str(self.business_developer.id),
            'current_version': self.current_version,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    meta = {
        'collection': 'proposals',
        'indexes': [
            'business_developer',
            'status',
            'created_at'
        ]
    }