import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import './ProfilePage.css';

function ProfilePage() {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editedProfile, setEditedProfile] = useState({});
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await axios.get('/api/user/profile');
      setProfile(response.data);
      setEditedProfile(response.data);
    } catch (error) {
      console.error('Error fetching profile:', error);
      setMessage('Error fetching profile. Please try again.');
    }
  };

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleCancel = () => {
    setIsEditing(false);
    setEditedProfile(profile);
  };

  const handleChange = (e) => {
    setEditedProfile({ ...editedProfile, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.put('/api/user/profile', editedProfile);
      setProfile(editedProfile);
      setIsEditing(false);
      setMessage('Profile updated successfully');
    } catch (error) {
      console.error('Error updating profile:', error);
      setMessage('Error updating profile. Please try again.');
    }
  };

  if (!user) return <p>Please log in to view your profile.</p>;
  if (!profile) return <div>Loading...</div>;

  return (
    <div className="profile-page">
      <h2>Your Profile</h2>
      {message && <div className="message">{message}</div>}
      {isEditing ? (
        <form onSubmit={handleSubmit}>
          <div>
            <label>Display Name:</label>
            <input
              type="text"
              name="displayName"
              value={editedProfile.displayName || ''}
              onChange={handleChange}
            />
          </div>
          <div>
            <label>Bio:</label>
            <textarea
              name="bio"
              value={editedProfile.bio || ''}
              onChange={handleChange}
            />
          </div>
          <div>
            <label>Location:</label>
            <input
              type="text"
              name="location"
              value={editedProfile.location || ''}
              onChange={handleChange}
            />
          </div>
          <div>
            <label>Website:</label>
            <input
              type="url"
              name="website"
              value={editedProfile.website || ''}
              onChange={handleChange}
            />
          </div>
          <button type="submit">Save Changes</button>
          <button type="button" onClick={handleCancel}>Cancel</button>
        </form>
      ) : (
        <div>
          <p><strong>Username:</strong> {profile.username}</p>
          <p><strong>Display Name:</strong> {profile.displayName || profile.username}</p>
          <p><strong>Email:</strong> {profile.email}</p>
          <p><strong>Bio:</strong> {profile.bio || 'No bio provided'}</p>
          <p><strong>Location:</strong> {profile.location || 'Not specified'}</p>
          <p><strong>Website:</strong> {profile.website ? <a href={profile.website} target="_blank" rel="noopener noreferrer">{profile.website}</a> : 'Not specified'}</p>
          <button onClick={handleEdit}>Edit Profile</button>
        </div>
      )}
      <div>
        <p>View your public profile: <a href={`/profile/${profile.username}`}>Public Profile</a></p>
      </div>
    </div>
  );
}

export default ProfilePage;