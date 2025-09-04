// Example usage of the mobile detection hook
import React from 'react';
import { Typography, Box, Paper } from '@mui/material';
import { useMobileDetection, useResponsiveValue } from '../hooks/useMobileDetection';

const MobileDetectionDemo: React.FC = () => {
  const detection = useMobileDetection();
  
  // Example of responsive values
  const gridColumns = useResponsiveValue(1, 2, 3);
  const fontSize = useResponsiveValue('14px', '16px', '18px');
  
  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h4" gutterBottom>
        Mobile Detection Demo
      </Typography>
      
      <Paper sx={{ p: 3, mb: 2 }}>
        <Typography variant="h6" gutterBottom>
          Device Information
        </Typography>
        <Typography>Device Type: {detection.isMobile ? 'Mobile' : detection.isTablet ? 'Tablet' : 'Desktop'}</Typography>
        <Typography>Screen Size: {detection.screenWidth} x {detection.screenHeight}</Typography>
        <Typography>Orientation: {detection.orientation}</Typography>
        <Typography>Touch Device: {detection.touchDevice ? 'Yes' : 'No'}</Typography>
        <Typography>Pixel Ratio: {detection.pixelRatio}</Typography>
      </Paper>
      
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Responsive Values Demo
        </Typography>
        <Typography sx={{ fontSize }}>
          This text size adapts to screen size
        </Typography>
        <Box 
          sx={{ 
            display: 'grid', 
            gridTemplateColumns: `repeat(${gridColumns}, 1fr)`,
            gap: 2,
            mt: 2
          }}
        >
          {Array.from({ length: gridColumns }, (_, i) => (
            <Box key={i} sx={{ p: 2, bgcolor: 'primary.light', color: 'white', textAlign: 'center' }}>
              Column {i + 1}
            </Box>
          ))}
        </Box>
      </Paper>
    </Box>
  );
};

export default MobileDetectionDemo;