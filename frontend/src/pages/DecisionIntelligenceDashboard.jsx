import React, { useState, useEffect } from 'react';
import { 
  Box, Typography, Grid, Paper, Table, TableBody, 
  TableCell, TableContainer, TableHead, TableRow, Chip,
  Card, CardContent, CircularProgress, Button, TextField
} from '@mui/material';

const DecisionIntelligenceDashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  
  // Scenario state
  const [scenarioSymbol, setScenarioSymbol] = useState('');
  const [scenarioAmount, setScenarioAmount] = useState('');
  const [scenarioAction, setScenarioAction] = useState('BUY');
  const [scenarioResult, setScenarioResult] = useState(null);
  const [simulating, setSimulating] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const response = await fetch('/api/intelligence/dashboard');
      const result = await response.json();
      setData(result.workspace);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSimulate = async () => {
    if (!scenarioSymbol || !scenarioAmount) return;
    setSimulating(true);
    try {
      const response = await fetch('/api/intelligence/scenario', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol: scenarioSymbol,
          amount: parseFloat(scenarioAmount),
          action: scenarioAction
        })
      });
      const result = await response.json();
      setScenarioResult(result.impact);
    } catch (e) {
      console.error(e);
    } finally {
      setSimulating(false);
    }
  };

  if (loading) return <CircularProgress />;
  if (!data) return <Typography>Error loading workspace</Typography>;

  const { portfolio, risk_analytics, recommendations, rebalancing_plan } = data;

  return (
    <Box p={3}>
      <Typography variant="h4" fontWeight="bold" mb={3}>Portfolio Decision Intelligence</Typography>
      
      {/* Overview Row */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} md={3}>
          <Card sx={{ bgcolor: '#eff6ff', border: '1px solid #bfdbfe' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Portfolio Total Value</Typography>
              <Typography variant="h5" color="#1e3a8a" fontWeight="bold">
                ${portfolio.total_value?.toLocaleString(undefined, {minimumFractionDigits: 2})}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ bgcolor: '#f0fdf4', border: '1px solid #bbf7d0' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Available Cash</Typography>
              <Typography variant="h5" color="#166534" fontWeight="bold">
                ${portfolio.cash_balance?.toLocaleString(undefined, {minimumFractionDigits: 2})}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card variant="outlined">
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Portfolio Volatility</Typography>
              <Typography variant="h5" fontWeight="bold">
                {(risk_analytics.portfolio_volatility * 100).toFixed(2)}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ bgcolor: '#fef2f2', border: '1px solid #fecaca' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Value at Risk (95%)</Typography>
              <Typography variant="h5" color="#991b1b" fontWeight="bold">
                ${risk_analytics.value_at_risk_95.toLocaleString(undefined, {minimumFractionDigits: 2})}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      {/* Actionable Recommendations */}
      <Typography variant="h5" fontWeight="bold" gutterBottom>Optimized Recommendations</Typography>
      <TableContainer component={Paper} sx={{ mb: 4 }}>
        <Table>
          <TableHead sx={{ bgcolor: '#f3f4f6' }}>
            <TableRow>
              <TableCell fontWeight="bold">Symbol</TableCell>
              <TableCell fontWeight="bold">AI Rec</TableCell>
              <TableCell fontWeight="bold" align="right">Confidence</TableCell>
              <TableCell fontWeight="bold" align="right">Suggested Investment</TableCell>
              <TableCell fontWeight="bold" align="right">Target Weight</TableCell>
              <TableCell fontWeight="bold" align="right">Risk Budget</TableCell>
              <TableCell fontWeight="bold" align="center">Top Factor</TableCell>
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
                <TableCell align="right">{(rec.confidence * 100).toFixed(1)}%</TableCell>
                <TableCell align="right" fontWeight="bold" color="primary">
                  ${rec.suggested_investment.toLocaleString()}
                </TableCell>
                <TableCell align="right">{(rec.target_weight * 100).toFixed(1)}%</TableCell>
                <TableCell align="right">{(rec.risk_budget_consumption * 100).toFixed(1)}%</TableCell>
                <TableCell align="center">
                  <Chip label={Object.keys(rec.shap_explanation || {})[0] || 'N/A'} size="small" variant="outlined" />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Scenario Sandbox */}
      <Typography variant="h5" fontWeight="bold" gutterBottom>Scenario Analyzer</Typography>
      <Card variant="outlined" sx={{ mb: 4, p: 2 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={2}>
            <TextField 
              fullWidth 
              size="small" 
              label="Symbol" 
              value={scenarioSymbol} 
              onChange={e => setScenarioSymbol(e.target.value)} 
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <TextField 
              fullWidth 
              size="small" 
              label="Action (BUY/SELL)" 
              value={scenarioAction} 
              onChange={e => setScenarioAction(e.target.value.toUpperCase())} 
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField 
              fullWidth 
              size="small" 
              type="number" 
              label="Amount ($)" 
              value={scenarioAmount} 
              onChange={e => setScenarioAmount(e.target.value)} 
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <Button 
              variant="contained" 
              color="primary" 
              fullWidth 
              onClick={handleSimulate}
              disabled={simulating}
            >
              {simulating ? 'Simulating...' : 'Run Scenario'}
            </Button>
          </Grid>
        </Grid>
        
        {scenarioResult && !scenarioResult.error && (
          <Box mt={3} p={2} bgcolor="#f8fafc" borderRadius={1}>
            <Typography variant="subtitle1" fontWeight="bold" gutterBottom>Simulation Impact</Typography>
            <Grid container spacing={4}>
              <Grid item xs={4}>
                <Typography color="textSecondary" variant="body2">Vol Delta</Typography>
                <Typography color={scenarioResult.deltas.volatility > 0 ? "error" : "success.main"}>
                  {scenarioResult.deltas.volatility > 0 ? '+' : ''}{(scenarioResult.deltas.volatility * 100).toFixed(3)}%
                </Typography>
              </Grid>
              <Grid item xs={4}>
                <Typography color="textSecondary" variant="body2">VaR Delta</Typography>
                <Typography color={scenarioResult.deltas.var_95 > 0 ? "error" : "success.main"}>
                  {scenarioResult.deltas.var_95 > 0 ? '+' : ''}${scenarioResult.deltas.var_95.toFixed(2)}
                </Typography>
              </Grid>
              <Grid item xs={4}>
                <Typography color="textSecondary" variant="body2">Div Score Delta</Typography>
                <Typography color={scenarioResult.deltas.diversification > 0 ? "success.main" : "error"}>
                  {scenarioResult.deltas.diversification > 0 ? '+' : ''}{scenarioResult.deltas.diversification.toFixed(2)}
                </Typography>
              </Grid>
            </Grid>
          </Box>
        )}
        {scenarioResult?.error && (
           <Box mt={2}><Typography color="error">{scenarioResult.error}</Typography></Box>
        )}
      </Card>
      
      {/* Rebalancing Advisor */}
      <Typography variant="h5" fontWeight="bold" gutterBottom>Rebalancing Advisor</Typography>
      {rebalancing_plan.status === 'OK' ? (
        <Alert severity="success">Portfolio is within optimal weight boundaries.</Alert>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead sx={{ bgcolor: '#f3f4f6' }}>
              <TableRow>
                <TableCell>Type</TableCell>
                <TableCell>Target</TableCell>
                <TableCell>Reason</TableCell>
                <TableCell align="right">Suggested Action</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rebalancing_plan.actions.map((act, i) => (
                <TableRow key={i}>
                  <TableCell><Chip label={act.type} size="small" color="warning" /></TableCell>
                  <TableCell fontWeight="bold">{act.symbol || act.sector}</TableCell>
                  <TableCell>{act.reason}</TableCell>
                  <TableCell align="right" color="error" fontWeight="bold">
                    {act.suggested_amount ? `-$${act.suggested_amount.toLocaleString(undefined, {maximumFractionDigits: 0})}` : 
                     act.suggested_reduction_pct ? `-${(act.suggested_reduction_pct*100).toFixed(1)}%` : ''}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

    </Box>
  );
};

export default DecisionIntelligenceDashboard;
