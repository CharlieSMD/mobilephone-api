import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Link
} from '@mui/material';
import { LockOutlined } from '@mui/icons-material';
import { login as loginApi } from '../api/auth';

interface LoginProps {
  onLoginSuccess: (token: string, user: any) => void;
  onSwitchToRegister: () => void;
}

interface LoginForm {
  username: string;
  password: string;
}

const Login: React.FC<LoginProps> = ({ onLoginSuccess, onSwitchToRegister }) => {
  const [formData, setFormData] = useState<LoginForm>({
    username: '',
    password: ''
  });
  const [errors, setErrors] = useState<Partial<LoginForm>>({});
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const validateForm = (): boolean => {
    const newErrors: Partial<LoginForm> = {};

    if (!formData.username.trim()) {
      newErrors.username = 'Username is required';
    }

    if (!formData.password.trim()) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (field: keyof LoginForm) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setFormData({
      ...formData,
      [field]: event.target.value
    });
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors({
        ...errors,
        [field]: ''
      });
    }
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setErrorMessage('');

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      const { token, user } = await loginApi(formData);
      
      // Save token to localStorage
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user));
      
      // Call parent callback
      onLoginSuccess(token, user);
      
    } catch (error: any) {
      if (error.response?.data?.message) {
        setErrorMessage(error.response.data.message);
      } else {
        setErrorMessage('Login failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        backgroundColor: '#f5f5f5'
      }}
    >
      <Card sx={{ maxWidth: 400, width: '100%', mx: 2 }}>
        <CardContent sx={{ p: 4 }}>
          <Box sx={{ textAlign: 'center', mb: 3 }}>
            <LockOutlined sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
            <Typography variant="h4" component="h1" gutterBottom>
              Login
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Sign in to your account
            </Typography>
          </Box>

          {errorMessage && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {errorMessage}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
            <TextField
              fullWidth
              label="Username"
              variant="outlined"
              margin="normal"
              value={formData.username}
              onChange={handleInputChange('username')}
              error={!!errors.username}
              helperText={errors.username}
              disabled={loading}
            />

            <TextField
              fullWidth
              label="Password"
              type="password"
              variant="outlined"
              margin="normal"
              value={formData.password}
              onChange={handleInputChange('password')}
              error={!!errors.password}
              helperText={errors.password}
              disabled={loading}
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              sx={{ mt: 3, mb: 2 }}
              disabled={loading}
            >
              {loading ? <CircularProgress size={24} /> : 'Login'}
            </Button>

            <Box sx={{ textAlign: 'center', mt: 2 }}>
              <Typography variant="body2">
                Don't have an account?{' '}
                <Link
                  component="button"
                  variant="body2"
                  onClick={onSwitchToRegister}
                  sx={{ cursor: 'pointer' }}
                >
                  Sign up
                </Link>
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Login; 