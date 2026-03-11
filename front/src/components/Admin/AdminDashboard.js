import React, { useState, useEffect } from 'react';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Grid,
  Paper,
  Tabs,
  Tab
} from '@mui/material';
import {
  ExitToApp,
  Dashboard,
  ListAlt,
  BarChart
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import Estadisticas from './Estadisticas';
import TablaVentas from './TablaVentas';
import Graficos from './Graficos';
import FiltrosFecha from './FiltrosFecha';
import { getEstadisticas } from '../../services/api';

const StyledAppBar = styled(AppBar)({
  background: 'linear-gradient(135deg, #0D47A1 0%, #1976D2 100%)',
});

const ContentContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(3),
  minHeight: 'calc(100vh - 64px)',
  backgroundColor: '#F5F7FA',
}));

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  borderRadius: 16,
  boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
}));

function TabPanel({ children, value, index }) {
  return (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

function AdminDashboard({ user, onLogout }) {
  const [tabValue, setTabValue] = useState(0);
  const [estadisticas, setEstadisticas] = useState({
    ventas_hoy: 0,
    ventas_semana: 0,
    ventas_mes: 0,
    ventas_totales: 0,
    ventas_por_vendedor: [],
    ultimas_ventas: [],
    top_productos: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    cargarEstadisticas();
  }, []);

  const cargarEstadisticas = async () => {
    try {
      const response = await getEstadisticas();
      setEstadisticas(response.data);
    } catch (error) {
      console.error('Error cargando estadísticas:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <StyledAppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            FRESCA Urban Food - Admin: {user.nombre}
          </Typography>
          
          <IconButton color="inherit" onClick={onLogout}>
            <ExitToApp />
          </IconButton>
        </Toolbar>
      </StyledAppBar>

      <ContentContainer>
        <Grid container spacing={3}>
          {/* Filtros de fecha */}
          <Grid item xs={12}>
            <StyledPaper>
              <FiltrosFecha onFiltrar={cargarEstadisticas} />
            </StyledPaper>
          </Grid>

          {/* Tabs de navegación */}
          <Grid item xs={12}>
            <StyledPaper sx={{ p: 0 }}>
              <Tabs
                value={tabValue}
                onChange={(e, v) => setTabValue(v)}
                sx={{
                  borderBottom: 1,
                  borderColor: 'divider',
                  '& .MuiTab-root': { py: 2 }
                }}
              >
                <Tab icon={<Dashboard />} label="RESUMEN" />
                <Tab icon={<ListAlt />} label="VENTAS" />
                <Tab icon={<BarChart />} label="ESTADÍSTICAS" />
              </Tabs>

              {/* Panel Resumen */}
              <TabPanel value={tabValue} index={0}>
                <Estadisticas 
                  data={estadisticas} 
                  loading={loading} 
                />
              </TabPanel>

              {/* Panel Ventas */}
              <TabPanel value={tabValue} index={1}>
                <TablaVentas 
                  ventas={estadisticas.ultimas_ventas}
                  loading={loading}
                />
              </TabPanel>

              {/* Panel Estadísticas */}
              <TabPanel value={tabValue} index={2}>
                <Graficos 
                  ventasPorVendedor={estadisticas.ventas_por_vendedor}
                  topProductos={estadisticas.top_productos}
                />
              </TabPanel>
            </StyledPaper>
          </Grid>
        </Grid>
      </ContentContainer>
    </Box>
  );
}

export default AdminDashboard;