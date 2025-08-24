import React, { useState, useEffect } from 'react';
import { bdAPI } from '../../services/api';

const BDOverview = () => {
  const [stats, setStats] = useState({
    totalProposals: 0,
    draft: 0,
    submitted: 0,
    approved: 0
  });

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await bdAPI.getProposals({ limit: 1000 });
      const proposals = response.data.proposals;
      
      setStats({
        totalProposals: proposals.length,
        draft: proposals.filter(p => p.status === 'draft').length,
        submitted: proposals.filter(p => p.status === 'submitted' || p.status === 'under_review').length,
        approved: proposals.filter(p => p.status === 'approved').length
      });
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-white mb-6">Business Developer Dashboard</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="card">
          <h3 className="text-lg font-semibold text-white mb-2">Total Proposals</h3>
          <p className="text-3xl font-bold text-primary">{stats.totalProposals}</p>
        </div>
        
        <div className="card">
          <h3 className="text-lg font-semibold text-white mb-2">Draft</h3>
          <p className="text-3xl font-bold text-yellow-500">{stats.draft}</p>
        </div>
        
        <div className="card">
          <h3 className="text-lg font-semibold text-white mb-2">Submitted</h3>
          <p className="text-3xl font-bold text-blue-500">{stats.submitted}</p>
        </div>
        
        <div className="card">
          <h3 className="text-lg font-semibold text-white mb-2">Approved</h3>
          <p className="text-3xl font-bold text-green-500">{stats.approved}</p>
        </div>
      </div>

      <div className="card">
        <h3 className="text-xl font-semibold text-white mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <a href="/bd/new-proposal" className="btn-primary text-center">
            Create New Proposal
          </a>
          <a href="/bd/proposals" className="btn-secondary text-center">
            View My Proposals
          </a>
        </div>
      </div>
    </div>
  );
};

export default BDOverview;