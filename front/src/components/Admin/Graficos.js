import React from 'react';
import { Grid, Paper, Typography, Box } from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer
} from 'recharts';

const COLORS = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336'];

function Graficos({ ventasPorVendedor, topProductos }) {
  // Preparar datos para gráfico de barras
  const datosVendedores = ventasPorVendedor?.map(v => ({
    nombre: v.nombre || v.vendedor,
    ventas: v.ventas || 0,
    total: v.total || 0
  })) || [];

  // Preparar datos para gráfico de pastel (productos)
  const datosProductos = topProductos?.map((p, index) => ({
    name: p.nombre || p.producto,
    value: p.cantidad || p.total_vendido || 0
  })) || [];

  return (
    <Grid container spacing={3}>
      {/* Gráfico de ventas por vendedor */}
      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 3, borderRadius: 2 }}>
          <Typography variant="h6" gutterBottom sx={{ color: '#1B5E20' }}>
            Ventas por Vendedor
          </Typography>
          <Box sx={{ height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={datosVendedores}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="nombre" />
                <YAxis />
                <Tooltip 
                  formatter={(value) => `$${value.toLocaleString()}`}
                />
                <Legend />
                <Bar dataKey="total" fill="#4CAF50" name="Total vendido" />
              </BarChart>
            </ResponsiveContainer>
          </Box>
        </Paper>
      </Grid>

      {/* Gráfico de productos más vendidos */}
      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 3, borderRadius: 2 }}>
          <Typography variant="h6" gutterBottom sx={{ color: '#1B5E20' }}>
            Productos más Vendidos
          </Typography>
          <Box sx={{ height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={datosProductos}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => entry.name}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {datosProductos.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Box>
        </Paper>
      </Grid>
    </Grid>
  );
}

export default Graficos;