import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import HomePage from './components/HomePage';
import NewPostPage from './components/NewPostPage';
import EditPostPage from './components/EditPostPage';
import AboutMePage from './components/AboutMePage';
import LoginPage from './components/LoginPage';
import RegisterPage from './components/RegisterPage';
import ForgotPasswordPage from './components/ForgotPasswordPage';
import './App.css';

function NavLinks() {
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return (
    <nav className="App-nav">
      <Link to="/" className="nav-link">Home</Link>
      {user && <Link to="/new-post" className="nav-link">New Post</Link>}
      <Link to="/about" className="nav-link">About Me</Link>
      {user ? (
        <button onClick={handleLogout} className="nav-link logout-btn">Logout</button>
      ) : (
        <>
          <Link to="/login" className="nav-link">Login</Link>
          <Link to="/register" className="nav-link">Register</Link>
        </>
      )}
    </nav>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <header className="App-header">
            <h1>Snow-dev</h1>
            <NavLinks />
          </header>
          <main className="App-main">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/new-post" element={<NewPostPage />} />
              <Route path="/edit-post/:id" element={<EditPostPage />} />
              <Route path="/about" element={<AboutMePage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/forgot-password" element={<ForgotPasswordPage />} />
            </Routes>
          </main>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;