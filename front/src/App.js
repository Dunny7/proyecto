import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Login from './components/Login';
import VendedorDashboard from './components/Vendedor/VendedorDashboard';
import AdminDashboard from './components/Admin/AdminDashboard';
import { getSession, logout } from './services/api';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1B5E20',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", sans-serif',
  },
});

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    verificarSesion();
  }, []);

  const verificarSesion = async () => {
    try {
      const response = await getSession();
      if (response.data.authenticated) {
        setUser(response.data.user);
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = async () => {
    try {
      await logout();
      setUser(null);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  if (loading) {
    return <div>Cargando...</div>;
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <Routes>
          <Route 
            path="/login" 
            element={
              user ? (
                <Navigate to={user.rol === 'admin' ? '/admin' : '/vendedor'} />
              ) : (
                <Login onLogin={handleLogin} />
              )
            } 
          />
          
          <Route 
            path="/vendedor" 
            element={
              user && user.rol === 'vendedor' ? (
                <VendedorDashboard user={user} onLogout={handleLogout} />
              ) : (
                <Navigate to="/login" />
              )
            } 
          />
          
          <Route 
            path="/admin" 
            element={
              user && user.rol === 'admin' ? (
                <AdminDashboard user={user} onLogout={handleLogout} />
              ) : (
                <Navigate to="/login" />
              )
            } 
          />
          
          <Route path="/" element={<Navigate to="/login" />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;