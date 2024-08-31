import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './components/Login';
import SnowAI from './components/AIPage';
import ProfilePage from './components/ProfilePage';
import HomePage from './components/HomePage';
import NewPost from './components/NewPost';
import AboutMe from './components/AboutMe';
import './App.css';

function AppContent() {
  const { user, logout } = useAuth();

  return (
    <div className="App">
      <header className="App-header">
        <h1>Snow-Blog</h1>
        <nav>
          <Link to="/">Home</Link>
          {user ? (
            <>
              <Link to="/profile">Profile</Link>
              <Link to="/snow-ai">Snow-AI</Link>
              <Link to="/new-post">New Post</Link>
              <button onClick={logout}>Logout</button>
            </>
          ) : (
            <Link to="/login">Login</Link>
          )}
        </nav>
      </header>

      <main className="App-main">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<Login />} />
          <Route path="/snow-ai" element={<SnowAI />} />  // Changed from "/ai" to "/snow-ai" and AIPage to SnowAI
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/new-post" element={<NewPost />} />
        </Routes>
      </main>

      <aside className="App-sidebar">
        <AboutMe />
      </aside>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthProvider>
  );
}

export default App;