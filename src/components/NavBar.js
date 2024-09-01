import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const NavBar = () => {
    const { isAuthenticated, isAdmin, user, logout } = useAuth();

    return (
        <nav>
            <Link to="/">Home</Link>
            <Link to="/snow-dump">Snow Dump</Link>
            {isAuthenticated ? (
                <>
                    <span>Welcome, {user.username}</span>
                    {isAdmin && <Link to="/admin">Admin Panel</Link>}
                    <button onClick={logout}>Logout</button>
                </>
            ) : (
                <Link to="/login">Login</Link>
            )}
        </nav>
    );
};

export default NavBar;