// frontend/src/pages/mail/index.tsx

import React from 'react';
import MailDashboard from './dashboard'; // Import the dashboard component
import { useAuth } from '../../context/AuthContext'; // Assume AuthContext provides user ID; adjust if different

const MailPage: React.FC = () => {
  const { user } = useAuth(); // Get current user from auth context

  if (!user) {
    return <div>Loading user...</div>; // Or redirect to login
  }

  return <MailDashboard userId={user.id} />; // Pass user ID to dashboard
};

export default MailPage;