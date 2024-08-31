import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

function HomePage() {
  const { user } = useAuth();
  const [posts, setPosts] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetchPosts();
  }, []);

  const fetchPosts = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/posts');
      const data = await response.json();
      setPosts(data);
    } catch (error) {
      console.error('Error fetching posts:', error);
    }
  };

  const handleDelete = async (postId) => {
    if (window.confirm('Are you sure you want to delete this post?')) {
      try {
        const response = await fetch(`http://localhost:5000/api/posts/${postId}`, {
          method: 'DELETE',
        });
        if (response.ok) {
          fetchPosts(); // Refresh the posts after deletion
        }
      } catch (error) {
        console.error('Error deleting post:', error);
      }
    }
  };

  const renderContent = (post) => {
    if (post.file_type === 'image') {
      return <img src={post.file_url} alt={post.title} className="post-image" />;
    } else if (post.file_type === 'video') {
      return <video src={post.file_url} controls className="post-video" />;
    } else if (post.file_type === 'audio') {
      return <audio src={post.file_url} controls className="post-audio" />;
    } else if (post.file_type === 'document') {
      return <a href={post.file_url} target="_blank" rel="noopener noreferrer">View Document</a>;
    } else if (post.video_url && post.video_url.includes('youtube.com/embed/')) {
      return (
        <iframe
          src={post.video_url}
          frameBorder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
          title={post.title}
        ></iframe>
      );
    }
    return <p>{post.content}</p>;
  };

  return (
    <div className="home-page">
      {posts.map(post => (
        <article key={post.id} className="post">
          <h3>{post.title}</h3>
          <div className="post-content">
            {renderContent(post)}
          </div>
          <p className="post-date">Created at: {new Date(post.created_at).toLocaleString()}</p>
          {user && (
            <div className="post-actions">
              <button onClick={() => navigate(`/edit-post/${post.id}`)} className="edit-btn">Edit</button>
              <button onClick={() => handleDelete(post.id)} className="delete-btn">Delete</button>
            </div>
          )}
        </article>
      ))}
    </div>
  );
}

export default HomePage;