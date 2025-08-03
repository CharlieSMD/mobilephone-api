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
  price: number;
  imageUrl: string;
}

const Home: React.FC = () => {
  const { user, logout } = useAuth();
  const [phones, setPhones] = useState<Phone[]>([]);
  const [filteredPhones, setFilteredPhones] = useState<Phone[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

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
        <Box sx={{ mb: 3 }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Search phones by brand, model, or storage..."
            value={searchTerm}
            onChange={handleSearch}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search />
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
              <Card key={phone.id} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <Box
                  sx={{
                    height: 200,
                    backgroundImage: `url(${phone.imageUrl})`,
                    backgroundSize: 'cover',
                    backgroundPosition: 'center',
                    backgroundRepeat: 'no-repeat'
                  }}
                />
                <CardContent sx={{ flexGrow: 1 }}>
                  <Typography variant="h6" component="h2" gutterBottom>
                    {phone.brand}
                  </Typography>
                  <Typography variant="body1" color="text.secondary" gutterBottom>
                    {phone.model}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {phone.storage} • {phone.ram} • {phone.screenSize}"
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Camera: {phone.camera}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Battery: {phone.battery}mAh
                  </Typography>
                  <Typography variant="h5" component="p" color="primary" sx={{ mt: 2 }}>
                    ${phone.price}
                  </Typography>
                </CardContent>
              </Card>
            ))}
          </Box>
        )}
      </Container>
    </Box>
  );
};

export default Home; 