/**
 * Email Context for managing selected account
 */

import React, { createContext, useState, useContext, ReactNode, useEffect } from 'react';

interface EmailContextType {
  selectedToken: number | null;
  setSelectedToken: (token: number | null) => void;
}

const EmailContext = createContext<EmailContextType | undefined>(undefined);

export const EmailProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [selectedToken, setSelectedToken] = useState<number | null>(() => {
    const stored = localStorage.getItem('selectedEmailToken');
    return stored ? parseInt(stored, 10) : null;
  });

  useEffect(() => {
    if (selectedToken) {
      localStorage.setItem('selectedEmailToken', selectedToken.toString());
    } else {
      localStorage.removeItem('selectedEmailToken');
    }
  }, [selectedToken]);

  return (
    <EmailContext.Provider value={{ selectedToken, setSelectedToken }}>
      {children}
    </EmailContext.Provider>
  );
};

export const useEmail = () => {
  const context = useContext(EmailContext);
  if (undefined === context) {
    throw new Error('useEmail must be used within EmailProvider');
  }
  return context;
};