import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Link,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import { login as loginApi } from '../api/auth';

interface CompactLoginProps {
  onLoginSuccess: (token: string, user: any) => void;
}

interface LoginForm {
  username: string;
  password: string;
}

const CompactLogin: React.FC<CompactLoginProps> = ({ onLoginSuccess }) => {
  const [open, setOpen] = useState(false);
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
      
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user));
      
      onLoginSuccess(token, user);
      setOpen(false);
      
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

  const handleOpen = () => {
    setOpen(true);
    setErrorMessage('');
    setFormData({ username: '', password: '' });
    setErrors({});
  };

  const handleClose = () => {
    setOpen(false);
    setErrorMessage('');
    setFormData({ username: '', password: '' });
    setErrors({});
  };

  return (
    <>
      <Button color="inherit" onClick={handleOpen}>
        Login
      </Button>
      
      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>Login</DialogTitle>
        <form onSubmit={handleSubmit}>
          <DialogContent>
            {errorMessage && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {errorMessage}
              </Alert>
            )}
            
            <TextField
              fullWidth
              label="Username"
              value={formData.username}
              onChange={handleInputChange('username')}
              error={!!errors.username}
              helperText={errors.username}
              margin="normal"
              disabled={loading}
            />
            
            <TextField
              fullWidth
              label="Password"
              type="password"
              value={formData.password}
              onChange={handleInputChange('password')}
              error={!!errors.password}
              helperText={errors.password}
              margin="normal"
              disabled={loading}
            />
          </DialogContent>
          
          <DialogActions>
            <Button onClick={handleClose} disabled={loading}>
              Cancel
            </Button>
            <Button 
              type="submit" 
              variant="contained" 
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : null}
            >
              {loading ? 'Logging in...' : 'Login'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </>
  );
};

export default CompactLogin;
