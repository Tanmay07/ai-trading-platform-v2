import React, { useState, useEffect } from 'react';
import { 
  Box, Typography, Grid, Paper, Table, TableBody, 
  TableCell, TableContainer, TableHead, TableRow, Chip,
  Card, CardContent, CircularProgress, Button 
} from '@mui/material';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents'; // We'll just use standard text emojis if icon fails
import api from '../services/api'; // Assume configured axios instance

const ModelArenaIntelligence = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [training, setTraining] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const response = await fetch('/api/model_arena/benchmark_report');
      const result = await response.json();
      setData(result);
    } catch (error) {
      console.error("Failed to fetch model arena data", error);
    } finally {
      setLoading(false);
    }
  };

  const handleTrain = async () => {
    setTraining(true);
    try {
      await fetch('/api/model_arena/train_all', { method: 'POST' });
      alert("Training Pipeline Initiated. Check backend logs.");
    } catch (e) {
      console.error(e);
    } finally {
      setTraining(false);
    }
  };

  if (loading) return <CircularProgress />;
  if (!data || !data.models) return <Typography>No model data available.</Typography>;

  const models = Object.values(data.models).sort((a, b) => b.composite_score - a.composite_score);
  const champion = models.find(m => m.status === 'Champion');

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" fontWeight="bold">Model Arena (Champion-Challenger Framework)</Typography>
        <Button variant="contained" color="primary" onClick={handleTrain} disabled={training}>
          {training ? 'Training...' : 'Retrain All Models'}
        </Button>
      </Box>

      {champion && (
        <Card sx={{ mb: 4, bgcolor: '#f0fdf4', border: '1px solid #166534' }}>
          <CardContent>
            <Typography variant="h5" color="#166534" fontWeight="bold" gutterBottom>
              🏆 Current Production Champion: {champion.algorithm} ({champion.model_id})
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={3}>
                <Typography variant="subtitle2" color="textSecondary">Composite Score</Typography>
                <Typography variant="h6">{champion.composite_score}</Typography>
              </Grid>
              <Grid item xs={3}>
                <Typography variant="subtitle2" color="textSecondary">ROC-AUC</Typography>
                <Typography variant="h6">{champion.metrics?.ROC_AUC?.toFixed(4)}</Typography>
              </Grid>
              <Grid item xs={3}>
                <Typography variant="subtitle2" color="textSecondary">Sharpe Ratio (Simulated)</Typography>
                <Typography variant="h6">{champion.metrics?.Sharpe_Ratio?.toFixed(4)}</Typography>
              </Grid>
              <Grid item xs={3}>
                <Typography variant="subtitle2" color="textSecondary">Dataset</Typography>
                <Typography variant="h6">{champion.dataset_version}</Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      <Typography variant="h5" gutterBottom fontWeight="bold">Benchmark Leaderboard</Typography>
      <TableContainer component={Paper} sx={{ mb: 4 }}>
        <Table>
          <TableHead sx={{ bgcolor: '#f3f4f6' }}>
            <TableRow>
              <TableCell fontWeight="bold">Model ID</TableCell>
              <TableCell fontWeight="bold">Algorithm</TableCell>
              <TableCell fontWeight="bold">Status</TableCell>
              <TableCell fontWeight="bold" align="right">Composite Score</TableCell>
              <TableCell fontWeight="bold" align="right">ROC-AUC</TableCell>
              <TableCell fontWeight="bold" align="right">F1 Score</TableCell>
              <TableCell fontWeight="bold" align="right">Log Loss</TableCell>
              <TableCell fontWeight="bold" align="right">Sharpe Ratio</TableCell>
              <TableCell fontWeight="bold" align="right">Max Drawdown</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {models.map((model) => (
              <TableRow key={model.model_id} sx={{ bgcolor: model.status === 'Champion' ? '#f0fdf4' : 'inherit' }}>
                <TableCell>{model.model_id}</TableCell>
                <TableCell>{model.algorithm}</TableCell>
                <TableCell>
                  <Chip 
                    label={model.status} 
                    color={model.status === 'Champion' ? 'success' : model.status === 'Challenger' ? 'warning' : 'default'} 
                    size="small" 
                  />
                </TableCell>
                <TableCell align="right" fontWeight="bold">{model.composite_score}</TableCell>
                <TableCell align="right">{model.metrics?.ROC_AUC?.toFixed(4)}</TableCell>
                <TableCell align="right">{model.metrics?.F1_Score?.toFixed(4)}</TableCell>
                <TableCell align="right">{model.metrics?.Log_Loss?.toFixed(4)}</TableCell>
                <TableCell align="right">{model.metrics?.Sharpe_Ratio?.toFixed(4)}</TableCell>
                <TableCell align="right">{(model.metrics?.Max_Drawdown * 100)?.toFixed(2)}%</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {champion && (
        <Box>
          <Typography variant="h6" gutterBottom>Top 5 SHAP Feature Importances ({champion.algorithm})</Typography>
          <Grid container spacing={2}>
            {Object.entries(champion.feature_importance || {})
              .slice(0, 5)
              .map(([feat, imp], idx) => (
              <Grid item xs={12} sm={6} md={2.4} key={feat}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle2" noWrap title={feat}>{idx + 1}. {feat}</Typography>
                    <Typography variant="h6" color="primary">{(imp * 100).toFixed(4)}</Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}
    </Box>
  );
};

export default ModelArenaIntelligence;
