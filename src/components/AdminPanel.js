import React from 'react';
import AdminUserManagement from './AdminUserManagement';
import './AdminPanel.css'; // Create this file if it doesn't exist

const AdminPanel = () => {
  return (
    <div className="admin-panel">
      <h1>Admin Panel</h1>
      <div className="admin-section">
        <AdminUserManagement />
      </div>
      {/* Other admin panel sections */}
    </div>
  );
};

export default AdminPanel;