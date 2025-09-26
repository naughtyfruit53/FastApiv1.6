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
  const fallbackUrl = process.env.NEXT_PUBLIC_SNAPPYMAIL_URL || 'http://localhost:8888';
  if (config) {
    // Prefill login with user's email for easy access (user enters password in SnappyMail)
    return `${fallbackUrl}/?login=${encodeURIComponent(config.email)}`;
  }
  return fallbackUrl;
};