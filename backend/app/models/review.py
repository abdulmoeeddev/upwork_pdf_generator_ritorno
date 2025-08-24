from mongoengine import Document, ReferenceField, StringField, DateTimeField
from datetime import datetime

class Review(Document):
    proposal = ReferenceField('Proposal', required=True, reverse_delete_rule=2)  # CASCADE
    reviewer = ReferenceField('User', required=True, reverse_delete_rule=2)  # CASCADE
    comments = StringField(required=True)
    status = StringField(
        required=True, 
        choices=['approved', 'rejected', 'revision_requested']
    )
    recommendations = StringField()  # Admin recommendations
    bd_response = StringField()      # BD's response to recommendations
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    def save(self, *args, **kwargs):
        """Override save to update timestamp"""
        if not self.created_at:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return super(Review, self).save(*args, **kwargs)

    def to_dict(self):
        """Convert review to dictionary representation"""
        return {
            'id': str(self.id),
            'proposal_id': str(self.proposal.id) if self.proposal else None,
            'proposal_title': self.proposal.title if self.proposal else None,
            'reviewer_id': str(self.reviewer.id) if self.reviewer else None,
            'reviewer_username': self.reviewer.username if self.reviewer else None,
            'comments': self.comments,
            'status': self.status,
            'recommendations': self.recommendations,
            'bd_response': self.bd_response,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def get_latest_for_proposal(cls, proposal):
        """Get the latest review for a proposal"""
        return cls.objects(proposal=proposal).order_by('-created_at').first()

    meta = {
        'collection': 'reviews',
        'indexes': [
            'proposal',
            'reviewer',
            'created_at',
            'status',
            ('proposal', 'created_at')
        ]
    }