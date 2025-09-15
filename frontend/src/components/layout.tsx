// frontend/src/components/layout.tsx
import React, { useState } from "react";
import MegaMenu from "./MegaMenu";
import CompanySetupGuard from "./CompanySetupGuard";
import { Box } from "@mui/material";
import StickyNotesPanel from "./StickyNotes/StickyNotesPanel";
import { useMobileDetection } from "../hooks/useMobileDetection";
import { DeviceConditional } from "../utils/mobile/DeviceConditional";
import MobileNav from "./MobileNav";  // Changed from MobileNavigation to MobileNav
import { mainMenuSections } from "./menuConfig";
import { MobileNavContext } from "../context/MobileNavContext";

const Layout: React.FC<{
  children: React.ReactNode;
  user?: any;
  onLogout: () => void;
  showMegaMenu?: boolean;
}> = ({ children, user, onLogout, showMegaMenu = true }) => {
  const { isMobile } = useMobileDetection();
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  const handleMobileMenuToggle = () => {
    setMobileNavOpen(!mobileNavOpen);
  };

  return (
    <Box>
      <DeviceConditional
        mobile={
          <>
            <MobileNav
              open={mobileNavOpen}  // Changed to controlled props
              onClose={() => setMobileNavOpen(false)}
              user={user}
              onLogout={onLogout}
              menuItems={mainMenuSections}
            />
          </>
        }
        desktop={
          <MegaMenu user={user} onLogout={onLogout} isVisible={showMegaMenu} />
        }
      />
      
      <Box sx={{ mt: showMegaMenu && !isMobile ? 2 : 0 }}>
        <MobileNavContext.Provider value={{ onMenuToggle: handleMobileMenuToggle }}>
          <CompanySetupGuard>
            {children}
            {!isMobile && <StickyNotesPanel />}
          </CompanySetupGuard>
        </MobileNavContext.Provider>
      </Box>
    </Box>
  );
};

export default Layout;