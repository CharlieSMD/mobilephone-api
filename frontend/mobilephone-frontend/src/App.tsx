import React, { useState } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './components/Login';
import Register from './components/Register';
import Home from './components/Home';

// Create theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

// Main app content component
const AppContent: React.FC = () => {
  const { isAuthenticated, loading, login } = useAuth();
  const [showLogin, setShowLogin] = useState(true);

  const handleLoginSuccess = (token: string, user: any) => {
    login(token, user);
  };

  const handleRegisterSuccess = (token: string, user: any) => {
    login(token, user);
  };

  const switchToRegister = () => {
    setShowLogin(false);
  };

  const switchToLogin = () => {
    setShowLogin(true);
  };

  // Show loading spinner while checking authentication
  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh' 
      }}>
        Loading...
      </div>
    );
  }

  // Show authentication pages if not authenticated
  if (!isAuthenticated) {
    return showLogin ? (
      <Login 
        onLoginSuccess={handleLoginSuccess}
        onSwitchToRegister={switchToRegister}
      />
    ) : (
      <Register 
        onRegisterSuccess={handleRegisterSuccess}
        onSwitchToLogin={switchToLogin}
      />
    );
  }

  // Show main app if authenticated
  return <Home />;
};

// Main App component
const App: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </ThemeProvider>
  );
};

export default App;
