import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import NewPostModal from './NewPostModal';
import ExpandedPostModal from './ExpandedPostModal';
import api from '../api/axios';
import './HomePage.css';

function HomePage({ refreshTrigger, setRefreshPosts }) {
  const [posts, setPosts] = useState([]);
  const [isNewPostModalOpen, setIsNewPostModalOpen] = useState(false);
  const [expandedPost, setExpandedPost] = useState(null);
  const { user } = useAuth();

  useEffect(() => {
    fetchPosts();
  }, [refreshTrigger]);

  const fetchPosts = async () => {
    try {
      console.log('Fetching posts...');
      const response = await api.get('/api/posts');
      console.log('Fetched posts:', response.data);
      setPosts(response.data);
    } catch (error) {
      console.error('Error fetching posts:', error);
    }
  };

  const openExpandedPost = (post) => {
    setExpandedPost(post);
  };

  const closeExpandedPost = () => {
    setExpandedPost(null);
  };

  return (
    <div className="home-page">
      <h1 className="welcome-text">Welcome to Chaos</h1>
      
      {user && (
        <button 
          onClick={() => setIsNewPostModalOpen(true)} 
          className="new-post-button"
        >
          + New Post
        </button>
      )}
      
      <div className="posts-grid">
        {posts.length === 0 ? (
          <p>No posts available.</p>
        ) : (
          posts.map(post => (
            <div key={post.id} className="post-card" onClick={() => openExpandedPost(post)}>
              <h2 className="post-title">{post.title}</h2>
              <p className="post-content">{post.content.substring(0, 100)}...</p>
              <p className="post-author">By: {post.author.display_name || post.author.username}</p>
              <p className="post-date">{new Date(post.created_at).toLocaleDateString()}</p>
            </div>
          ))
        )}
      </div>

      <NewPostModal 
        isOpen={isNewPostModalOpen} 
        onClose={() => setIsNewPostModalOpen(false)}
        onPostCreated={() => {
          setIsNewPostModalOpen(false);
          setRefreshPosts(prev => !prev);
        }}
      />

      <ExpandedPostModal 
        post={expandedPost}
        onClose={closeExpandedPost}
      />
    </div>
  );
}

export default HomePage;