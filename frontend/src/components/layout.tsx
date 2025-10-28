'use client'; // <-- Mark as client component (uses useState)

import React, { useState } from "react";
import MegaMenu from "./MegaMenu";
import CompanySetupGuard from "./CompanySetupGuard";
import { Box } from "@mui/material";

import { useMobileDetection } from "../hooks/useMobileDetection";
import { DeviceConditional } from "../utils/mobile/DeviceConditional";
import MobileNav from "./MobileNav";

import { mainMenuSections } from "./menuConfig";
import { MobileNavContext } from "../context/MobileNavContext";

const Layout: React.FC<{
  children: React.ReactNode;
  user?: any;
  onLogout: () => void;
  showMegaMenu?: boolean;
}> = ({ children, user, onLogout, showMegaMenu = true }) => {
  const { isMobile } = useMobileDetection();
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);

  return (
    <>
      <DeviceConditional
        mobile={
          <MobileNav
            open={mobileDrawerOpen}
            onClose={() => setMobileDrawerOpen(false)}
            user={user}
            onLogout={onLogout}
            // Fixed: pass the real menu data (was using undefined `menuItems`)
            menuItems={mainMenuSections}
          />
        }
        desktop={
          <MegaMenu user={user} onLogout={onLogout} isVisible={showMegaMenu} />
        }
      />

      <Box sx={{ mt: showMegaMenu && !isMobile ? 2 : 0 }}>
        <MobileNavContext.Provider
          value={{ onMenuToggle: () => setMobileDrawerOpen(true) }}
        >
          <CompanySetupGuard>{children}</CompanySetupGuard>
        </MobileNavContext.Provider>
      </Box>
    </>
  );
};

export default Layout;