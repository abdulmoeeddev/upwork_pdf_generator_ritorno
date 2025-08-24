import React, { useState, useEffect } from 'react';
import { adminAPI } from '../../services/api';

const AdminOverview = () => {
  const [stats, setStats] = useState({
    totalProposals: 0,
    pendingReview: 0,
    approved: 0,
    rejected: 0
  });

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const [proposalsRes] = await Promise.all([
        adminAPI.getProposals({ limit: 1000 })
      ]);

      const proposals = proposalsRes.data.proposals;
      const pendingReview = proposals.filter(p => p.status === 'submitted' || p.status === 'under_review').length;
      const approved = proposals.filter(p => p.status === 'approved').length;
      const rejected = proposals.filter(p => p.status === 'rejected').length;

      setStats({
        totalProposals: proposals.length,
        pendingReview,
        approved,
        rejected
      });
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-white mb-6">Admin Dashboard</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="card">
          <h3 className="text-lg font-semibold text-white mb-2">Total Proposals</h3>
          <p className="text-3xl font-bold text-primary">{stats.totalProposals}</p>
        </div>
        
        <div className="card">
          <h3 className="text-lg font-semibold text-white mb-2">Pending Review</h3>
          <p className="text-3xl font-bold text-yellow-500">{stats.pendingReview}</p>
        </div>
        
        <div className="card">
          <h3 className="text-lg font-semibold text-white mb-2">Approved</h3>
          <p className="text-3xl font-bold text-green-500">{stats.approved}</p>
        </div>
        
        <div className="card">
          <h3 className="text-lg font-semibold text-white mb-2">Rejected</h3>
          <p className="text-3xl font-bold text-red-500">{stats.rejected}</p>
        </div>
      </div>

      <div className="card">
        <h3 className="text-xl font-semibold text-white mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <a href="/admin/proposals" className="btn-primary text-center">
            Review Proposals
          </a>
          <a href="/admin/bd-management" className="btn-secondary text-center">
            Manage BD Accounts
          </a>
        </div>
      </div>
    </div>
  );
};

export default AdminOverview;