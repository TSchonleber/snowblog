import React from 'react';
import { Link } from 'react-router-dom';
import './ExpandedPostModal.css';

function ExpandedPostModal({ post, onClose }) {
  if (!post) return null;

  return (
    <div className="expanded-post-overlay">
      <div className="expanded-post-modal">
        <button className="close-button" onClick={onClose}>&times;</button>
        <h2 className="post-title">{post.title}</h2>
        <p className="post-content">{post.content}</p>
        {post.file_url && (
          post.file_type === 'image' ? (
            <img src={post.file_url} alt={post.title} className="post-image" />
          ) : (
            <video src={post.file_url} controls className="post-video">
              Your browser does not support the video tag.
            </video>
          )
        )}
        <p className="post-author">
          Posted by: <Link to={`/profile/${post.author.username}`}>{post.author.display_name || post.author.username}</Link>
        </p>
        <p className="post-date">{new Date(post.created_at).toLocaleDateString()}</p>
      </div>
    </div>
  );
}

export default ExpandedPostModal;