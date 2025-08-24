import React, { useState } from 'react';
import { bdAPI } from '../../services/api';
import { useNavigate } from 'react-router-dom';

const NewProposal = () => {
  const [formData, setFormData] = useState({
    title: '',
    project_description: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await bdAPI.createProposal(formData);
      navigate('/bd/proposals');
      alert('Proposal created successfully!');
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to create proposal');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-white mb-6">Create New Proposal</h2>
      
      <div className="card">
        {error && (
          <div className="bg-red-500/10 border border-red-500 text-red-500 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-gray-300 mb-2">
              Proposal Title
            </label>
            <input
              type="text"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              className="input-field w-full"
              placeholder="Enter proposal title"
              required
            />
          </div>

          <div>
            <label htmlFor="project_description" className="block text-sm font-medium text-gray-300 mb-2">
              Project Description
            </label>
            <textarea
              id="project_description"
              name="project_description"
              value={formData.project_description}
              onChange={handleChange}
              className="input-field w-full h-32"
              placeholder="Describe the project in detail..."
              required
            />
          </div>

          <div className="flex space-x-4">
            <button
              type="submit"
              disabled={loading}
              className="btn-primary flex-1 disabled:opacity-50"
            >
              {loading ? 'Creating...' : 'Create Proposal'}
            </button>
            <button
              type="button"
              onClick={() => navigate('/bd/proposals')}
              className="btn-secondary flex-1"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default NewProposal;