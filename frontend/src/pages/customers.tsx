import React from 'react';
import { useRouter } from 'next/router';
import CustomerManagement from './masters/customers';

const CustomersPage: React.FC = () => {
  return <CustomerManagement />;
};

export default CustomersPage;