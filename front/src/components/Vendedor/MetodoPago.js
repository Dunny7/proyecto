import React from 'react';
import { ToggleButton, ToggleButtonGroup, Box, Typography } from '@mui/material';
import { styled } from '@mui/material/styles';

const StyledToggleButton = styled(ToggleButton)(({ theme }) => ({
  flex: 1,
  padding: theme.spacing(1.5),
  '&.Mui-selected': {
    backgroundColor: '#1B5E20',
    color: 'white',
    '&:hover': {
      backgroundColor: '#0D3D0D',
    },
  },
}));

const metodos = [
  { value: 'efectivo', label: '💵 Efectivo', icon: '💰' },
  { value: 'nequi', label: '📱 Nequi', icon: '📲' },
  { value: 'tarjeta', label: '💳 Tarjeta', icon: '💳' },
  { value: 'daviplata', label: '📲 DaviPlata', icon: '📱' },
];

function MetodoPago({ valor, onChange }) {
  return (
    <Box>
      <Typography variant="subtitle2" gutterBottom>
        Método de Pago
      </Typography>
      <ToggleButtonGroup
        value={valor}
        exclusive
        onChange={(e, nuevo) => nuevo && onChange(nuevo)}
        sx={{ display: 'flex', gap: 1 }}
      >
        {metodos.map((metodo) => (
          <StyledToggleButton key={metodo.value} value={metodo.value}>
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <span>{metodo.icon}</span>
              <span>{metodo.label}</span>
            </Box>
          </StyledToggleButton>
        ))}
      </ToggleButtonGroup>
    </Box>
  );
}

export default MetodoPago;