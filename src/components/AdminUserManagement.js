import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './AdminUserManagement.css'; // We'll create this file next

const AdminUserManagement = () => {
  const [users, setUsers] = useState([]);
  const [editingUser, setEditingUser] = useState(null);
  const [newPassword, setNewPassword] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await axios.get('/api/admin/users');
      setUsers(response.data);
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const handleEdit = (user) => {
    setEditingUser(user);
    setNewPassword('');
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    try {
      await axios.put(`/api/admin/users/${editingUser.id}`, editingUser);
      if (newPassword) {
        await axios.put(`/api/admin/users/${editingUser.id}/change-password`, { new_password: newPassword });
        setMessage('User updated and password changed successfully');
      } else {
        setMessage('User updated successfully');
      }
      setEditingUser(null);
      setNewPassword('');
      fetchUsers();
    } catch (error) {
      console.error('Error updating user:', error);
      setMessage('Error updating user');
    }
  };

  const handleDelete = async (userId) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      try {
        await axios.delete(`/api/admin/users/${userId}`);
        fetchUsers();
      } catch (error) {
        console.error('Error deleting user:', error);
      }
    }
  };

  return (
    <div className="admin-user-management">
      <h2>User Management</h2>
      {message && <div className="message">{message}</div>}
      <div className="user-table-container">
        <table className="user-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Username</th>
              <th>Email</th>
              <th>Admin</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id}>
                <td>{user.id}</td>
                <td>{user.username}</td>
                <td>{user.email}</td>
                <td>{user.is_admin ? 'Yes' : 'No'}</td>
                <td>
                  <button className="edit-btn" onClick={() => handleEdit(user)}>Edit</button>
                  <button className="delete-btn" onClick={() => handleDelete(user.id)}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {editingUser && (
        <div className="edit-user-form">
          <h3>Edit User</h3>
          <form onSubmit={handleUpdate}>
            <div className="form-group">
              <label>Username:</label>
              <input
                type="text"
                value={editingUser.username}
                onChange={(e) => setEditingUser({...editingUser, username: e.target.value})}
              />
            </div>
            <div className="form-group">
              <label>Email:</label>
              <input
                type="email"
                value={editingUser.email}
                onChange={(e) => setEditingUser({...editingUser, email: e.target.value})}
              />
            </div>
            <div className="form-group">
              <label>
                <input
                  type="checkbox"
                  checked={editingUser.is_admin}
                  onChange={(e) => setEditingUser({...editingUser, is_admin: e.target.checked})}
                />
                Admin
              </label>
            </div>
            <div className="form-group">
              <label>New Password:</label>
              <input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="Leave blank to keep current password"
              />
            </div>
            <div className="form-actions">
              <button type="submit" className="update-btn">Update</button>
              <button type="button" className="cancel-btn" onClick={() => setEditingUser(null)}>Cancel</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

export default AdminUserManagement;