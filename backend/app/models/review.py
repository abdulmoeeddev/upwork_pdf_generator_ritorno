from . import db

class Review(db.Document):
    proposal = db.ReferenceField('Proposal', required=True)
    reviewer = db.ReferenceField('User', required=True)
    comments = db.StringField(required=True)
    status = db.StringField(required=True, choices=['approved', 'rejected', 'revision_requested'])
    recommendations = db.StringField()  # Admin recommendations
    bd_response = db.StringField()  # BD's response to recommendations
    created_at = db.DateTimeField(default=db.datetime.utcnow)
    updated_at = db.DateTimeField(default=db.datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'proposal_id': str(self.proposal.id),
            'reviewer_id': str(self.reviewer.id),
            'reviewer_username': self.reviewer.username,
            'comments': self.comments,
            'status': self.status,
            'recommendations': self.recommendations,
            'bd_response': self.bd_response,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    meta = {
        'collection': 'reviews',
        'indexes': [
            'proposal',
            'reviewer',
            'created_at'
        ]
    }