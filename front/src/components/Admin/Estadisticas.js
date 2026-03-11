import React from 'react';
import { Grid, Paper, Typography, Box, Skeleton } from '@mui/material';
import {
  TrendingUp,
  AttachMoney,
  ShoppingCart,
  People
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';

const StatCard = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  borderRadius: 16,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  transition: 'transform 0.2s',
  '&:hover': {
    transform: 'translateY(-4px)',
    boxShadow: theme.shadows[8],
  },
}));

const IconWrapper = styled(Box)(({ color }) => ({
  width: 60,
  height: 60,
  borderRadius: '50%',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  backgroundColor: color,
  color: 'white',
  fontSize: 30,
}));

function Estadisticas({ data, loading }) {
  const stats = [
    {
      titulo: 'Ventas Hoy',
      valor: data.ventas_hoy,
      icono: <AttachMoney />,
      color: '#4CAF50',
      formato: 'moneda'
    },
    {
      titulo: 'Ventas Semana',
      valor: data.ventas_semana,
      icono: <TrendingUp />,
      color: '#2196F3',
      formato: 'moneda'
    },
    {
      titulo: 'Ventas Mes',
      valor: data.ventas_mes,
      icono: <ShoppingCart />,
      color: '#FF9800',
      formato: 'moneda'
    },
    {
      titulo: 'Total Acumulado',
      valor: data.ventas_totales,
      icono: <People />,
      color: '#9C27B0',
      formato: 'moneda'
    }
  ];

  const formatearMoneda = (valor) => {
    return `$${valor?.toLocaleString() || 0}`;
  };

  if (loading) {
    return (
      <Grid container spacing={3}>
        {[1, 2, 3, 4].map((i) => (
          <Grid item xs={12} sm={6} md={3} key={i}>
            <Skeleton variant="rounded" height={120} />
          </Grid>
        ))}
      </Grid>
    );
  }

  return (
    <Grid container spacing={3}>
      {stats.map((stat, index) => (
        <Grid item xs={12} sm={6} md={3} key={index}>
          <StatCard>
            <Box>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {stat.titulo}
              </Typography>
              <Typography variant="h4" sx={{ fontWeight: 700, color: stat.color }}>
                {formatearMoneda(stat.valor)}
              </Typography>
            </Box>
            <IconWrapper color={stat.color}>
              {stat.icono}
            </IconWrapper>
          </StatCard>
        </Grid>
      ))}
    </Grid>
  );
}

export default Estadisticas;