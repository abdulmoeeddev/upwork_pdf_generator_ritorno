import React from 'react';
import { useAuth } from '../contexts/AuthContext';

const Header = () => {
  const { user } = useAuth();

  return (
    <header className="bg-background-light border-b border-gray-700 p-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">
          Welcome back, {user?.username}!
        </h2>
        <div className="flex items-center space-x-4">
          <div className="text-right">
            <p className="text-white font-medium">{user?.username}</p>
            <p className="text-sm text-gray-400 capitalize">{user?.role?.replace('_', ' ')}</p>
          </div>
          <div className="w-10 h-10 bg-primary rounded-full flex items-center justify-center">
            <span className="text-white font-bold text-sm">
              {user?.username?.charAt(0).toUpperCase()}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;