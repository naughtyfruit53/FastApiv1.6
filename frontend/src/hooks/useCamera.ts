import { useState, useRef, useCallback } from 'react';

interface CameraState {
  isSupported: boolean;
  isActive: boolean;
  stream: MediaStream | null;
  error: string | null;
  startCamera: (facingMode?: 'user' | 'environment') => Promise<void>;
  stopCamera: () => void;
  capturePhoto: () => Promise<Blob | null>;
  switchCamera: () => Promise<void>;
}

export function useCamera(): CameraState {
  const [isActive, setIsActive] = useState(false);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [facingMode, setFacingMode] = useState<'user' | 'environment'>('environment');
  const videoRef = useRef<HTMLVideoElement | null>(null);

  const isSupported = 'mediaDevices' in navigator && 'getUserMedia' in navigator.mediaDevices;

  const startCamera = useCallback(async (mode: 'user' | 'environment' = 'environment') => {
    if (!isSupported) {
      setError('Camera is not supported on this device');
      return;
    }

    try {
      setError(null);
      setFacingMode(mode);

      const constraints: MediaStreamConstraints = {
        video: {
          facingMode: mode,
          width: { ideal: 1920 },
          height: { ideal: 1080 },
        },
        audio: false,
      };

      const mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
      setStream(mediaStream);
      setIsActive(true);

      // If there's a video element, set the stream
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to access camera';
      console.error('Camera error:', err);
      setError(errorMessage);
      setIsActive(false);
    }
  }, [isSupported]);

  const stopCamera = useCallback(() => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      setStream(null);
      setIsActive(false);

      if (videoRef.current) {
        videoRef.current.srcObject = null;
      }
    }
  }, [stream]);

  const capturePhoto = useCallback(async (): Promise<Blob | null> => {
    if (!stream || !videoRef.current) {
      setError('Camera is not active');
      return null;
    }

    try {
      const canvas = document.createElement('canvas');
      const video = videoRef.current;

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      const context = canvas.getContext('2d');
      if (!context) {
        throw new Error('Failed to get canvas context');
      }

      context.drawImage(video, 0, 0, canvas.width, canvas.height);

      return new Promise((resolve) => {
        canvas.toBlob((blob) => {
          resolve(blob);
        }, 'image/jpeg', 0.95);
      });
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to capture photo';
      console.error('Capture error:', err);
      setError(errorMessage);
      return null;
    }
  }, [stream]);

  const switchCamera = useCallback(async () => {
    stopCamera();
    const newMode = facingMode === 'user' ? 'environment' : 'user';
    await startCamera(newMode);
  }, [facingMode, startCamera, stopCamera]);

  return {
    isSupported,
    isActive,
    stream,
    error,
    startCamera,
    stopCamera,
    capturePhoto,
    switchCamera,
  };
}
