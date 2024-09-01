import React from 'react';
import { NavLink, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import UserIcon from './UserIcon';
import './Header.css';

function Header() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      console.error('Logout failed', error);
    }
  };

  return (
    <header className="App-header">
      <div className="header-content">
        <div className="header-left">
          <Link to="/" className="site-title">
            <h1>Snow-Blog</h1>
          </Link>
        </div>
        <nav className="header-nav">
          <NavLink to="/snow-dump">Snow-Dump</NavLink>
          {user && user.is_admin && <NavLink to="/admin">Admin</NavLink>}
          {user ? (
            <>
              <NavLink to="/settings" className="settings-icon">⚙️</NavLink>
              <Link to={`/profile/${user.username}`} className="user-icon-link">
                <UserIcon />
              </Link>
              <button onClick={handleLogout} className="logout-button">Logout</button>
            </>
          ) : (
            <>
              <NavLink to="/login">Login</NavLink>
              <NavLink to="/register">Register</NavLink>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}

export default Header;