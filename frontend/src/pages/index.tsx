import { useRouter } from "next/router"; // Changed to correct import for Pages Router
import { useEffect } from "react";
export default function Home(): null {
  const router = useRouter();
  useEffect(() => {
    // Redirect to login page immediately
    router.push("/login");
  }, [router]);
  return null; // Render nothing while redirecting
}