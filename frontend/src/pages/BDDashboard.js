import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import BDOverview from '../components/bd/BDOverview';
import MyProposals from '../components/bd/MyProposals';
import NewProposal from '../components/bd/NewProposal';

const BDDashboard = () => {
  return (
    <div className="space-y-6">
      <Routes>
        <Route path="/" element={<BDOverview />} />
        <Route path="/proposals" element={<MyProposals />} />
        <Route path="/new-proposal" element={<NewProposal />} />
        <Route path="*" element={<Navigate to="/bd" />} />
      </Routes>
    </div>
  );
};

export default BDDashboard;