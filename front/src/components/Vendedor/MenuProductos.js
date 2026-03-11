import React from 'react';
import { Grid, Card, CardContent, Typography, Button, Box } from '@mui/material';
import { styled } from '@mui/material/styles';

const ProductCard = styled(Card)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  transition: 'transform 0.2s, box-shadow 0.2s',
  cursor: 'pointer',
  '&:hover': {
    transform: 'translateY(-4px)',
    boxShadow: theme.shadows[8],
  },
}));

const ProductPrice = styled(Typography)(({ theme }) => ({
  color: '#1B5E20',
  fontWeight: 700,
  fontSize: '1.5rem',
  marginBottom: theme.spacing(1),
}));

const CategoryBadge = styled(Box)(({ category, theme }) => {
  const colors = {
    hamburguesa: { bg: '#FFE0B2', color: '#E65100' },
    perro: { bg: '#FFCDD2', color: '#B71C1C' },
    bebida: { bg: '#BBDEFB', color: '#0D47A1' },
    adicional: { bg: '#C8E6C9', color: '#1B5E20' },
  };
  const style = colors[category] || { bg: '#E0E0E0', color: '#424242' };
  
  return {
    backgroundColor: style.bg,
    color: style.color,
    padding: '4px 12px',
    borderRadius: 20,
    fontSize: '0.8rem',
    fontWeight: 600,
    display: 'inline-block',
    marginBottom: theme.spacing(1),
  };
});

const getIcon = (categoria) => {
  switch(categoria) {
    case 'hamburguesa': return '🍔';
    case 'perro': return '🌭';
    case 'bebida': return '🥤';
    default: return '🧀';
  }
};

function MenuProductos({ productos, onAgregar }) {
  return (
    <Grid container spacing={2}>
      {productos.map((producto) => (
        <Grid item xs={12} sm={6} md={4} key={producto.id}>
          <ProductCard onClick={() => onAgregar(producto)}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <CategoryBadge category={producto.categoria}>
                  {getIcon(producto.categoria)} {producto.categoria}
                </CategoryBadge>
                <Typography variant="caption" color="text.secondary">
                  {producto.codigo}
                </Typography>
              </Box>
              
              <Typography variant="h6" component="h3" sx={{ mt: 1, fontWeight: 600 }}>
                {producto.nombre}
              </Typography>
              
              <ProductPrice>
                ${producto.precio.toLocaleString()}
              </ProductPrice>
              
              <Button 
                variant="contained" 
                fullWidth
                onClick={(e) => {
                  e.stopPropagation();
                  onAgregar(producto);
                }}
                sx={{
                  background: 'linear-gradient(135deg, #1B5E20 0%, #4CAF50 100%)',
                }}
              >
                Agregar al pedido
              </Button>
            </CardContent>
          </ProductCard>
        </Grid>
      ))}
    </Grid>
  );
}

export default MenuProductos;