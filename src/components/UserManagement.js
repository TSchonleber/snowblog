import React, { useState, useEffect } from 'react';
import api from '../api/axios';

function UserManagement() {
  const [users, setUsers] = useState([]);
  const [pendingUsers, setPendingUsers] = useState([]);

  useEffect(() => {
    fetchUsers();
    fetchPendingUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await api.get('/api/users');
      setUsers(response.data);
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const fetchPendingUsers = async () => {
    try {
      const response = await api.get('/auth/pending-users');
      setPendingUsers(response.data);
    } catch (error) {
      console.error('Error fetching pending users:', error);
    }
  };

  const approveUser = async (userId) => {
    try {
      await api.post(`/auth/approve-user/${userId}`);
      fetchUsers();
      fetchPendingUsers();
    } catch (error) {
      console.error('Error approving user:', error);
    }
  };

  const toggleAdminStatus = async (userId, currentStatus) => {
    try {
      await api.put(`/api/users/${userId}`, { is_admin: !currentStatus });
      fetchUsers();
    } catch (error) {
      console.error('Error toggling admin status:', error);
    }
  };

  const deleteUser = async (userId) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      try {
        await api.delete(`/api/users/${userId}`);
        fetchUsers();
      } catch (error) {
        console.error('Error deleting user:', error);
      }
    }
  };

  return (
    <div className="user-management">
      <h3>Pending Users</h3>
      <ul>
        {pendingUsers.map(user => (
          <li key={user.id}>
            {user.username} - {user.email}
            <button onClick={() => approveUser(user.id)}>Approve</button>
          </li>
        ))}
      </ul>

      <h3>Approved Users</h3>
      <ul>
        {users.map(user => (
          <li key={user.id}>
            {user.username} - {user.email}
            <button onClick={() => toggleAdminStatus(user.id, user.is_admin)}>
              {user.is_admin ? 'Remove Admin' : 'Make Admin'}
            </button>
            <button onClick={() => deleteUser(user.id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default UserManagement;