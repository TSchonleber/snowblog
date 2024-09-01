import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import api from '../api/axios';

function ProfilePage() {
  const { user, updateUser } = useAuth();
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [email, setEmail] = useState(user ? user.email : '');
  const [username, setUsername] = useState(user ? user.username : '');
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (user) {
      setEmail(user.email);
      setUsername(user.username);
    }
  }, [user]);

  const handleChangePassword = async (e) => {
    e.preventDefault();
    try {
      const response = await api.post('/auth/change-password', { oldPassword, newPassword });
      setMessage(response.data.message);
      setOldPassword('');
      setNewPassword('');
    } catch (error) {
      setMessage(error.response?.data?.error || 'An error occurred');
    }
  };

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    try {
      const response = await api.put('/auth/update-profile', { email, username });
      updateUser(response.data.user);
      setMessage('Profile updated successfully');
    } catch (error) {
      setMessage(error.response?.data?.error || 'An error occurred');
    }
  };

  if (!user) {
    return <p>Please log in to view your profile.</p>;
  }

  return (
    <div className="profile-page">
      <h2>Profile</h2>
      <form onSubmit={handleUpdateProfile}>
        <div>
          <label>Username:</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Email:</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <button type="submit">Update Profile</button>
      </form>
      <h3>Change Password</h3>
      <form onSubmit={handleChangePassword}>
        <div>
          <label>Old Password:</label>
          <input
            type="password"
            value={oldPassword}
            onChange={(e) => setOldPassword(e.target.value)}
            required
          />
        </div>
        <div>
          <label>New Password:</label>
          <input
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit">Change Password</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
}

export default ProfilePage;