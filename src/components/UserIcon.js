import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import './UserIcon.css';

function UserIcon() {
  const { user } = useAuth();

  if (!user) return null;

  return (
    <div className="user-icon">
      {user.avatar_url ? (
        <img 
          src={user.avatar_url} 
          alt={`${user.username}'s avatar`} 
          className="user-avatar"
        />
      ) : (
        <div className="user-icon-placeholder">
          {user.username.charAt(0).toUpperCase()}
        </div>
      )}
    </div>
  );
}

export default UserIcon;