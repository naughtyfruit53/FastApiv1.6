import { createContext, useContext, useState, ReactNode } from 'react';

interface MobileNavContextType {
  onMenuToggle: () => void;
  isMenuOpen: boolean;
}

export const MobileNavContext = createContext<MobileNavContextType | undefined>(undefined);

export const MobileNavProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const onMenuToggle = () => setIsMenuOpen(!isMenuOpen);
  return (
    <MobileNavContext.Provider value={{ onMenuToggle, isMenuOpen }}>
      {children}
    </MobileNavContext.Provider>
  );
};

export const useMobileNav = () => {
  const context = useContext(MobileNavContext);
  if (!context) {
    throw new Error('useMobileNav must be used within MobileNavProvider');
  }
  return context;
};
