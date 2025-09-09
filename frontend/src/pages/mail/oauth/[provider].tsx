import { useRouter } from 'next/router';
import { useEffect, useState } from 'react';
import api from '../../../lib/api'; // Adjust path if needed

const OAuthInitiatePage = () => {
  const router = useRouter();
  const { provider } = router.query;
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    const initiateFlow = async () => {
      if (provider) {
        try {
          const response = await api.post(`/oauth/login/${provider as string}`, {});
          const { authorization_url, state } = response.data;
          localStorage.setItem(`oauth_provider_${state}`, provider as string);
          window.location.href = authorization_url;
        } catch (err: any) {
          console.error('Failed to initiate OAuth:', err);
          setErrorMessage(err.response?.data?.detail || 'Failed to initiate OAuth flow. Please check your configuration and try again.');
          setLoading(false);
        }
      }
    };
    initiateFlow();
  }, [provider]);

  if (loading) {
    return <div>Loading...</div>;
  }

  return <div>{errorMessage || 'Error initiating OAuth. Please try again.'}</div>;
};

export default OAuthInitiatePage;