import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Link, useLocation } from 'react-router-dom';

const Sidebar = () => {
  const { user, logout } = useAuth();
  const location = useLocation();

  const adminMenu = [
    { name: 'Dashboard', path: '/admin', icon: '📊' },
    { name: 'Proposals', path: '/admin/proposals', icon: '📝' },
    { name: 'BD Management', path: '/admin/bd-management', icon: '👥' }
  ];

  const bdMenu = [
    { name: 'Dashboard', path: '/bd', icon: '📊' },
    { name: 'My Proposals', path: '/bd/proposals', icon: '📝' },
    { name: 'New Proposal', path: '/bd/new-proposal', icon: '➕' }
  ];

  const menuItems = user?.role === 'admin' ? adminMenu : bdMenu;

  return (
    <div className="w-64 bg-background-light border-r border-gray-700 flex flex-col">
      <div className="p-6 border-b border-gray-700">
        <h1 className="text-xl font-bold text-white">Upwork Proposal Generator</h1>
        <p className="text-sm text-gray-400 mt-1">{user?.role === 'admin' ? 'Admin' : 'Business Developer'}</p>
      </div>
      
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {menuItems.map((item) => (
            <li key={item.path}>
              <Link
                to={item.path}
                className={`flex items-center px-4 py-3 rounded-lg transition-colors duration-200 ${
                  location.pathname === item.path
                    ? 'bg-primary text-white'
                    : 'text-gray-300 hover:bg-background-lighter hover:text-white'
                }`}
              >
                <span className="mr-3">{item.icon}</span>
                {item.name}
              </Link>
            </li>
          ))}
        </ul>
      </nav>
      
      <div className="p-4 border-t border-gray-700">
        <button
          onClick={logout}
          className="w-full flex items-center px-4 py-3 text-gray-300 hover:bg-background-lighter hover:text-white rounded-lg transition-colors duration-200"
        >
          <span className="mr-3">🚪</span>
          Logout
        </button>
      </div>
    </div>
  );
};

export default Sidebar;