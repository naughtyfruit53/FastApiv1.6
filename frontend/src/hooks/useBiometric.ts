import { useState, useEffect } from 'react';

interface BiometricState {
  isAvailable: boolean;
  isSupported: boolean;
  authenticate: () => Promise<boolean>;
  error: string | null;
}

export function useBiometric(): BiometricState {
  const [isAvailable, setIsAvailable] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    checkBiometricAvailability();
  }, []);

  const checkBiometricAvailability = async () => {
    try {
      // Check if Web Authentication API is supported
      if (!window.PublicKeyCredential) {
        setIsSupported(false);
        return;
      }

      setIsSupported(true);

      // Check if platform authenticator is available
      const available = await window.PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable();
      setIsAvailable(available);
    } catch (err) {
      console.error('Error checking biometric availability:', err);
      setIsSupported(false);
      setIsAvailable(false);
    }
  };

  const authenticate = async (): Promise<boolean> => {
    if (!isAvailable || !isSupported) {
      setError('Biometric authentication is not available on this device');
      return false;
    }

    try {
      setError(null);

      // Generate challenge (in production, this should come from server)
      const challenge = new Uint8Array(32);
      crypto.getRandomValues(challenge);

      const publicKeyCredentialRequestOptions: PublicKeyCredentialRequestOptions = {
        challenge,
        timeout: 60000,
        userVerification: 'required',
        rpId: window.location.hostname,
      };

      const credential = await navigator.credentials.get({
        publicKey: publicKeyCredentialRequestOptions,
      }) as PublicKeyCredential | null;

      if (credential) {
        console.log('Biometric authentication successful');
        return true;
      }

      setError('Authentication failed');
      return false;
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Authentication failed';
      console.error('Biometric authentication error:', err);
      setError(errorMessage);
      return false;
    }
  };

  return {
    isAvailable,
    isSupported,
    authenticate,
    error,
  };
}
