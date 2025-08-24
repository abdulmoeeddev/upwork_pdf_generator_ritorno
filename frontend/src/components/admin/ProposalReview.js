import React, { useState, useEffect } from 'react';
import { adminAPI } from '../../services/api';

const ProposalReview = () => {
  const [proposals, setProposals] = useState([]);
  const [selectedProposal, setSelectedProposal] = useState(null);
  const [reviewData, setReviewData] = useState({
    comments: '',
    status: '',
    recommendations: ''
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchProposals();
  }, []);

  const fetchProposals = async () => {
    try {
      const response = await adminAPI.getProposals({ status: 'submitted' });
      setProposals(response.data.proposals);
    } catch (error) {
      console.error('Failed to fetch proposals:', error);
    }
  };

  const handleReviewSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await adminAPI.reviewProposal(selectedProposal.id, reviewData);
      setSelectedProposal(null);
      setReviewData({ comments: '', status: '', recommendations: '' });
      fetchProposals();
      alert('Review submitted successfully!');
    } catch (error) {
      console.error('Failed to submit review:', error);
      alert('Failed to submit review');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-white mb-6">Proposal Review</h2>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-xl font-semibold text-white mb-4">Proposals Pending Review</h3>
          <div className="space-y-4">
            {proposals.map((proposal) => (
              <div key={proposal.id} className="border border-gray-600 rounded-lg p-4">
                <h4 className="text-lg font-medium text-white mb-2">{proposal.title}</h4>
                <p className="text-gray-400 text-sm mb-3 line-clamp-2">{proposal.project_description}</p>
                <button
                  onClick={() => setSelectedProposal(proposal)}
                  className="btn-primary text-sm"
                >
                  Review Proposal
                </button>
              </div>
            ))}
            
            {proposals.length === 0 && (
              <p className="text-gray-400 text-center py-8">No proposals pending review</p>
            )}
          </div>
        </div>

        {selectedProposal && (
          <div className="card">
            <h3 className="text-xl font-semibold text-white mb-4">Review Proposal</h3>
            <form onSubmit={handleReviewSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Comments
                </label>
                <textarea
                  value={reviewData.comments}
                  onChange={(e) => setReviewData({ ...reviewData, comments: e.target.value })}
                  className="input-field w-full h-32"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Status
                </label>
                <select
                  value={reviewData.status}
                  onChange={(e) => setReviewData({ ...reviewData, status: e.target.value })}
                  className="input-field w-full"
                  required
                >
                  <option value="">Select status</option>
                  <option value="approved">Approve</option>
                  <option value="rejected">Reject</option>
                  <option value="revision_requested">Request Revision</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Recommendations (Optional)
                </label>
                <textarea
                  value={reviewData.recommendations}
                  onChange={(e) => setReviewData({ ...reviewData, recommendations: e.target.value })}
                  className="input-field w-full h-24"
                />
              </div>

              <div className="flex space-x-4">
                <button
                  type="submit"
                  disabled={loading}
                  className="btn-primary flex-1 disabled:opacity-50"
                >
                  {loading ? 'Submitting...' : 'Submit Review'}
                </button>
                <button
                  type="button"
                  onClick={() => setSelectedProposal(null)}
                  className="btn-secondary flex-1"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProposalReview;