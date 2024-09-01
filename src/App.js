import React, { useState, useRef, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './components/Login';
import SnowDump from './components/AIPage';
import ProfilePage from './components/ProfilePage';
import HomePage from './components/HomePage';
import NewPostModal from './components/NewPostModal';
import AboutMePopout from './components/AboutMePopout';
import UserIcon from './components/UserIcon';
import AdminPanel from './components/AdminPanel';
import FloatingChat from './components/FloatingChat';
import './App.css';

function AppContent() {
  const { user, logout } = useAuth();
  const [isNewPostModalOpen, setIsNewPostModalOpen] = useState(false);
  const [isAboutMeOpen, setIsAboutMeOpen] = useState(false);
  const aboutMeRef = useRef(null);
  const aboutMeButtonRef = useRef(null);

  useEffect(() => {
    const handleMouseLeave = (e) => {
      if (!aboutMeRef.current.contains(e.relatedTarget) && !aboutMeButtonRef.current.contains(e.relatedTarget)) {
        setIsAboutMeOpen(false);
      }
    };

    document.addEventListener('mouseleave', handleMouseLeave);

    return () => {
      document.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, []);

  console.log('Current user:', user);
  console.log('Is admin:', user?.is_admin);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Snow-Blog</h1>
        <nav>
          <Link to="/">Home</Link>
          {user ? (
            <>
              <Link to="/snow-dump">Snow-Dump</Link>
              <button onClick={() => setIsNewPostModalOpen(true)}>New Post</button>
              {user.is_admin && <Link to="/admin">Admin Panel</Link>}
              <button onClick={logout}>Logout</button>
              <UserIcon />
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
          <Route path="/snow-dump" element={<SnowDump />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/admin" element={<AdminPanel />} />
        </Routes>
      </main>

      <NewPostModal 
        isOpen={isNewPostModalOpen} 
        onClose={() => setIsNewPostModalOpen(false)}
        onPostCreated={() => {
          setIsNewPostModalOpen(false);
        }}
      />

      <div 
        ref={aboutMeRef} 
        className={`about-me-container ${isAboutMeOpen ? 'open' : ''}`}
        onMouseEnter={() => setIsAboutMeOpen(true)}
        onMouseLeave={() => setIsAboutMeOpen(false)}
      >
        <AboutMePopout 
          isOpen={isAboutMeOpen}
          onClose={() => setIsAboutMeOpen(false)}
        />
      </div>

      {user && <FloatingChat />}

      <button 
        ref={aboutMeButtonRef}
        className="about-me-button" 
        onMouseEnter={() => setIsAboutMeOpen(true)}
      >
        About Me
      </button>
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