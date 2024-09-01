import React, { useState } from 'react';
import api from '../api/axios';
import './EditPostModal.css';

function EditPostModal({ post, onClose, onEditComplete }) {
  const [title, setTitle] = useState(post.title);
  const [content, setContent] = useState(post.content);
  const [file, setFile] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('title', title);
    formData.append('content', content);
    if (file) formData.append('file', file);

    try {
      await api.put(`/api/posts/${post.id}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      onEditComplete();
    } catch (error) {
      console.error('Error updating post:', error);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content cyberpunk-modal">
        <h2 className="modal-title glitch" data-text="Edit Post">Edit Post</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              className="cyberpunk-input"
            />
          </div>
          <div className="form-group">
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              required
              className="cyberpunk-textarea"
            />
          </div>
          <div className="form-group">
            <input
              type="file"
              onChange={(e) => setFile(e.target.files[0])}
              className="cyberpunk-file-input"
            />
          </div>
          <div className="button-group">
            <button type="submit" className="cyberpunk-button submit-button">Update Post</button>
            <button type="button" onClick={onClose} className="cyberpunk-button cancel-button">Cancel</button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default EditPostModal;