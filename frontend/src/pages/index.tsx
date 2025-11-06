// frontend/src/pages/index.tsx
import { useRouter } from "next/router";
import { useEffect } from "react";

import { ProtectedPage } from '../components/ProtectedPage';
const Home = () => {
  const router = useRouter();
  useEffect(() => {
    // Redirect to login page immediately
    router.push("/login");
  }, [router]);
  return null; // Render nothing while redirecting
};

Home.getLayout = (page) => page;

export default Home;