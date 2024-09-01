import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Link } from 'react-router-dom';

function UserIcon() {
  const { user } = useAuth();

  if (!user) return null;

  return (
    <Link to="/profile" className="user-icon">
      <div className="user-avatar">
        {user.username.charAt(0).toUpperCase()}
      </div>
      <span className="user-name">{user.username}</span>
    </Link>
  );
}

export default UserIcon;