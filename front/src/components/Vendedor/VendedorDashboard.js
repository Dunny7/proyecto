import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  AppBar,
  Toolbar,
  IconButton,
  Badge,
  Snackbar,
  Alert,
  Button
} from '@mui/material';
import {
  ShoppingCart,
  ExitToApp,
  Receipt
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import MenuProductos from './MenuProductos';
import Carrito from './Carrito';
import MetodoPago from './MetodoPago';
import { getProductos, registrarVenta } from '../../services/api';

const StyledAppBar = styled(AppBar)({
  background: 'linear-gradient(135deg, #1B5E20 0%, #4CAF50 100%)',
});

const ContentContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(3),
  minHeight: 'calc(100vh - 64px)',
  backgroundColor: '#F5F7FA',
}));

function VendedorDashboard({ user, onLogout }) {
  const [productos, setProductos] = useState([]);
  const [carrito, setCarrito] = useState([]);
  const [metodoPago, setMetodoPago] = useState('efectivo');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    cargarProductos();
  }, []);

  const cargarProductos = async () => {
    try {
      const response = await getProductos();
      setProductos(response.data);
    } catch (error) {
      console.error('Error cargando productos:', error);
      setSnackbar({
        open: true,
        message: 'Error al cargar productos',
        severity: 'error'
      });
    }
  };

  const agregarAlCarrito = (producto) => {
    setCarrito(prev => {
      const existente = prev.find(item => item.id === producto.id);
      if (existente) {
        return prev.map(item =>
          item.id === producto.id
            ? { ...item, cantidad: item.cantidad + 1 }
            : item
        );
      }
      return [...prev, { ...producto, cantidad: 1 }];
    });
    
    setSnackbar({
      open: true,
      message: `${producto.nombre} agregado al pedido`,
      severity: 'success'
    });
  };

  const actualizarCantidad = (id, nuevaCantidad) => {
    if (nuevaCantidad <= 0) {
      setCarrito(prev => prev.filter(item => item.id !== id));
    } else {
      setCarrito(prev =>
        prev.map(item =>
          item.id === id ? { ...item, cantidad: nuevaCantidad } : item
        )
      );
    }
  };

  const eliminarDelCarrito = (id) => {
    setCarrito(prev => prev.filter(item => item.id !== id));
  };

  const calcularTotal = () => {
    return carrito.reduce((sum, item) => sum + (item.precio * item.cantidad), 0);
  };

  const finalizarVenta = async () => {
    if (carrito.length === 0) {
      setSnackbar({
        open: true,
        message: 'El carrito está vacío',
        severity: 'warning'
      });
      return;
    }

    setLoading(true);
    try {
      const productosVenta = carrito.map(item => ({
        producto_id: item.id,
        cantidad: item.cantidad,
        precio: item.precio
      }));

      const response = await registrarVenta(productosVenta, metodoPago);
      
      if (response.data.success) {
        setSnackbar({
          open: true,
          message: `¡Venta registrada! Total: $${response.data.total.toLocaleString()}`,
          severity: 'success'
        });
        setCarrito([]);
      }
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Error al registrar la venta',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const imprimirComanda = () => {
    if (carrito.length === 0) {
      setSnackbar({
        open: true,
        message: 'No hay productos para imprimir',
        severity: 'warning'
      });
      return;
    }

    const ventana = window.open('', '_blank');
    ventana.document.write(`
      <html>
        <head><title>Comanda - FRESCA</title></head>
        <body style="font-family: Arial; padding: 20px;">
          <h1 style="color: #1B5E20;">FRESCA Urban Food</h1>
          <p>Fecha: ${new Date().toLocaleString()}</p>
          <p>Vendedor: ${user.nombre}</p>
          <hr>
          ${carrito.map(item => `
            <p>${item.cantidad}x ${item.nombre} - $${(item.precio * item.cantidad).toLocaleString()}</p>
          `).join('')}
          <hr>
          <h2>Total: $${calcularTotal().toLocaleString()}</h2>
          <p>Método de pago: ${metodoPago}</p>
        </body>
      </html>
    `);
    ventana.document.close();
    ventana.print();
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <StyledAppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            FRESCA Urban Food - {user.nombre}
          </Typography>
          
          <IconButton color="inherit" onClick={imprimirComanda}>
            <Receipt />
          </IconButton>
          
          <IconButton color="inherit" onClick={onLogout}>
            <ExitToApp />
          </IconButton>
        </Toolbar>
      </StyledAppBar>

      <ContentContainer>
        <Grid container spacing={3}>
          {/* Menú de productos */}
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 2, borderRadius: 2 }}>
              <Typography variant="h5" gutterBottom sx={{ color: '#1B5E20', fontWeight: 600 }}>
                🍔 Menú de Productos
              </Typography>
              <MenuProductos 
                productos={productos} 
                onAgregar={agregarAlCarrito}
              />
            </Paper>
          </Grid>

          {/* Carrito y pago */}
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 2, borderRadius: 2, mb: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <ShoppingCart sx={{ mr: 1, color: '#1B5E20' }} />
                <Typography variant="h6">Pedido Actual</Typography>
                <Badge 
                  badgeContent={carrito.length} 
                  color="primary" 
                  sx={{ ml: 2 }}
                />
              </Box>
              
              <Carrito 
                items={carrito}
                onActualizarCantidad={actualizarCantidad}
                onEliminar={eliminarDelCarrito}
                total={calcularTotal()}
              />
            </Paper>

            <Paper sx={{ p: 2, borderRadius: 2 }}>
              <MetodoPago 
                valor={metodoPago}
                onChange={setMetodoPago}
              />
              
              <Box sx={{ mt: 2 }}>
                <Typography variant="h6" align="right" sx={{ color: '#1B5E20' }}>
                  Total: ${calcularTotal().toLocaleString()}
                </Typography>
                
                <Button
                  fullWidth
                  variant="contained"
                  size="large"
                  onClick={finalizarVenta}
                  disabled={carrito.length === 0 || loading}
                  sx={{
                    mt: 2,
                    py: 1.5,
                    background: 'linear-gradient(135deg, #1B5E20 0%, #4CAF50 100%)',
                  }}
                >
                  {loading ? 'Procesando...' : 'Finalizar Venta'}
                </Button>
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </ContentContainer>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}

export default VendedorDashboard;