import React, { useState, useEffect } from 'react';
import { 
  Box, Typography, Grid, Paper, Table, TableBody, 
  TableCell, TableContainer, TableHead, TableRow, Chip,
  Card, CardContent, CircularProgress, Alert, AlertTitle
} from '@mui/material';
import Markdown from 'react-markdown';
import { Link } from 'react-router-dom';

const ExecutiveDashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const response = await fetch('/api/executive/dashboard');
      const result = await response.json();
      setData(result.dashboard);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <CircularProgress />;
  if (!data) return <Typography>Error loading executive dashboard</Typography>;

  const { 
    market_snapshot, portfolio_snapshot, portfolio_health, 
    risk_overview, recommendations, daily_brief, alerts 
  } = data;

  return (
    <Box p={3} bgcolor="#f8fafc" minHeight="100vh">
      <Typography variant="h3" fontWeight="bold" mb={1} color="#0f172a">Executive Command Center</Typography>
      <Typography variant="subtitle1" color="textSecondary" mb={4}>Institutional AI Investment Intelligence Terminal</Typography>

      {/* Alerts */}
      {alerts.length > 0 && (
        <Box mb={4}>
          {alerts.map((alert, i) => (
            <Alert key={i} severity={alert.severity} sx={{ mb: 1 }}>
              {alert.message}
            </Alert>
          ))}
        </Box>
      )}

      <Grid container spacing={3} mb={4}>
        {/* Left Column: Brief & Health */}
        <Grid item xs={12} md={7}>
          <Card variant="outlined" sx={{ height: '100%', border: '1px solid #e2e8f0', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}>
            <CardContent>
              <Typography variant="h5" fontWeight="bold" gutterBottom borderBottom="2px solid #3b82f6" pb={1} display="inline-block">
                Daily Investment Brief
              </Typography>
              <Box mt={2} sx={{ '& h3': { mt: 2, mb: 1, fontSize: '1.2rem', fontWeight: 600, color: '#1e293b' }, '& p': { mb: 2, color: '#475569', lineHeight: 1.6 } }}>
                <Markdown>{daily_brief}</Markdown>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Right Column: Portfolio Health & Snapshot */}
        <Grid item xs={12} md={5}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Card sx={{ bgcolor: portfolio_health.score >= 80 ? '#f0fdf4' : '#fffbeb', border: `1px solid ${portfolio_health.score >= 80 ? '#bbf7d0' : '#fde68a'}` }}>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>Portfolio Health Score</Typography>
                  <Box display="flex" alignItems="center" justifyContent="space-between">
                    <Typography variant="h3" fontWeight="bold" color={portfolio_health.score >= 80 ? '#166534' : '#b45309'}>
                      {portfolio_health.health_score} <Typography variant="caption" fontSize="1rem">/100</Typography>
                    </Typography>
                    <Chip label={`Grade ${portfolio_health.grade}`} color={portfolio_health.score >= 80 ? 'success' : 'warning'} />
                  </Box>
                  <Typography variant="body2" color="textSecondary" mt={1}>{portfolio_health.status}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6}>
               <Card variant="outlined">
                <CardContent>
                  <Typography color="textSecondary" variant="body2">Total Value</Typography>
                  <Typography variant="h6" fontWeight="bold">${portfolio_snapshot.total_value?.toLocaleString(undefined, {minimumFractionDigits: 0})}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6}>
               <Card variant="outlined">
                <CardContent>
                  <Typography color="textSecondary" variant="body2">VaR (95%)</Typography>
                  <Typography variant="h6" fontWeight="bold">${risk_overview.value_at_risk_95?.toLocaleString(undefined, {minimumFractionDigits: 0})}</Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Grid>
      </Grid>

      {/* Market Snapshot Row */}
      <Typography variant="h5" fontWeight="bold" mb={2}>Market Snapshot</Typography>
      <Grid container spacing={2} mb={4}>
        {Object.entries(market_snapshot.indices).map(([name, data]) => (
          <Grid item xs={6} md={3} key={name}>
            <Card variant="outlined">
              <CardContent sx={{ pb: '16px !important' }}>
                <Typography color="textSecondary" variant="body2">{name}</Typography>
                <Box display="flex" alignItems="baseline" gap={1}>
                  <Typography variant="h6" fontWeight="bold">{data.value.toLocaleString()}</Typography>
                  <Typography variant="body2" fontWeight="bold" color={data.change >= 0 ? 'success.main' : 'error.main'}>
                    {data.change > 0 ? '+' : ''}{data.change}%
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* AI Recommendations */}
      <Typography variant="h5" fontWeight="bold" mb={2}>High Conviction AI Opportunities</Typography>
      <TableContainer component={Paper} variant="outlined">
        <Table>
          <TableHead sx={{ bgcolor: '#f1f5f9' }}>
            <TableRow>
              <TableCell fontWeight="bold">Symbol</TableCell>
              <TableCell fontWeight="bold">AI Rec</TableCell>
              <TableCell fontWeight="bold" align="right">Conviction</TableCell>
              <TableCell fontWeight="bold" align="right">Suggested Investment</TableCell>
              <TableCell fontWeight="bold" align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {recommendations.map((rec, i) => (
              <TableRow key={i}>
                <TableCell fontWeight="bold">{rec.symbol}</TableCell>
                <TableCell>
                  <Chip 
                    label={rec.recommendation} 
                    color={rec.recommendation === 'BUY' ? 'success' : 'default'} 
                    size="small" 
                  />
                </TableCell>
                <TableCell align="right" fontWeight="bold" color="primary">{(rec.confidence * 100).toFixed(1)}%</TableCell>
                <TableCell align="right">${rec.suggested_investment?.toLocaleString()}</TableCell>
                <TableCell align="right">
                  <Button 
                    component={Link} 
                    to={`/platform/research/${rec.symbol}`} 
                    size="small" 
                    variant="outlined"
                  >
                    Deep Dive
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

    </Box>
  );
};

export default ExecutiveDashboard;
