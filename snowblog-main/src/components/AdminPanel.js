import React from 'react';
import UserManagement from './UserManagement';

function AdminPanel() {
  return (
    <div className="admin-panel">
      <h2>Admin Panel</h2>
      <UserManagement />
    </div>
  );
}

export default AdminPanel;