import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import { useAuth } from '../contexts/AuthContext';
import EditPostModal from './EditPostModal';
import './HomePage.css';

function HomePage({ refreshTrigger }) {
  const [posts, setPosts] = useState([]);
  const [editingPost, setEditingPost] = useState(null);
  const { user } = useAuth();

  useEffect(() => {
    fetchPosts();
  }, [refreshTrigger]);

  const fetchPosts = async () => {
    try {
      const response = await api.get('/api/posts');
      console.log('Fetched posts:', response.data);
      setPosts(response.data);
    } catch (error) {
      console.error('Error fetching posts:', error);
    }
  };

  const handleDelete = async (postId) => {
    if (window.confirm('Are you sure you want to delete this post?')) {
      try {
        await api.delete(`/api/posts/${postId}`);
        fetchPosts();
      } catch (error) {
        console.error('Error deleting post:', error);
      }
    }
  };

  const handleEdit = (post) => {
    setEditingPost(post);
  };

  const handleEditComplete = () => {
    setEditingPost(null);
    fetchPosts();
  };

  return (
    <div className="home-page">
      <h1 className="welcome-text">Welcome to Chaos</h1>
      <div className="posts-grid">
        {posts.length === 0 ? (
          <p>No posts found.</p>
        ) : (
          posts.map(post => (
            <div key={post.id} className="post-card">
              <h2 className="post-title">{post.title}</h2>
              <p className="post-content">{post.content}</p>
              {post.file_url && (
                <img src={post.file_url} alt="Post attachment" className="post-image" />
              )}
              {post.video_url && (
                <iframe
                  src={post.video_url}
                  title="Embedded video"
                  frameBorder="0"
                  allowFullScreen
                  className="post-video"
                ></iframe>
              )}
              <p className="post-date">Posted on: {new Date(post.created_at).toLocaleDateString()}</p>
              {user && (user.id === post.author_id || user.is_admin) && (
                <div className="post-actions">
                  <button onClick={() => handleEdit(post)} className="edit-button">Edit</button>
                  <button onClick={() => handleDelete(post.id)} className="delete-button">Delete</button>
                </div>
              )}
            </div>
          ))
        )}
      </div>
      {editingPost && (
        <EditPostModal
          post={editingPost}
          onClose={() => setEditingPost(null)}
          onEditComplete={handleEditComplete}
        />
      )}
    </div>
  );
}

export default HomePage;