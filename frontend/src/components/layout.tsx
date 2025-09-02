// frontend/src/components/layout.tsx
import React from "react";
import MegaMenu from "./MegaMenu";
import CompanySetupGuard from "./CompanySetupGuard";
import { Box } from "@mui/material";
import StickyNotesPanel from "./StickyNotes/StickyNotesPanel";

const Layout: React.FC<{
  children: React.ReactNode;
  user?: any;
  onLogout: () => void;
  showMegaMenu?: boolean;
}> = ({ children, user, onLogout, showMegaMenu = true }) => {
  return (
    <Box>
      <MegaMenu user={user} onLogout={onLogout} isVisible={showMegaMenu} />
      <Box sx={{ mt: showMegaMenu ? 2 : 0 }}>
        <CompanySetupGuard>
          {children}
          <StickyNotesPanel />
        </CompanySetupGuard>
      </Box>
    </Box>
  );
};

export default Layout;
