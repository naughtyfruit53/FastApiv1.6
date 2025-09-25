// frontend/src/services/emailService.ts
import { api } from '../lib/api';

export interface SnappyMailConfig {
  imap_host: string;
  imap_port: number;
  smtp_host: string;
  smtp_port: number;
  use_ssl: boolean;
  email: string;
}

export const getSnappyMailConfig = async (userId: number): Promise<SnappyMailConfig | null> => {
  try {
    const response = await api.get(`/mail/config/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Failed to fetch SnappyMail config:', error);
    return null;
  }
};

export const getSnappyMailUrl = async (userId: number): Promise<string> => {
  const config = await getSnappyMailConfig(userId);
  if (config) {
    const protocol = config.use_ssl ? 'https' : 'http';
    return `${protocol}://${config.imap_host}:${config.imap_port}`;
  }
  // Fallback to env or default
  return (typeof window !== 'undefined' ? process.env.NEXT_PUBLIC_SNAPPYMAIL_URL : '') || 'http://localhost:8888';
};