import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

export const authAPI = {
  login: (credentials) => axios.post(`${API_BASE_URL}/auth/login`, credentials),
  getProfile: () => axios.get(`${API_BASE_URL}/auth/profile`)
};

export const adminAPI = {
  getProposals: (params) => axios.get(`${API_BASE_URL}/admin/proposals`, { params }),
  reviewProposal: (proposalId, data) => axios.post(`${API_BASE_URL}/admin/proposals/${proposalId}/review`, data),
  createBDUser: (data) => axios.post(`${API_BASE_URL}/admin/users/bd`, data),
  getBDUsers: () => axios.get(`${API_BASE_URL}/admin/users/bd`)
};

export const bdAPI = {
  getProposals: (params) => axios.get(`${API_BASE_URL}/bd/proposals`, { params }),
  createProposal: (data) => axios.post(`${API_BASE_URL}/bd/proposals`, data),
  updateProposal: (proposalId, data) => axios.put(`${API_BASE_URL}/bd/proposals/${proposalId}`, data),
  submitProposal: (proposalId) => axios.post(`${API_BASE_URL}/bd/proposals/${proposalId}/submit`),
  getProposalReviews: (proposalId) => axios.get(`${API_BASE_URL}/bd/proposals/${proposalId}/reviews`),
  reviseProposal: (proposalId, data) => axios.post(`${API_BASE_URL}/bd/proposals/${proposalId}/revise`, data)
};

export const documentsAPI = {
  previewProposal: (proposalId) => axios.get(`${API_BASE_URL}/documents/proposals/${proposalId}/preview`, {
    responseType: 'blob'
  }),
  downloadProposal: (proposalId) => axios.get(`${API_BASE_URL}/documents/proposals/${proposalId}/download`, {
    responseType: 'blob'
  })
};