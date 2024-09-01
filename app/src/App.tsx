import React from 'react';
import { Grid } from '@mui/material';
import CustomToolbar from './components/Toolbar';
import LeftPanel from './components/LeftPanel';
import RightPanel from './components/RightPanel';

const App: React.FC = () => {
  return (
    <div>
      <CustomToolbar />
      <Grid container>
        <Grid item xs={6}>
          <LeftPanel />
        </Grid>
        <Grid item xs={6}>
          <RightPanel />
        </Grid>
      </Grid>
    </div>
  );
}

export default App;
