import React, { useState, useEffect } from 'react';
import { adminAPI } from '../../services/api';

const BDManagement = () => {
  const [users, setUsers] = useState([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchBDUsers();
  }, []);

  const fetchBDUsers = async () => {
    try {
      const response = await adminAPI.getBDUsers();
      setUsers(response.data.users);
    } catch (error) {
      console.error('Failed to fetch BD users:', error);
    }
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await adminAPI.createBDUser(formData);
      setSuccess(`User created successfully! Password: ${response.data.password}`);
      setFormData({ username: '', email: '' });
      setShowCreateForm(false);
      fetchBDUsers();
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to create user');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-white">Business Developer Management</h2>
        <button
          onClick={() => setShowCreateForm(true)}
          className="btn-primary"
        >
          Add BD User
        </button>
      </div>

      {showCreateForm && (
        <div className="card mb-6">
          <h3 className="text-xl font-semibold text-white mb-4">Create New BD User</h3>
          
          {error && (
            <div className="bg-red-500/10 border border-red-500 text-red-500 px-4 py-3 rounded-lg mb-4">
              {error}
            </div>
          )}
          
          {success && (
            <div className="bg-green-500/10 border border-green-500 text-green-500 px-4 py-3 rounded-lg mb-4">
              {success}
            </div>
          )}

          <form onSubmit={handleCreateUser} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Username
              </label>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                className="input-field w-full"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Email
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                className="input-field w-full"
                required
              />
            </div>

            <div className="flex space-x-4">
              <button
                type="submit"
                disabled={loading}
                className="btn-primary flex-1 disabled:opacity-50"
              >
                {loading ? 'Creating...' : 'Create User'}
              </button>
              <button
                type="button"
                onClick={() => setShowCreateForm(false)}
                className="btn-secondary flex-1"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="card">
        <h3 className="text-xl font-semibold text-white mb-4">BD Users</h3>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-600">
                <th className="text-left py-3 px-4 text-gray-400">Username</th>
                <th className="text-left py-3 px-4 text-gray-400">Email</th>
                <th className="text-left py-3 px-4 text-gray-400">Status</th>
                <th className="text-left py-3 px-4 text-gray-400">Created</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id} className="border-b border-gray-600 hover:bg-background-lighter">
                  <td className="py-4 px-4 text-white font-medium">{user.username}</td>
                  <td className="py-4 px-4 text-gray-400">{user.email}</td>
                  <td className="py-4 px-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      user.is_active ? 'bg-green-500' : 'bg-red-500'
                    }`}>
                      {user.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="py-4 px-4 text-gray-400">
                    {new Date(user.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
              
              {users.length === 0 && (
                <tr>
                  <td colSpan="4" className="py-8 px-4 text-center text-gray-400">
                    No BD users found.
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

export default BDManagement;