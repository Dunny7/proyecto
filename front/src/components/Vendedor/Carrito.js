import React from 'react';
import {
  List,
  ListItem,
  IconButton,
  Typography,
  Box,
  Divider
} from '@mui/material';
import { Delete, Add, Remove } from '@mui/icons-material';
import { styled } from '@mui/material/styles';

const CartItem = styled(ListItem)(({ theme }) => ({
  backgroundColor: '#F8F9FA',
  marginBottom: theme.spacing(1),
  borderRadius: 8,
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(1),
}));

const QuantityControl = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(0.5),
  minWidth: 100,
}));

const ItemInfo = styled(Box)({
  flex: 2,
});

const ItemPrice = styled(Box)({
  minWidth: 80,
  textAlign: 'right',
  fontWeight: 600,
  color: '#1B5E20',
});

function Carrito({ items, onActualizarCantidad, onEliminar }) {
  // Función para formatear moneda
  const formatearMoneda = (valor) => {
    return `$${valor.toLocaleString('es-CO')}`;
  };

  // Calcular total
  const calcularTotal = () => {
    return items.reduce((sum, item) => sum + (item.precio * item.cantidad), 0);
  };

  if (!items || items.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', py: 4, color: 'text.secondary' }}>
        <Typography variant="body1">🛒 El carrito está vacío</Typography>
        <Typography variant="caption">Agrega productos del menú</Typography>
      </Box>
    );
  }

  return (
    <>
      <List sx={{ maxHeight: 400, overflow: 'auto' }}>
        {items.map((item) => (
          <CartItem key={item.id}>
            <ItemInfo>
              <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                {item.nombre}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {formatearMoneda(item.precio)} c/u
              </Typography>
            </ItemInfo>
            
            <QuantityControl>
              <IconButton 
                size="small" 
                onClick={() => onActualizarCantidad(item.id, item.cantidad - 1)}
                sx={{ bgcolor: '#f0f0f0', '&:hover': { bgcolor: '#e0e0e0' } }}
              >
                <Remove fontSize="small" />
              </IconButton>
              
              <Typography sx={{ minWidth: 30, textAlign: 'center', fontWeight: 600 }}>
                {item.cantidad}
              </Typography>
              
              <IconButton 
                size="small"
                onClick={() => onActualizarCantidad(item.id, item.cantidad + 1)}
                sx={{ bgcolor: '#f0f0f0', '&:hover': { bgcolor: '#e0e0e0' } }}
              >
                <Add fontSize="small" />
              </IconButton>
            </QuantityControl>
            
            <ItemPrice>
              {formatearMoneda(item.precio * item.cantidad)}
            </ItemPrice>
            
            <IconButton 
              size="small" 
              color="error"
              onClick={() => onEliminar(item.id)}
              sx={{ '&:hover': { bgcolor: '#ffebee' } }}
            >
              <Delete fontSize="small" />
            </IconButton>
          </CartItem>
        ))}
      </List>
      
      <Divider sx={{ my: 2 }} />
      
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', px: 1 }}>
        <Typography variant="h6" sx={{ fontWeight: 600 }}>Total:</Typography>
        <Typography variant="h5" sx={{ color: '#1B5E20', fontWeight: 700 }}>
          {formatearMoneda(calcularTotal())}
        </Typography>
      </Box>
    </>
  );
}

export default Carrito;