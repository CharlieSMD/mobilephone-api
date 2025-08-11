import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  AppBar,
  Toolbar,
  Button,
  Avatar,
  Menu,
  MenuItem,
  Chip,
  TextField,
  InputAdornment
} from '@mui/material';
import { AccountCircle, Logout, Phone, Search } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import PhoneDetails from './PhoneDetails';
import axios from 'axios';

interface Phone {
  id: number;
  brand: string;
  model: string;
  storage: string;
  ram: string;
  screenSize: string;
  camera: string;
  battery: string;
  imageUrl: string;
}

const Home: React.FC = () => {
  const { user, logout } = useAuth();
  const [phones, setPhones] = useState<Phone[]>([]);
  const [filteredPhones, setFilteredPhones] = useState<Phone[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [imageErrors, setImageErrors] = useState<Set<number>>(new Set());
  const [selectedPhone, setSelectedPhone] = useState<Phone | null>(null);
  const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false);

  useEffect(() => {
    fetchPhones();
  }, []);

  const fetchPhones = async () => {
    try {
      const response = await axios.get('http://localhost:5198/api/phone');
      setPhones(response.data);
      setFilteredPhones(response.data);
    } catch (error) {
      console.error('Failed to fetch phones:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (event: React.ChangeEvent<HTMLInputElement>) => {
    const term = event.target.value;
    setSearchTerm(term);
    
    if (!term.trim()) {
      setFilteredPhones(phones);
    } else {
      const filtered = phones.filter(phone =>
        phone.brand.toLowerCase().includes(term.toLowerCase()) ||
        phone.model.toLowerCase().includes(term.toLowerCase()) ||
        phone.storage.toLowerCase().includes(term.toLowerCase())
      );
      setFilteredPhones(filtered);
    }
  };

  const handleImageError = (phoneId: number) => {
    setImageErrors(prev => new Set(prev).add(phoneId));
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    handleMenuClose();
  };

  const handlePhoneDetailsOpen = (phone: Phone) => {
    setSelectedPhone(phone);
    setIsDetailsModalOpen(true);
  };

  const handlePhoneDetailsClose = () => {
    setIsDetailsModalOpen(false);
    setSelectedPhone(null);
  };

  const getUserInitials = () => {
    if (!user) return '';
    const firstName = user.firstName || '';
    const lastName = user.lastName || '';
    return (firstName.charAt(0) + lastName.charAt(0)).toUpperCase() || user.username.charAt(0).toUpperCase();
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* App Bar */}
      <AppBar position="static">
        <Toolbar>
          <Phone sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Mobile Phone Catalogue
          </Typography>
          
          {user && (
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Chip
                label={`Welcome, ${user.firstName || user.username}`}
                color="secondary"
                sx={{ mr: 2 }}
              />
              <Button
                color="inherit"
                onClick={handleMenuOpen}
                startIcon={<AccountCircle />}
              >
                {getUserInitials()}
              </Button>
              <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleMenuClose}
              >
                <MenuItem disabled>
                  <Typography variant="body2">
                    {user.email}
                  </Typography>
                </MenuItem>
                <MenuItem onClick={handleLogout}>
                  <Logout sx={{ mr: 1 }} />
                  Logout
                </MenuItem>
              </Menu>
            </Box>
          )}
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Available Phones
        </Typography>
        
        {/* Search Bar */}
        <Box sx={{ mb: 4 }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Search phones by brand, model, or storage..."
            value={searchTerm}
            onChange={handleSearch}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 3,
                '&:hover fieldset': {
                  borderColor: '#667eea',
                },
                '&.Mui-focused fieldset': {
                  borderColor: '#667eea',
                },
              },
            }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search sx={{ color: '#667eea' }} />
                </InputAdornment>
              ),
            }}
          />
        </Box>
        
        {loading ? (
          <Typography>Loading phones...</Typography>
        ) : (
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(3, 1fr)', lg: 'repeat(4, 1fr)' }, gap: 3 }}>
            {filteredPhones.map((phone) => (
              <Card key={phone.id} sx={{ height: '100%', display: 'flex', flexDirection: 'column', transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-4px)', boxShadow: 3 } }}>
                <Box
                  sx={{
                    height: 120,
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    position: 'relative',
                    overflow: 'hidden'
                  }}
                >
                  <Box sx={{ textAlign: 'center', color: 'white' }}>
                    <Typography variant="h5" fontWeight="bold" sx={{ mb: 1 }}>
                      {phone.brand}
                    </Typography>
                    <Typography variant="body1" sx={{ opacity: 0.9 }}>
                      {phone.model}
                    </Typography>
                  </Box>
                  <Box
                    sx={{
                      position: 'absolute',
                      top: -50,
                      right: -50,
                      width: 100,
                      height: 100,
                      borderRadius: '50%',
                      background: 'rgba(255,255,255,0.1)',
                      zIndex: 1
                    }}
                  />
                </Box>
                <CardContent sx={{ flexGrow: 1, p: 3 }}>
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="body2" color="text.secondary" gutterBottom sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <Box component="span" sx={{ mr: 1, fontSize: '1.2em' }}>📱</Box>
                      {phone.storage} • {phone.ram} • {phone.screenSize}"
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <Box component="span" sx={{ mr: 1, fontSize: '1.2em' }}>📷</Box>
                      {phone.camera}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                      <Box component="span" sx={{ mr: 1, fontSize: '1.2em' }}>🔋</Box>
                      {phone.battery}mAh
                    </Typography>
                  </Box>
                  <Box sx={{ 
                    mt: 'auto', 
                    pt: 2, 
                    borderTop: '1px solid #e0e0e0',
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center'
                  }}>
                    <Box sx={{ 
                      px: 2, 
                      py: 1, 
                      borderRadius: 2, 
                      bgcolor: '#667eea', 
                      color: 'white',
                      fontSize: '0.875rem',
                      fontWeight: 'medium',
                      cursor: 'pointer',
                      '&:hover': {
                        bgcolor: '#5a6fd8'
                      }
                    }} onClick={() => handlePhoneDetailsOpen(phone)}>
                      View Details
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            ))}
          </Box>
        )}
      </Container>

      {selectedPhone && (
        <PhoneDetails
          phone={selectedPhone}
          open={isDetailsModalOpen}
          onClose={handlePhoneDetailsClose}
        />
      )}
    </Box>
  );
};

export default Home; 