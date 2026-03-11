import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Typography,
  Box,
  Skeleton
} from '@mui/material';
import { styled } from '@mui/material/styles';

const StyledTableContainer = styled(TableContainer)({
  borderRadius: 12,
  overflow: 'hidden',
});

const StatusChip = styled(Chip)(({ status }) => {
  const colors = {
    pendiente: { bg: '#FFF3E0', color: '#E65100' },
    listo: { bg: '#E8F5E9', color: '#2E7D32' },
    entregado: { bg: '#E3F2FD', color: '#1565C0' },
  };
  const style = colors[status] || colors.pendiente;
  
  return {
    backgroundColor: style.bg,
    color: style.color,
    fontWeight: 600,
  };
});

function TablaVentas({ ventas, loading }) {
  if (loading) {
    return (
      <Box sx={{ p: 2 }}>
        {[1, 2, 3, 4, 5].map((i) => (
          <Skeleton key={i} height={60} sx={{ my: 1 }} />
        ))}
      </Box>
    );
  }

  if (!ventas || ventas.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <Typography variant="body1" color="text.secondary">
          No hay ventas registradas
        </Typography>
      </Box>
    );
  }

  return (
    <StyledTableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow sx={{ backgroundColor: '#F5F5F5' }}>
            <TableCell><strong>ID</strong></TableCell>
            <TableCell><strong>Producto</strong></TableCell>
            <TableCell align="center"><strong>Cantidad</strong></TableCell>
            <TableCell align="right"><strong>Total</strong></TableCell>
            <TableCell><strong>Vendedor</strong></TableCell>
            <TableCell align="center"><strong>Estado</strong></TableCell>
            <TableCell><strong>Fecha</strong></TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {ventas.map((venta) => (
            <TableRow key={venta.id} hover>
              <TableCell>#{venta.id}</TableCell>
              <TableCell>{venta.nombre || venta.producto}</TableCell>
              <TableCell align="center">{venta.cantidad}</TableCell>
              <TableCell align="right" sx={{ fontWeight: 600 }}>
                ${venta.total?.toLocaleString()}
              </TableCell>
              <TableCell>{venta.vendedor || venta.vendedor_nombre}</TableCell>
              <TableCell align="center">
                <StatusChip 
                  label={venta.estado?.toUpperCase() || 'PENDIENTE'}
                  status={venta.estado}
                  size="small"
                />
              </TableCell>
              <TableCell>
                {new Date(venta.fecha).toLocaleString()}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </StyledTableContainer>
  );
}

export default TablaVentas;