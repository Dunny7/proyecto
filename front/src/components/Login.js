import React, { useState } from 'react';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  InputAdornment,
  IconButton
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import { login } from '../services/api';
import { useNavigate } from 'react-router-dom';

const StyledPaper = styled(Paper)(({ theme }) => ({
  marginTop: theme.spacing(8),
  padding: theme.spacing(4),
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  borderRadius: 16,
  boxShadow: '0 8px 24px rgba(0,0,0,0.12)',
}));

const Logo = styled(Box)(({ theme }) => ({
  width: 120,
  height: 120,
  borderRadius: '50%',
  background: 'linear-gradient(135deg, #1B5E20 0%, #4CAF50 100%)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  marginBottom: theme.spacing(2),
  '& svg': {
    fontSize: 64,
    color: 'white',
  },
}));

function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const response = await login(username, password);
      if (response.data.success) {
        onLogin(response.data.user);
        navigate(response.data.user.rol === 'admin' ? '/admin' : '/vendedor');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Error al iniciar sesión');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container component="main" maxWidth="xs">
      <StyledPaper>
        <Logo>
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
          </svg>
        </Logo>
        
        <Typography component="h1" variant="h4" sx={{ fontWeight: 700, color: '#1B5E20', mb: 1 }}>
          FRESCA
        </Typography>
        
        <Typography variant="subtitle1" sx={{ color: 'text.secondary', mb: 3 }}>
          Urban Food - Sistema de Gestión
        </Typography>
        
        {error && <Alert severity="error" sx={{ width: '100%', mb: 2 }}>{error}</Alert>}
        
        <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%' }}>
          <TextField
            margin="normal"
            required
            fullWidth
            label="Usuario"
            autoFocus
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            variant="outlined"
            sx={{ mb: 2 }}
          />
          
          <TextField
            margin="normal"
            required
            fullWidth
            label="Contraseña"
            type={showPassword ? 'text' : 'password'}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            variant="outlined"
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    onClick={() => setShowPassword(!showPassword)}
                    edge="end"
                  >
                    {showPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
            sx={{ mb: 3 }}
          />
          
          <Button
            type="submit"
            fullWidth
            variant="contained"
            disabled={loading}
            sx={{
              py: 1.5,
              background: 'linear-gradient(135deg, #1B5E20 0%, #4CAF50 100%)',
              '&:hover': {
                background: 'linear-gradient(135deg, #0D3D0D 0%, #3D8B40 100%)',
              },
            }}
          >
            {loading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
          </Button>
        </Box>
        
        <Box sx={{ mt: 3, width: '100%' }}>
          <Typography variant="body2" color="text.secondary" align="center">
            Credenciales de prueba:
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'center', gap: 3, mt: 1 }}>
            <Box>
              <Typography variant="caption" color="text.secondary">Admin</Typography>
              <Typography variant="body2" fontWeight="bold">admin / admin123</Typography>
            </Box>
            <Box>
              <Typography variant="caption" color="text.secondary">Vendedor</Typography>
              <Typography variant="body2" fontWeight="bold">vendedor1 / vende123</Typography>
            </Box>
          </Box>
        </Box>
      </StyledPaper>
    </Container>
  );
}

export default Login;