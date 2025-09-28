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
import { register as registerApi } from '../api/auth';

interface CompactRegisterProps {
  onRegisterSuccess: (token: string, user: any) => void;
}

interface RegisterForm {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  firstName: string;
  lastName: string;
}

const CompactRegister: React.FC<CompactRegisterProps> = ({ onRegisterSuccess }) => {
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState<RegisterForm>({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: ''
  });
  const [errors, setErrors] = useState<Partial<RegisterForm>>({});
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const validateForm = (): boolean => {
    const newErrors: Partial<RegisterForm> = {};

    if (!formData.username.trim()) {
      newErrors.username = 'Username is required';
    } else if (formData.username.length < 3) {
      newErrors.username = 'Username must be at least 3 characters';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }

    if (!formData.password.trim()) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (field: keyof RegisterForm) => (
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
      const { token, user } = await registerApi({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        firstName: formData.firstName,
        lastName: formData.lastName
      });
      
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user));
      
      onRegisterSuccess(token, user);
      setOpen(false);
      
    } catch (error: any) {
      if (error.response?.data?.message) {
        setErrorMessage(error.response.data.message);
      } else {
        setErrorMessage('Registration failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleOpen = () => {
    setOpen(true);
    setErrorMessage('');
    setFormData({
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      firstName: '',
      lastName: ''
    });
    setErrors({});
  };

  const handleClose = () => {
    setOpen(false);
    setErrorMessage('');
    setFormData({
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      firstName: '',
      lastName: ''
    });
    setErrors({});
  };

  return (
    <>
      <Button color="inherit" onClick={handleOpen}>
        Register
      </Button>
      
      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>Register</DialogTitle>
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
              label="Email"
              type="email"
              value={formData.email}
              onChange={handleInputChange('email')}
              error={!!errors.email}
              helperText={errors.email}
              margin="normal"
              disabled={loading}
            />
            
            <TextField
              fullWidth
              label="First Name"
              value={formData.firstName}
              onChange={handleInputChange('firstName')}
              margin="normal"
              disabled={loading}
            />
            
            <TextField
              fullWidth
              label="Last Name"
              value={formData.lastName}
              onChange={handleInputChange('lastName')}
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
            
            <TextField
              fullWidth
              label="Confirm Password"
              type="password"
              value={formData.confirmPassword}
              onChange={handleInputChange('confirmPassword')}
              error={!!errors.confirmPassword}
              helperText={errors.confirmPassword}
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
              {loading ? 'Registering...' : 'Register'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </>
  );
};

export default CompactRegister;
