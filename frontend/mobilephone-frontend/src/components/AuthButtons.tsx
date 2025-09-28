import React, { useState } from 'react';
import { Button, Box } from '@mui/material';
import Login from './Login';
import Register from './Register';

interface AuthButtonsProps {
  onLoginSuccess: (token: string, user: any) => void;
}

const AuthButtons: React.FC<AuthButtonsProps> = ({ onLoginSuccess }) => {
  const [showLogin, setShowLogin] = useState(true);

  const handleLoginSuccess = (token: string, user: any) => {
    onLoginSuccess(token, user);
  };

  const handleRegisterSuccess = (token: string, user: any) => {
    onLoginSuccess(token, user);
  };

  const switchToRegister = () => {
    setShowLogin(false);
  };

  const switchToLogin = () => {
    setShowLogin(true);
  };

  return (
    <Box sx={{ display: 'flex', gap: 1 }}>
      {showLogin ? (
        <Login 
          onLoginSuccess={handleLoginSuccess}
          onSwitchToRegister={switchToRegister}
        />
      ) : (
        <Register 
          onRegisterSuccess={handleRegisterSuccess}
          onSwitchToLogin={switchToLogin}
        />
      )}
    </Box>
  );
};

export default AuthButtons;
