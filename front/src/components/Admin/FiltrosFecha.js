import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Grid
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { es } from 'date-fns/locale';

function FiltrosFecha({ onFiltrar }) {
  const [fechaInicio, setFechaInicio] = useState(new Date());
  const [fechaFin, setFechaFin] = useState(new Date());

  const handleFiltrar = () => {
    onFiltrar({
      inicio: fechaInicio.toISOString().split('T')[0],
      fin: fechaFin.toISOString().split('T')[0]
    });
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={es}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={4}>
            <DatePicker
              label="Fecha Inicio"
              value={fechaInicio}
              onChange={setFechaInicio}
              renderInput={(params) => <TextField {...params} fullWidth />}
            />
          </Grid>
          
          <Grid item xs={12} sm={4}>
            <DatePicker
              label="Fecha Fin"
              value={fechaFin}
              onChange={setFechaFin}
              renderInput={(params) => <TextField {...params} fullWidth />}
            />
          </Grid>
          
          <Grid item xs={12} sm={4}>
            <Button
              variant="contained"
              onClick={handleFiltrar}
              fullWidth
              sx={{
                py: 1.5,
                background: 'linear-gradient(135deg, #1B5E20 0%, #4CAF50 100%)',
              }}
            >
              Filtrar Ventas
            </Button>
          </Grid>
        </Grid>
      </Box>
    </LocalizationProvider>
  );
}

export default FiltrosFecha;