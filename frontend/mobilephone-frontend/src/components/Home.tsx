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
  Menu,
  MenuItem,
  Chip,
  TextField,
  InputAdornment
} from '@mui/material';
import { AccountCircle, Logout, Phone as PhoneIcon, Search, CompareArrows } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import PhoneDetails from './PhoneDetails';
import PhoneCompare from './PhoneCompare';
import FavoriteStar from './FavoriteStar';
import CompactLogin from './CompactLogin';
import CompactRegister from './CompactRegister';
import { getAllPhones, getPhoneById } from '../api/phone';
import type { Phone } from '../types/phone';

// Phone type moved to shared types

const Home: React.FC = () => {
  const { user, logout, login } = useAuth();
  const [phones, setPhones] = useState<Phone[]>([]);
  const [filteredPhones, setFilteredPhones] = useState<Phone[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedPhone, setSelectedPhone] = useState<Phone | null>(null);
  const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false);
  const [isCompareModalOpen, setIsCompareModalOpen] = useState(false);
  const [comparePhones, setComparePhones] = useState<Phone[]>([]);

  useEffect(() => {
    fetchPhones();
  }, []);

  const fetchPhones = async () => {
    try {
      const list = await getAllPhones();
      setPhones(list);
      setFilteredPhones(list);
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

  const handleLoginSuccess = (token: string, userData: any) => {
    login(token, userData);
  };

  const handlePhoneDetailsOpen = async (phone: Phone) => {
    try {
      // Always fetch the latest record by id to ensure fields like Colors are up to date
      const data = await getPhoneById(phone.id);
      setSelectedPhone(data as Phone);
    } catch (err) {
      // Fallback to the cached list item if fetch fails
      setSelectedPhone(phone);
    } finally {
      setIsDetailsModalOpen(true);
    }
  };

  const handlePhoneDetailsClose = () => {
    setIsDetailsModalOpen(false);
    setSelectedPhone(null);
  };

  const handleCompareOpen = async (phone: Phone) => {
    try {
      // Always fetch the latest record by id to ensure fields like Colors are up to date
      const data = await getPhoneById(phone.id);
      setComparePhones([data as Phone]);
      setIsCompareModalOpen(true);
    } catch (err) {
      // Fallback to the cached list item if fetch fails
      setComparePhones([phone]);
      setIsCompareModalOpen(true);
    }
  };

  const handleCompareClose = () => {
    setIsCompareModalOpen(false);
    setComparePhones([]);
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
          <PhoneIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Mobile Phone Catalogue
          </Typography>
          
          {user ? (
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
          ) : (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <CompactLogin onLoginSuccess={handleLoginSuccess} />
              <CompactRegister onRegisterSuccess={handleLoginSuccess} />
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
                {/* Phone Image Section */}
                <Box
                  sx={{
                    height: 180,
                    background: 'white',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    position: 'relative',
                    overflow: 'hidden',
                    borderBottom: '1px solid #f0f0f0'
                  }}
                >
                  {/* Compare Icon */}
                  <Box
                    sx={{
                      position: 'absolute',
                      top: 8,
                      left: 8,
                      zIndex: 1,
                      backgroundColor: 'rgba(255, 255, 255, 0.8)',
                      borderRadius: '50%',
                      '&:hover': {
                        backgroundColor: 'rgba(255, 255, 255, 0.9)',
                        transform: 'scale(1.1)'
                      },
                      transition: 'all 0.2s ease',
                      cursor: 'pointer'
                    }}
                    onClick={() => handleCompareOpen(phone)}
                  >
                    <CompareArrows sx={{ p: 0.5, color: '#667eea' }} />
                  </Box>
                  
                  {/* Favorite Star */}
                  <FavoriteStar phoneId={phone.id} position="card" />
                  {phone.imageUrl ? (
                    <img
                      src={phone.imageUrl}
                      alt={`${phone.brand} ${phone.model}`}
                      style={{
                        maxWidth: '90%',
                        maxHeight: '90%',
                        objectFit: 'contain',
                        borderRadius: '8px'
                      }}
                      onError={(e) => {
                        const target = e.target as HTMLImageElement;
                        target.style.display = 'none';
                        // Show placeholder when image fails to load
                        const placeholder = target.nextElementSibling as HTMLElement;
                        if (placeholder) {
                          placeholder.style.display = 'flex';
                        }
                      }}
                    />
                  ) : null}
                  
                  {/* Placeholder when no image or image fails to load */}
                  <Box
                    sx={{
                      display: phone.imageUrl ? 'none' : 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: '#666',
                      textAlign: 'center',
                      width: '100%',
                      height: '100%',
                      background: 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)'
                    }}
                  >
                    <Typography variant="h6" fontWeight="bold" sx={{ mb: 1, color: '#333' }}>
                      {phone.brand}
                    </Typography>
                    <Typography variant="body1" sx={{ color: '#666', mb: 1 }}>
                      {phone.model}
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#999', fontSize: '0.875rem' }}>
                      📱 No Image Available
                    </Typography>
                  </Box>
                </Box>
                <CardContent sx={{ flexGrow: 1, p: 3 }}>
                  {/* Phone Brand and Model Header */}
                  <Box sx={{ mb: 3, textAlign: 'center' }}>
                    <Typography variant="h6" fontWeight="bold" sx={{ color: '#333', mb: 0.5 }}>
                      {phone.brand}
                    </Typography>
                    <Typography variant="body1" sx={{ color: '#666', fontSize: '0.9rem' }}>
                      {phone.model}
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

      <PhoneCompare
        phones={comparePhones}
        open={isCompareModalOpen}
        onClose={handleCompareClose}
      />
    </Box>
  );
};

export default Home; 