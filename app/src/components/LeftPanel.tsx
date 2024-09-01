import React from 'react';
import { Box, Typography } from '@mui/material';

const LeftPanel: React.FC = () => {
  return (
    <Box 
      display="flex" 
      justifyContent="center" 
      alignItems="center" 
      height="70vh"
      padding="16px"
    >
        <Box 
        display="flex" 
        justifyContent="center" 
        alignItems="center" 
        height="100%"
        width="100%"
        bgcolor="#f0f0f0"
        >
        <img 
            src="http://localhost:5050/video_feed" 
            alt="Camera Stream" 
            style={{ maxWidth: '100%', maxHeight: '100%', borderRadius: '8px' }}
        />
        </Box>
    </Box>
  );
}

export default LeftPanel;
