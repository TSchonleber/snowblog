import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import './Settings.css';

function Settings() {
  const { user, updateUser } = useAuth();
  const [settings, setSettings] = useState(null);
  const [message, setMessage] = useState('');
  const [avatar, setAvatar] = useState(null);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await axios.get('/api/user/settings');
      setSettings(response.data);
    } catch (error) {
      console.error('Error fetching settings:', error);
      setMessage('Error fetching settings. Please try again.');
    }
  };

  const handleChange = (e) => {
    setSettings({ ...settings, [e.target.name]: e.target.value });
  };

  const handleAvatarChange = (e) => {
    setAvatar(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const formData = new FormData();
      Object.keys(settings).forEach(key => {
        formData.append(key, settings[key]);
      });
      if (avatar) {
        formData.append('avatar', avatar);
      }

      const response = await axios.put('/api/user/settings', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      setMessage('Settings updated successfully');
      updateUser(response.data.user);
    } catch (error) {
      console.error('Error updating settings:', error);
      setMessage('Error updating settings. Please try again.');
    }
  };

  if (!user) return <p>Please log in to view your settings.</p>;
  if (!settings) return <div>Loading...</div>;

  return (
    <div className="settings-page">
      <h2>Account Settings</h2>
      {message && <div className="message">{message}</div>}
      <form onSubmit={handleSubmit}>
        <div>
          <label>Email:</label>
          <input
            type="email"
            name="email"
            value={settings.email}
            onChange={handleChange}
          />
        </div>
        <div>
          <label>Password:</label>
          <input
            type="password"
            name="password"
            placeholder="Enter new password"
            onChange={handleChange}
          />
        </div>
        <div>
          <label>Avatar:</label>
          <input
            type="file"
            accept="image/*"
            onChange={handleAvatarChange}
          />
        </div>
        {settings.avatar_url && (
          <div className="current-avatar">
            <img src={settings.avatar_url} alt="Current avatar" />
          </div>
        )}
        <button type="submit">Save Changes</button>
      </form>
    </div>
  );
}

export default Settings;