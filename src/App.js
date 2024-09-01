import React, { useState, useRef, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Header from './components/Header';
import Login from './components/Login';
import SnowDump from './components/AIPage';
import PublicProfilePage from './components/PublicProfilePage';
import HomePage from './components/HomePage';
import NewPostModal from './components/NewPostModal';
import AboutMePopout from './components/AboutMePopout';
import AdminPanel from './components/AdminPanel';
import FloatingChat from './components/FloatingChat';
import './App.css';
import Settings from './components/Settings';

function AppContent() {
  const { user } = useAuth();
  const [isNewPostModalOpen, setIsNewPostModalOpen] = useState(false);
  const [isAboutMeOpen, setIsAboutMeOpen] = useState(false);
  const [refreshPosts, setRefreshPosts] = useState(false);
  const aboutMeRef = useRef(null);
  const aboutMeButtonRef = useRef(null);

  useEffect(() => {
    const handleMouseLeave = (e) => {
      if (!aboutMeRef.current?.contains(e.relatedTarget) && !aboutMeButtonRef.current?.contains(e.relatedTarget)) {
        setIsAboutMeOpen(false);
      }
    };

    document.addEventListener('mouseleave', handleMouseLeave);

    return () => {
      document.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, []);

  return (
    <div className="App">
      <Header />

      <main className="App-main">
        <Routes>
          <Route path="/" element={<HomePage refreshTrigger={refreshPosts} setRefreshPosts={setRefreshPosts} />} />
          <Route path="/login" element={<Login />} />
          <Route path="/snow-dump" element={<SnowDump />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/profile/:username" element={<PublicProfilePage />} />
          <Route path="/admin" element={<AdminPanel />} />
        </Routes>
      </main>

      {user && (
        <button 
          onClick={() => setIsNewPostModalOpen(true)} 
          className="new-post-button"
        >
          + New Post
        </button>
      )}

      <NewPostModal 
        isOpen={isNewPostModalOpen} 
        onClose={() => setIsNewPostModalOpen(false)}
        onPostCreated={() => {
          setIsNewPostModalOpen(false);
          setRefreshPosts(prev => !prev);
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
        className="about-me-button neon-text" 
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