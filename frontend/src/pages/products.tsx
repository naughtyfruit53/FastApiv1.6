import React from 'react';
import { useRouter } from 'next/router';
import ProductManagement from './masters/products';

const ProductsPage: React.FC = () => {
  return <ProductManagement />;
};

export default ProductsPage;