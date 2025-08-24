from mongoengine import Document, StringField, DictField, ReferenceField, IntField, DateTimeField
from enum import Enum
from datetime import datetime

class ProposalStatus(Enum):
    DRAFT = 'draft'
    SUBMITTED = 'submitted'
    UNDER_REVIEW = 'under_review'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    REVISION_REQUESTED = 'revision_requested'

class Proposal(Document):
    title = StringField(required=True, max_length=200)
    project_description = StringField(required=True)
    json_content = DictField(required=True)  # GROQ-generated JSON template
    status = StringField(
        required=True,
        choices=[status.value for status in ProposalStatus],
        default=ProposalStatus.DRAFT.value
    )
    business_developer = ReferenceField('User', required=True, reverse_delete_rule=2)  # CASCADE
    current_version = IntField(default=1, min_value=1)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    def save(self, *args, **kwargs):
        """Override save to update timestamp"""
        if not self.created_at:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return super(Proposal, self).save(*args, **kwargs)

    def to_dict(self):
        """Convert proposal to dictionary representation"""
        return {
            'id': str(self.id),
            'title': self.title,
            'project_description': self.project_description,
            'json_content': self.json_content,
            'status': self.status,
            'business_developer': str(self.business_developer.id) if self.business_developer else None,
            'business_developer_username': self.business_developer.username if self.business_developer else None,
            'current_version': self.current_version,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def get_by_id_and_user(cls, proposal_id, user_id):
        """Get proposal by ID for specific user"""
        return cls.objects(id=proposal_id, business_developer=user_id).first()

    meta = {
        'collection': 'proposals',
        'indexes': [
            'business_developer',
            'status',
            'created_at',
            ('business_developer', 'status'),
            ('business_developer', 'created_at')
        ]
    }