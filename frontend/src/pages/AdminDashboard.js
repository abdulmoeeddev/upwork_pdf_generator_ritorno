import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import ProposalReview from '../components/admin/ProposalReview';
import BDManagement from '../components/admin/BDManagement';
import AdminOverview from '../components/admin/AdminOverview';

const AdminDashboard = () => {
  return (
    <div className="space-y-6">
      <Routes>
        <Route path="/" element={<AdminOverview />} />
        <Route path="/proposals" element={<ProposalReview />} />
        <Route path="/bd-management" element={<BDManagement />} />
        <Route path="*" element={<Navigate to="/admin" />} />
      </Routes>
    </div>
  );
};

export default AdminDashboard;