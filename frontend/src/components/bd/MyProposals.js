import React, { useState, useEffect } from 'react';
import { bdAPI, documentsAPI } from '../../services/api';

const MyProposals = () => {
  const [proposals, setProposals] = useState([]);
  const [selectedProposal, setSelectedProposal] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchProposals();
  }, []);

  const fetchProposals = async () => {
    try {
      const response = await bdAPI.getProposals();
      setProposals(response.data.proposals);
    } catch (error) {
      console.error('Failed to fetch proposals:', error);
    }
  };

  const handlePreview = async (proposalId) => {
    try {
      const response = await documentsAPI.previewProposal(proposalId);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      window.open(url, '_blank');
    } catch (error) {
      console.error('Failed to preview proposal:', error);
    }
  };

  const handleDownload = async (proposalId, title) => {
    try {
      const response = await documentsAPI.downloadProposal(proposalId);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${title}_proposal.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Failed to download proposal:', error);
      alert('Proposal must be approved before download');
    }
  };

  const handleSubmit = async (proposalId) => {
    setLoading(true);
    try {
      await bdAPI.submitProposal(proposalId);
      fetchProposals();
      alert('Proposal submitted for review!');
    } catch (error) {
      console.error('Failed to submit proposal:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusColors = {
      draft: 'bg-gray-500',
      submitted: 'bg-blue-500',
      under_review: 'bg-yellow-500',
      approved: 'bg-green-500',
      rejected: 'bg-red-500',
      revision_requested: 'bg-orange-500'
    };

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[status]}`}>
        {status.replace('_', ' ')}
      </span>
    );
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-white mb-6">My Proposals</h2>
      
      <div className="card">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-600">
                <th className="text-left py-3 px-4 text-gray-400">Title</th>
                <th className="text-left py-3 px-4 text-gray-400">Status</th>
                <th className="text-left py-3 px-4 text-gray-400">Created</th>
                <th className="text-left py-3 px-4 text-gray-400">Actions</th>
              </tr>
            </thead>
            <tbody>
              {proposals.map((proposal) => (
                <tr key={proposal.id} className="border-b border-gray-600 hover:bg-background-lighter">
                  <td className="py-4 px-4">
                    <div className="text-white font-medium">{proposal.title}</div>
                    <div className="text-gray-400 text-sm mt-1 line-clamp-2">
                      {proposal.project_description}
                    </div>
                  </td>
                  <td className="py-4 px-4">
                    {getStatusBadge(proposal.status)}
                  </td>
                  <td className="py-4 px-4 text-gray-400">
                    {new Date(proposal.created_at).toLocaleDateString()}
                  </td>
                  <td className="py-4 px-4">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handlePreview(proposal.id)}
                        className="btn-secondary text-sm"
                      >
                        Preview
                      </button>
                      {proposal.status === 'draft' && (
                        <button
                          onClick={() => handleSubmit(proposal.id)}
                          disabled={loading}
                          className="btn-primary text-sm"
                        >
                          Submit
                        </button>
                      )}
                      {proposal.status === 'approved' && (
                        <button
                          onClick={() => handleDownload(proposal.id, proposal.title)}
                          className="btn-primary text-sm"
                        >
                          Download
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
              
              {proposals.length === 0 && (
                <tr>
                  <td colSpan="4" className="py-8 px-4 text-center text-gray-400">
                    No proposals found. <a href="/bd/new-proposal" className="text-primary hover:underline">Create your first proposal</a>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default MyProposals;