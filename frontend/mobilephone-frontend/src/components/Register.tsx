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
import { PersonAddOutlined } from '@mui/icons-material';
import { register as registerApi } from '../api/auth';

interface RegisterProps {
  onRegisterSuccess: (token: string, user: any) => void;
  onSwitchToLogin: () => void;
}

interface RegisterForm {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  firstName: string;
  lastName: string;
}

const Register: React.FC<RegisterProps> = ({ onRegisterSuccess, onSwitchToLogin }) => {
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

    // Username validation
    if (!formData.username.trim()) {
      newErrors.username = 'Username is required';
    } else if (formData.username.length < 3) {
      newErrors.username = 'Username must be at least 3 characters';
    }

    // Email validation
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    // Password validation
    if (!formData.password.trim()) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    // Confirm password validation
    if (!formData.confirmPassword.trim()) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    // First name validation
    if (!formData.firstName.trim()) {
      newErrors.firstName = 'First name is required';
    }

    // Last name validation
    if (!formData.lastName.trim()) {
      newErrors.lastName = 'Last name is required';
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
      const { token, user } = await registerApi({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        firstName: formData.firstName,
        lastName: formData.lastName
      });
      
      // Save token to localStorage
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user));
      
      // Call parent callback
      onRegisterSuccess(token, user);
      
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
      <Card sx={{ maxWidth: 500, width: '100%', mx: 2 }}>
        <CardContent sx={{ p: 4 }}>
          <Box sx={{ textAlign: 'center', mb: 3 }}>
            <PersonAddOutlined sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
            <Typography variant="h4" component="h1" gutterBottom>
              Register
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Create your account
            </Typography>
          </Box>

          {errorMessage && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {errorMessage}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
            <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
              <TextField
                fullWidth
                label="First Name"
                variant="outlined"
                value={formData.firstName}
                onChange={handleInputChange('firstName')}
                error={!!errors.firstName}
                helperText={errors.firstName}
                disabled={loading}
              />
              <TextField
                fullWidth
                label="Last Name"
                variant="outlined"
                value={formData.lastName}
                onChange={handleInputChange('lastName')}
                error={!!errors.lastName}
                helperText={errors.lastName}
                disabled={loading}
              />
            </Box>

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
              label="Email"
              type="email"
              variant="outlined"
              margin="normal"
              value={formData.email}
              onChange={handleInputChange('email')}
              error={!!errors.email}
              helperText={errors.email}
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

            <TextField
              fullWidth
              label="Confirm Password"
              type="password"
              variant="outlined"
              margin="normal"
              value={formData.confirmPassword}
              onChange={handleInputChange('confirmPassword')}
              error={!!errors.confirmPassword}
              helperText={errors.confirmPassword}
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
              {loading ? <CircularProgress size={24} /> : 'Register'}
            </Button>

            <Box sx={{ textAlign: 'center', mt: 2 }}>
              <Typography variant="body2">
                Already have an account?{' '}
                <Link
                  component="button"
                  variant="body2"
                  onClick={onSwitchToLogin}
                  sx={{ cursor: 'pointer' }}
                >
                  Sign in
                </Link>
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Register; 