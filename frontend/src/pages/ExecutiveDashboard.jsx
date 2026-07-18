import React, { useState, useEffect } from 'react';
import { 
  Box, Typography, Grid, Paper, Table, TableBody, 
  TableCell, TableContainer, TableHead, TableRow, Chip,
  Card, CardContent, CircularProgress, Alert, AlertTitle, Button
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
      const response = await fetch('http://localhost:8000/api/executive/dashboard');
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
    <Box p={3} sx={{ color: 'var(--text-primary)' }}>
      <Typography variant="h3" fontWeight="bold" mb={1}>Executive Command Center</Typography>
      <Typography variant="subtitle1" color="var(--text-secondary)" mb={4}>Institutional AI Investment Intelligence Terminal</Typography>

      {/* Alerts */}
      {alerts.length > 0 && (
        <Box mb={4}>
          {alerts.map((alert, i) => (
            <Alert key={i} severity={alert.severity} sx={{ mb: 1, bgcolor: 'var(--bg-surface-elevated)', color: 'var(--text-primary)', border: '1px solid var(--glass-border)' }}>
              {alert.message}
            </Alert>
          ))}
        </Box>
      )}

      <Grid container spacing={3} mb={4}>
        {/* Left Column: Brief & Health */}
        <Grid item xs={12} md={7}>
          <Card className="glass-card" sx={{ height: '100%', bgcolor: 'var(--bg-surface)' }}>
            <CardContent>
              <Typography variant="h5" fontWeight="bold" gutterBottom borderBottom="2px solid var(--accent-primary)" pb={1} display="inline-block" color="var(--text-primary)">
                Daily Investment Brief
              </Typography>
              <Box mt={2} sx={{ '& h3': { mt: 2, mb: 1, fontSize: '1.2rem', fontWeight: 600, color: 'var(--text-primary)' }, '& p': { mb: 2, color: 'var(--text-secondary)', lineHeight: 1.6 }, '& strong': { color: 'var(--accent-primary)' } }}>
                <Markdown>{daily_brief}</Markdown>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Right Column: Portfolio Health & Snapshot */}
        <Grid item xs={12} md={5}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Card className="glass-card" sx={{ bgcolor: portfolio_health.score >= 80 ? 'rgba(34, 197, 94, 0.1)' : 'rgba(245, 158, 11, 0.1)', border: `1px solid ${portfolio_health.score >= 80 ? 'rgba(34, 197, 94, 0.3)' : 'rgba(245, 158, 11, 0.3)'}` }}>
                <CardContent>
                  <Typography color="var(--text-secondary)" gutterBottom>Portfolio Health Score</Typography>
                  <Box display="flex" alignItems="center" justifyContent="space-between">
                    <Typography variant="h3" fontWeight="bold" color={portfolio_health.score >= 80 ? '#4ade80' : '#fbbf24'}>
                      {portfolio_health.health_score} <Typography variant="caption" fontSize="1rem">/100</Typography>
                    </Typography>
                    <Chip label={`Grade ${portfolio_health.grade}`} color={portfolio_health.score >= 80 ? 'success' : 'warning'} variant="outlined" />
                  </Box>
                  <Typography variant="body2" color="var(--text-secondary)" mt={1}>{portfolio_health.status}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6}>
               <Card className="glass-card" sx={{ bgcolor: 'var(--bg-surface)' }}>
                <CardContent>
                  <Typography color="var(--text-secondary)" variant="body2">Total Value</Typography>
                  <Typography variant="h6" fontWeight="bold" color="var(--text-primary)">${portfolio_snapshot.total_value?.toLocaleString('en-US', {minimumFractionDigits: 0})}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6}>
               <Card className="glass-card" sx={{ bgcolor: 'var(--bg-surface)' }}>
                <CardContent>
                  <Typography color="var(--text-secondary)" variant="body2">VaR (95%)</Typography>
                  <Typography variant="h6" fontWeight="bold" color="var(--text-primary)">${risk_overview.value_at_risk_95?.toLocaleString('en-US', {minimumFractionDigits: 0})}</Typography>
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
            <Card className="glass-card" sx={{ bgcolor: 'var(--bg-surface)' }}>
              <CardContent sx={{ pb: '16px !important' }}>
                <Typography color="var(--text-secondary)" variant="body2">{name}</Typography>
                <Box display="flex" alignItems="baseline" gap={1}>
                  <Typography variant="h6" fontWeight="bold" color="var(--text-primary)">{data.value.toLocaleString('en-US')}</Typography>
                  <Typography variant="body2" fontWeight="bold" color={data.change >= 0 ? '#4ade80' : '#f87171'}>
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
      <TableContainer component={Paper} className="glass-card" sx={{ bgcolor: 'var(--bg-surface)', border: '1px solid var(--glass-border)' }}>
        <Table>
          <TableHead sx={{ bgcolor: 'var(--bg-surface-elevated)' }}>
            <TableRow>
              <TableCell sx={{ color: 'var(--text-secondary)', fontWeight: 'bold', borderBottom: '1px solid var(--glass-border)' }}>Symbol</TableCell>
              <TableCell sx={{ color: 'var(--text-secondary)', fontWeight: 'bold', borderBottom: '1px solid var(--glass-border)' }}>AI Rec</TableCell>
              <TableCell align="right" sx={{ color: 'var(--text-secondary)', fontWeight: 'bold', borderBottom: '1px solid var(--glass-border)' }}>Conviction</TableCell>
              <TableCell align="right" sx={{ color: 'var(--text-secondary)', fontWeight: 'bold', borderBottom: '1px solid var(--glass-border)' }}>Suggested Investment</TableCell>
              <TableCell align="right" sx={{ color: 'var(--text-secondary)', fontWeight: 'bold', borderBottom: '1px solid var(--glass-border)' }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {recommendations.map((rec, i) => (
              <TableRow key={i}>
                <TableCell sx={{ color: 'var(--text-primary)', fontWeight: 'bold', borderBottom: '1px solid var(--glass-border)' }}>{rec.symbol}</TableCell>
                <TableCell sx={{ borderBottom: '1px solid var(--glass-border)' }}>
                  <Chip 
                    label={rec.recommendation} 
                    sx={{ bgcolor: rec.recommendation === 'BUY' ? 'rgba(34, 197, 94, 0.2)' : 'rgba(148, 163, 184, 0.2)', color: rec.recommendation === 'BUY' ? '#4ade80' : '#94a3b8' }} 
                    size="small" 
                  />
                </TableCell>
                <TableCell align="right" sx={{ fontWeight: 'bold', color: 'var(--accent-primary)', borderBottom: '1px solid var(--glass-border)' }}>{(rec.confidence * 100).toFixed(1)}%</TableCell>
                <TableCell align="right" sx={{ color: 'var(--text-primary)', borderBottom: '1px solid var(--glass-border)' }}>${rec.suggested_investment?.toLocaleString('en-US')}</TableCell>
                <TableCell align="right" sx={{ borderBottom: '1px solid var(--glass-border)' }}>
                  <Button 
                    component={Link} 
                    to={`/platform/research/${rec.symbol}`} 
                    size="small" 
                    variant="outlined"
                    sx={{ color: 'var(--accent-primary)', borderColor: 'var(--accent-primary)' }}
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
