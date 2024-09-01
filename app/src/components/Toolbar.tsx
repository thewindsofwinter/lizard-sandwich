import React from 'react';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import { AppBar, IconButton, Toolbar, Typography } from '@mui/material';

const CustomToolbar: React.FC = () => {
  return (
    <AppBar position="static"
        sx={{
            padding: '0 20px',
        }}
    >
        <Toolbar>
            <IconButton edge="start" color="inherit" aria-label="menu" sx={{ mr: 2 }}>
            <SmartToyIcon />
            </IconButton>
            <Typography variant="h6" color="inherit" component="div">
            Your Three-Eyed Bot
            </Typography>
        </Toolbar>
    </AppBar>
  );
}

export default CustomToolbar;
