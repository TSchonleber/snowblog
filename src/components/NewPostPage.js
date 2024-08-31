import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

function NewPostPage() {
  const [newPost, setNewPost] = useState({ title: '', content: '', file: null, videoUrl: '' });
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { user } = useAuth();

  // Redirect if not authenticated
  if (!user) {
    navigate('/login');
    return null;
  }

  const handleInputChange = (e) => {
    if (e.target.name === 'file') {
      setNewPost({ ...newPost, file: e.target.files[0] });
    } else {
      setNewPost({ ...newPost, [e.target.name]: e.target.value });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    const formData = new FormData();
    formData.append('title', newPost.title);
    if (newPost.content) formData.append('content', newPost.content);
    if (newPost.videoUrl) formData.append('videoUrl', newPost.videoUrl);
    if (newPost.file) formData.append('file', newPost.file);

    try {
      const response = await fetch('http://localhost:5000/api/posts', {
        method: 'POST',
        body: formData,
        credentials: 'include'
      });
      if (response.ok) {
        navigate('/');
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'An error occurred while creating the post.');
      }
    } catch (error) {
      console.error('Error creating post:', error);
      setError('An error occurred while creating the post.');
    }
  };

  return (
    <div className="new-post-page">
      <h2>Create a New Post</h2>
      {error && <p className="error-message">{error}</p>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="title">Title:</label>
          <input
            type="text"
            id="title"
            name="title"
            value={newPost.title}
            onChange={handleInputChange}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="content">Content:</label>
          <textarea
            id="content"
            name="content"
            value={newPost.content}
            onChange={handleInputChange}
          />
        </div>
        <div className="form-group">
          <label htmlFor="file">Upload File:</label>
          <input
            type="file"
            id="file"
            name="file"
            onChange={handleInputChange}
          />
        </div>
        <div className="form-group">
          <label htmlFor="videoUrl">Video URL:</label>
          <input
            type="text"
            id="videoUrl"
            name="videoUrl"
            value={newPost.videoUrl}
            onChange={handleInputChange}
          />
        </div>
        <button type="submit" className="submit-btn">Create Post</button>
      </form>
    </div>
  );
}

export default NewPostPage;