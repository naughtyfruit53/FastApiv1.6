/**
 * Email Context for managing selected account
 */

import React, { createContext, useState, useContext, ReactNode, useEffect } from 'react';

interface EmailContextType {
  selectedAccountId: number | null;
  setSelectedAccountId: (account: number | null) => void;
}

const EmailContext = createContext<EmailContextType | undefined>(undefined);

export const EmailProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [selectedAccountId, setSelectedAccountId] = useState<number | null>(() => {
    const stored = localStorage.getItem('selectedEmailAccount');
    return stored ? parseInt(stored, 10) : null;
  });

  useEffect(() => {
    if (selectedAccountId) {
      localStorage.setItem('selectedEmailAccount', selectedAccountId.toString());
    } else {
      localStorage.removeItem('selectedEmailAccount');
    }
  }, [selectedAccountId]);

  return (
    <EmailContext.Provider value={{ selectedAccountId, setSelectedAccountId }}>
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