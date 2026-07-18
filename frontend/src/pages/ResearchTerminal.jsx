import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  Box, Typography, Grid, Paper, Card, CardContent, CircularProgress, Chip, Button 
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';

const ResearchTerminal = () => {
  const { symbol } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`/api/executive/research/${symbol}`);
        const result = await response.json();
        setData(result.research);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [symbol]);

  if (loading) return <CircularProgress />;
  if (!data || data.error) return <Typography color="error">{data?.error || 'Failed to load research'}</Typography>;

  return (
    <Box p={3} bgcolor="#f8fafc" minHeight="100vh">
      <Button component={Link} to="/" startIcon={<ArrowBackIcon />} sx={{ mb: 3 }}>
        Back to Dashboard
      </Button>
      
      <Typography variant="h3" fontWeight="bold" mb={4}>{data.symbol} Research Terminal</Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card variant="outlined" sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom borderBottom="1px solid #e2e8f0" pb={1}>AI Prediction (Champion Model)</Typography>
              <Box display="flex" alignItems="center" gap={2} mt={2} mb={3}>
                <Chip 
                  label={data.ai_prediction.recommendation} 
                  color={data.ai_prediction.recommendation === 'BUY' ? 'success' : 'default'} 
                  sx={{ fontSize: '1.2rem', p: 2, fontWeight: 'bold' }}
                />
                <Typography variant="h4" color="primary" fontWeight="bold">
                  {(data.ai_prediction.confidence * 100).toFixed(1)}% Conf
                </Typography>
              </Box>
              <Typography variant="body2" color="textSecondary">
                Historical Accuracy for {data.symbol}: {(data.historical_accuracy * 100).toFixed(1)}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card variant="outlined" sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom borderBottom="1px solid #e2e8f0" pb={1}>SHAP Explainability</Typography>
              <Typography variant="subtitle2" color="success.main" mt={2} mb={1}>Top Positive Drivers</Typography>
              {data.explainability.top_positive_factors.map(([feat, imp]) => (
                <Box key={feat} display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2">{feat}</Typography>
                  <Typography variant="body2" fontWeight="bold">{(imp*100).toFixed(2)}</Typography>
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card variant="outlined" sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom borderBottom="1px solid #e2e8f0" pb={1}>Technical Summary</Typography>
              <Box mt={2}>
                <Grid container spacing={2}>
                  {Object.entries(data.technical_summary).map(([key, val]) => (
                     <Grid item xs={6} key={key}>
                       <Typography variant="body2" color="textSecondary">{key}</Typography>
                       <Typography variant="body1" fontWeight="bold">{val}</Typography>
                     </Grid>
                  ))}
                </Grid>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ResearchTerminal;
