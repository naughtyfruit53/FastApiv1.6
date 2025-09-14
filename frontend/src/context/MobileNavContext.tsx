import { createContext, useContext } from 'react';

interface MobileNavContextType {
  onMenuToggle: () => void;
}

export const MobileNavContext = createContext<MobileNavContextType | undefined>(undefined);

export const useMobileNav = () => {
  const context = useContext(MobileNavContext);
  if (!context) {
    throw new Error('useMobileNav must be used within MobileNavProvider');
  }
  return context;
};