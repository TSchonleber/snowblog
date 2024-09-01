import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import ExpandedPostModal from './ExpandedPostModal';
import './PublicProfilePage.css';

function PublicProfilePage() {
  const { username } = useParams();
  const { user, updateUser } = useAuth();
  const [profile, setProfile] = useState(null);
  const [posts, setPosts] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [expandedPost, setExpandedPost] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editedProfile, setEditedProfile] = useState(null);
  const [avatar, setAvatar] = useState(null);
  const [avatarPreview, setAvatarPreview] = useState(null);
  const [updateMessage, setUpdateMessage] = useState('');

  const fetchPublicProfile = useCallback(async () => {
    try {
      const response = await axios.get(`/api/user/public-profile/${username}`);
      setProfile(response.data);
      setEditedProfile(response.data);
    } catch (error) {
      console.error('Error fetching public profile:', error);
      setError('Error fetching profile. Please try again.');
    }
  }, [username]);

  const fetchUserPosts = useCallback(async () => {
    try {
      const response = await axios.get(`/api/posts/user/${username}`);
      setPosts(response.data);
    } catch (error) {
      console.error('Error fetching user posts:', error);
    }
  }, [username]);

  useEffect(() => {
    setLoading(true);
    Promise.all([fetchPublicProfile(), fetchUserPosts()])
      .then(() => setLoading(false))
      .catch(() => setLoading(false));
  }, [fetchPublicProfile, fetchUserPosts]);

  const openExpandedPost = (post) => {
    setExpandedPost(post);
  };

  const closeExpandedPost = () => {
    setExpandedPost(null);
  };

  const handleEdit = () => {
    setIsEditing(true);
    setEditedProfile({...profile});
    setAvatarPreview(profile.avatar_url);
  };

  const handleChange = (e) => {
    setEditedProfile({ ...editedProfile, [e.target.name]: e.target.value });
  };

  const handleAvatarChange = (e) => {
    const file = e.target.files[0];
    setAvatar(file);
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setAvatarPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setUpdateMessage('');
    try {
      const formData = new FormData();
      Object.keys(editedProfile).forEach(key => {
        if (key !== 'display_name') { // Exclude display_name from the update
          formData.append(key, editedProfile[key]);
        }
      });
      if (avatar) {
        formData.append('avatar', avatar);
      }

      const response = await axios.put(`/api/user/public-profile/${username}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      setProfile(response.data);
      setIsEditing(false);
      if (user && user.username === username) {
        updateUser(response.data);
      }
      setUpdateMessage('Profile updated successfully!');
      setAvatar(null);
    } catch (error) {
      console.error('Error updating profile:', error);
      setUpdateMessage('Error updating profile. Please try again.');
    }
  };

  if (loading) return <div className="loading">Loading...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!profile) return <div className="error">Profile not found</div>;

  const isOwnProfile = user && user.username === username;

  return (
    <div className="public-profile-page">
      {updateMessage && <div className="update-message">{updateMessage}</div>}
      {isEditing ? (
        <form onSubmit={handleSubmit} className="edit-profile-form">
          <div className="avatar-upload">
            <img src={avatarPreview || '/default-avatar.png'} alt="Avatar preview" className="avatar-preview" />
            <input
              type="file"
              accept="image/*"
              onChange={handleAvatarChange}
              id="avatar-upload"
            />
            <label htmlFor="avatar-upload" className="avatar-upload-label">
              Change Avatar
            </label>
          </div>
          <div className="form-group">
            <label htmlFor="display_name">Display Name:</label>
            <input
              type="text"
              id="display_name"
              name="display_name"
              value={profile.display_name || profile.username}
              readOnly
              className="read-only-input"
            />
          </div>
          <div className="form-group">
            <label htmlFor="bio">Bio:</label>
            <textarea
              id="bio"
              name="bio"
              value={editedProfile.bio || ''}
              onChange={handleChange}
            />
          </div>
          <div className="form-group">
            <label htmlFor="location">Location:</label>
            <input
              type="text"
              id="location"
              name="location"
              value={editedProfile.location || ''}
              onChange={handleChange}
            />
          </div>
          <div className="form-group">
            <label htmlFor="website">Website:</label>
            <input
              type="url"
              id="website"
              name="website"
              value={editedProfile.website || ''}
              onChange={handleChange}
            />
          </div>
          <div className="form-actions">
            <button type="submit" className="save-button">Save Changes</button>
            <button type="button" onClick={() => setIsEditing(false)} className="cancel-button">Cancel</button>
          </div>
        </form>
      ) : (
        <>
          <div className="profile-header">
            <div className="profile-picture">
              <img src={profile.avatar_url || '/default-avatar.png'} alt={`${profile.username}'s avatar`} />
            </div>
            <div className="profile-info">
              <h2>{profile.display_name || profile.username}'s Profile</h2>
              <p><strong>Bio:</strong> {profile.bio || 'No bio provided'}</p>
              <p><strong>Location:</strong> {profile.location || 'Not specified'}</p>
              {profile.website && (
                <p><strong>Website:</strong> <a href={profile.website} target="_blank" rel="noopener noreferrer">{profile.website}</a></p>
              )}
              <p><strong>Member since:</strong> {profile.created_at ? new Date(profile.created_at).toLocaleDateString() : 'Unknown'}</p>
            </div>
          </div>
          {isOwnProfile && (
            <button onClick={handleEdit} className="edit-profile-button">Edit Profile</button>
          )}
        </>
      )}
      <div className="user-posts">
        <h3>Recent Posts</h3>
        {posts.length > 0 ? (
          <ul className="post-list">
            {posts.map(post => (
              <li key={post.id} className="post-item">
                <span className="post-title" onClick={() => openExpandedPost(post)}>{post.title}</span>
                <span className="post-date">{new Date(post.created_at).toLocaleDateString()}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p>No posts yet.</p>
        )}
      </div>
      {expandedPost && (
        <ExpandedPostModal
          post={expandedPost}
          onClose={closeExpandedPost}
        />
      )}
    </div>
  );
}

export default PublicProfilePage;