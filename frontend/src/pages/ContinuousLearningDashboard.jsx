import React, { useState, useEffect } from 'react';
import { 
  Box, Typography, Grid, Paper, Table, TableBody, 
  TableCell, TableContainer, TableHead, TableRow, Chip,
  Card, CardContent, CircularProgress, Alert, AlertTitle
} from '@mui/material';

const ContinuousLearningDashboard = () => {
  const [journal, setJournal] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [drift, setDrift] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [journRes, analRes, driftRes] = await Promise.all([
        fetch('/api/paper_trading/journal'),
        fetch('/api/paper_trading/analytics/ai_vs_human'),
        fetch('/api/paper_trading/analytics/drift')
      ]);
      const journData = await journRes.json();
      const analData = await analRes.json();
      const driftData = await driftRes.json();
      
      setJournal(journData.journal || []);
      setAnalytics(analData);
      setDrift(driftData.drift);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <CircularProgress />;

  return (
    <Box p={3}>
      <Typography variant="h4" fontWeight="bold" mb={3}>Continuous Learning & Model Drift</Typography>
      
      {drift?.retraining_recommended && (
        <Alert severity="error" sx={{ mb: 4 }}>
          <AlertTitle>Retraining Recommended</AlertTitle>
          Model drift detected beyond acceptable thresholds. The Champion Model should be retrained.
        </Alert>
      )}
      
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} md={4}>
          <Card sx={{ border: '1px solid #e5e7eb' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Feature Drift Score</Typography>
              <Typography variant="h4" color={drift?.feature_drift_score > 0.1 ? 'error' : 'primary'} fontWeight="bold">
                {drift?.feature_drift_score?.toFixed(4) || "N/A"}
              </Typography>
              <Typography variant="body2" color="textSecondary">Threshold: 0.1000</Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card sx={{ border: '1px solid #e5e7eb' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Prediction Drift Score</Typography>
              <Typography variant="h4" color={drift?.prediction_drift_score > 0.05 ? 'error' : 'primary'} fontWeight="bold">
                {drift?.prediction_drift_score?.toFixed(4) || "N/A"}
              </Typography>
              <Typography variant="body2" color="textSecondary">Threshold: 0.0500</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ border: '1px solid #e5e7eb', bgcolor: '#f0fdf4' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>AI Win Rate (Simulated)</Typography>
              <Typography variant="h4" color="#166534" fontWeight="bold">
                {(analytics?.ai_accuracy * 100)?.toFixed(1)}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      <Typography variant="h5" fontWeight="bold" gutterBottom>AI vs Human Analytics</Typography>
      <Grid container spacing={3} mb={4}>
        <Grid item xs={6} md={3}>
          <Card variant="outlined">
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Total Recommendations</Typography>
              <Typography variant="h5" fontWeight="bold">{analytics?.total_recommendations}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={6} md={3}>
          <Card variant="outlined" sx={{ bgcolor: '#f0fdf4' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Human Approved</Typography>
              <Typography variant="h5" color="#166534" fontWeight="bold">{analytics?.approved}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={6} md={3}>
          <Card variant="outlined" sx={{ bgcolor: '#fef2f2' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Human Ignored</Typography>
              <Typography variant="h5" color="#991b1b" fontWeight="bold">{analytics?.ignored}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={6} md={3}>
          <Card variant="outlined" sx={{ bgcolor: '#fffbeb' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Human Overridden</Typography>
              <Typography variant="h5" color="#b45309" fontWeight="bold">{analytics?.overridden}</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Typography variant="h5" fontWeight="bold" gutterBottom>Investment Journal</Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead sx={{ bgcolor: '#f3f4f6' }}>
            <TableRow>
              <TableCell>Date</TableCell>
              <TableCell>Symbol</TableCell>
              <TableCell>Recommendation</TableCell>
              <TableCell>Human Decision</TableCell>
              <TableCell align="right">Outcome Return</TableCell>
              <TableCell>Lessons Learned</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {journal.map((entry) => (
              <TableRow key={entry.id}>
                <TableCell>{entry.date}</TableCell>
                <TableCell fontWeight="bold">{entry.symbol}</TableCell>
                <TableCell>{entry.recommendation}</TableCell>
                <TableCell>
                  <Chip 
                    label={entry.human_decision || "PENDING"} 
                    color={
                      entry.human_decision === 'APPROVED' ? 'success' : 
                      entry.human_decision === 'IGNORED' ? 'error' : 
                      entry.human_decision === 'OVERRIDDEN' ? 'warning' : 'default'
                    } 
                    size="small" 
                  />
                </TableCell>
                <TableCell align="right">
                  {entry.outcome_return !== null ? `${(entry.outcome_return * 100).toFixed(2)}%` : '-'}
                </TableCell>
                <TableCell>{entry.lessons_learned || '-'}</TableCell>
              </TableRow>
            ))}
            {journal.length === 0 && (
              <TableRow>
                <TableCell colSpan={6} align="center">No journal entries found.</TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

    </Box>
  );
};

export default ContinuousLearningDashboard;
