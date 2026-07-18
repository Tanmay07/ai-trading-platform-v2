import React, { useState, useEffect } from 'react';
import { 
  Box, Typography, Grid, Paper, Table, TableBody, 
  TableCell, TableContainer, TableHead, TableRow, Chip,
  Card, CardContent, CircularProgress, Button, IconButton, Tooltip
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';

const PaperTradingValidation = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [portfolio, setPortfolio] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [recRes, portRes] = await Promise.all([
        fetch('/api/paper_trading/recommendations'),
        fetch('/api/paper_trading/portfolio')
      ]);
      const recData = await recRes.json();
      const portData = await portRes.json();
      
      setRecommendations(recData.recommendations || []);
      setPortfolio(portData.portfolio || {});
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleDecision = async (recId, decision) => {
    try {
      await fetch('/api/paper_trading/journal/decision', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ recommendation_id: recId, decision })
      });
      fetchData(); // Refresh
    } catch (e) {
      console.error(e);
    }
  };

  if (loading) return <CircularProgress />;

  return (
    <Box p={3}>
      <Typography variant="h4" fontWeight="bold" mb={3}>Paper Trading & Model Validation</Typography>
      
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} md={4}>
          <Card sx={{ bgcolor: '#eff6ff', border: '1px solid #bfdbfe' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Virtual Portfolio Value</Typography>
              <Typography variant="h4" color="#1e3a8a" fontWeight="bold">
                ${portfolio.total_value?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card sx={{ bgcolor: '#f0fdf4', border: '1px solid #bbf7d0' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Available Cash</Typography>
              <Typography variant="h4" color="#166534" fontWeight="bold">
                ${portfolio.cash_balance?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card sx={{ bgcolor: portfolio.unrealized_pnl >= 0 ? '#f0fdf4' : '#fef2f2', border: '1px solid #e5e7eb' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Unrealized P&L</Typography>
              <Typography variant="h4" color={portfolio.unrealized_pnl >= 0 ? '#166534' : '#991b1b'} fontWeight="bold">
                ${portfolio.unrealized_pnl?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Typography variant="h5" fontWeight="bold" gutterBottom>Daily Champion Recommendations</Typography>
      <Typography variant="body2" color="textSecondary" mb={2}>
        Approve or Ignore the AI's recommendations to record your decision in the Investment Journal.
      </Typography>
      
      <TableContainer component={Paper} sx={{ mb: 4 }}>
        <Table>
          <TableHead sx={{ bgcolor: '#f3f4f6' }}>
            <TableRow>
              <TableCell>Date</TableCell>
              <TableCell>Symbol</TableCell>
              <TableCell>Recommendation</TableCell>
              <TableCell align="right">Confidence</TableCell>
              <TableCell>Top SHAP Factors</TableCell>
              <TableCell align="center">Human Decision</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {recommendations.map((rec, i) => (
              <TableRow key={i}>
                <TableCell>{rec.date}</TableCell>
                <TableCell fontWeight="bold">{rec.symbol}</TableCell>
                <TableCell>
                  <Chip 
                    label={rec.recommendation} 
                    color={rec.recommendation === 'BUY' ? 'success' : 'default'} 
                    size="small" 
                  />
                </TableCell>
                <TableCell align="right">{(rec.confidence * 100).toFixed(2)}%</TableCell>
                <TableCell>
                  {Object.keys(rec.shap_explanation || {}).join(", ")}
                </TableCell>
                <TableCell align="center">
                  <Tooltip title="Approve Trade (Record in Portfolio)">
                    <IconButton color="success" onClick={() => handleDecision(rec.id, 'APPROVED')}>
                      <CheckCircleIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Ignore Recommendation">
                    <IconButton color="error" onClick={() => handleDecision(rec.id, 'IGNORED')}>
                      <CancelIcon />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
            {recommendations.length === 0 && (
              <TableRow>
                <TableCell colSpan={6} align="center">No recommendations generated for today.</TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
      
      <Typography variant="h5" fontWeight="bold" gutterBottom>Open Positions Monitor</Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead sx={{ bgcolor: '#f3f4f6' }}>
            <TableRow>
              <TableCell>Symbol</TableCell>
              <TableCell>Entry Date</TableCell>
              <TableCell align="right">Entry Price</TableCell>
              <TableCell align="right">Quantity</TableCell>
              <TableCell align="right">AI Confidence</TableCell>
              <TableCell align="center">Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {(portfolio.open_positions || []).map((pos) => (
              <TableRow key={pos.id}>
                <TableCell fontWeight="bold">{pos.symbol}</TableCell>
                <TableCell>{pos.entry_date}</TableCell>
                <TableCell align="right">${pos.entry_price.toFixed(2)}</TableCell>
                <TableCell align="right">{pos.quantity}</TableCell>
                <TableCell align="right">{(pos.ai_confidence * 100).toFixed(2)}%</TableCell>
                <TableCell align="center">
                  <Chip label="OPEN" color="primary" size="small" />
                </TableCell>
              </TableRow>
            ))}
            {(!portfolio.open_positions || portfolio.open_positions.length === 0) && (
              <TableRow>
                <TableCell colSpan={6} align="center">No open positions in virtual portfolio.</TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

    </Box>
  );
};

export default PaperTradingValidation;
