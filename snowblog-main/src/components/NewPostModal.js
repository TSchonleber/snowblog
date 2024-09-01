import React, { useState } from 'react';
import api from '../api/axios';
import './NewPostModal.css';

function NewPostModal({ isOpen, onClose, onPostCreated }) {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [file, setFile] = useState(null);
  const [mediaUrl, setMediaUrl] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('title', title);
    formData.append('content', content);
    if (file) formData.append('file', file);
    formData.append('mediaUrl', mediaUrl);

    try {
      await api.post('/api/posts', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      onPostCreated();
      clearForm();
      onClose();
    } catch (error) {
      console.error('Error creating post:', error);
    }
  };

  const clearForm = () => {
    setTitle('');
    setContent('');
    setFile(null);
    setMediaUrl('');
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    const allowedTypes = ['image', 'video', 'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    
    if (selectedFile && allowedTypes.some(type => selectedFile.type.startsWith(type))) {
      setFile(selectedFile);
    } else {
      alert('Please select an image, video, or document file.');
      e.target.value = null;
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content cyberpunk-modal">
        <h2 className="modal-title glitch" data-text="Create New Post">Create New Post</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <input
              type="text"
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              placeholder="Enter title"
              className="cyberpunk-input"
            />
          </div>
          <div className="form-group">
            <textarea
              id="content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              required
              placeholder="Enter content"
              className="cyberpunk-textarea"
            />
          </div>
          <div className="form-group">
            <label htmlFor="file" className="cyberpunk-file-input">
              <span>Upload File (Image, Video, or Document)</span>
              <input
                type="file"
                id="file"
                onChange={handleFileChange}
                accept="image/*,video/*,.pdf,.doc,.docx"
              />
            </label>
            {file && <p className="file-name">{file.name}</p>}
          </div>
          <div className="form-group">
            <input
              type="url"
              id="mediaUrl"
              value={mediaUrl}
              onChange={(e) => setMediaUrl(e.target.value)}
              placeholder="Enter image or video URL"
              className="cyberpunk-input"
            />
          </div>
          <div className="button-group">
            <button type="submit" className="cyberpunk-button submit-button">Create Post</button>
            <button type="button" onClick={onClose} className="cyberpunk-button cancel-button">Cancel</button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default NewPostModal;