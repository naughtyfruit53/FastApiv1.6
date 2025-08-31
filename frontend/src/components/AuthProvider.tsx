// frontend/src/components/AuthProvider.tsx
import React, { createContext, useState, ReactNode } from 'react';
import { useRouter } from 'next/router';
import { jwtDecode } from 'jwt-decode';
import axios from 'axios';

interface User {
  id: number;
  email: string;
}

interface JwtPayload {
  exp: number;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const api = axios.create({
    baseURL: '/api/v1',
  });

  api.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  api.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;
      if (error.response.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;
        await refreshToken();
        return api(originalRequest);
      }
      return Promise.reject(error);
    }
  );

  const refreshToken = async () => {
    const token = localStorage.getItem('token');
    if (!token) {return logout();}
    try {
      const response = await api.post('/auth/refresh-token');
      localStorage.setItem('token', response.data.access_token);
      await fetchUser();
    } catch (refreshError) {
      console.error('Token refresh failed', refreshError);
      logout();
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    router.push('/login');
  };

  const fetchUser = async () => {
    try {
      const response = await api.get('/users/me');
      setUser(response.data);
    } catch (fetchError) {
      console.error('Fetch user error', fetchError);
      throw fetchError;
    }
  };

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const decoded: JwtPayload = jwtDecode(token);
          if (decoded.exp * 1000 < Date.now()) {
            console.log('Token expired on load, logging out');
            logout();
            return;
          }
          await fetchUser();
        } catch (authError) {
          console.error('Auth check failed', authError);
          logout();
        }
      } else {
        logout();
      }
      setLoading(false);
    };
    checkAuth();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const response = await api.post('/auth/login/email', { email, password });
      localStorage.setItem('token', response.data.access_token);
      setUser(response.data.user);
      router.push('/dashboard');
    } catch (loginError) {
      console.error('Login error', loginError);
      throw loginError;
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, refreshToken }}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = React.useContext(AuthContext);
  if (undefined === context) {throw new Error('useAuth must be used within AuthProvider');}
  return context;
};