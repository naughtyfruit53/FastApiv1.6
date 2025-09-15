// pages/journal-entries.tsx
import React from 'react';
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  Button, 
  Grid,
  Alert
} from '@mui/material';
import { 
  NoteAdd
} from '@mui/icons-material';
import DashboardLayout from '../../components/DashboardLayout';

const JournalEntriesPage: React.FC = () => {
  return (
    <DashboardLayout
      title="Journal Entries"
      subtitle="Create and manage journal entries"
    >
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Alert severity="info" sx={{ mb: 3 }}>
            This journal entries module is under development. Core functionality will be available soon.
          </Alert>
        </Grid>
        
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ 
                display: 'flex', 
                flexDirection: 'column',
                alignItems: 'center', 
                justifyContent: 'center', 
                minHeight: 400,
                textAlign: 'center'
              }}>
                <NoteAdd sx={{ fontSize: 80, color: 'primary.main', mb: 2 }} />
                <Typography variant="h4" gutterBottom>
                  Journal Entries
                </Typography>
                <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
                  Create and manage journal entries
                </Typography>
                <Button variant="contained" disabled>
                  Feature Coming Soon
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </DashboardLayout>
  );
};

export default JournalEntriesPage;