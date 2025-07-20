import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Grid,
  Card,
  CardContent,
  CardMedia,
  Button,
  Box,
  Rating,
  TextField,
  InputAdornment
} from '@mui/material';
import { Search, Phone } from '@mui/icons-material';
import './App.css';

interface Phone {
  id: number;
  brand: string;
  model: string;
  price: number;
  image?: string;
  rating?: number;
}

function App() {
  const [phones, setPhones] = useState<Phone[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  // Sample data - in real app, this would come from API
  const samplePhones: Phone[] = [
    {
      id: 1,
      brand: 'Apple',
      model: 'iPhone 15 Pro',
      price: 999.99,
      rating: 4.5
    },
    {
      id: 2,
      brand: 'Samsung',
      model: 'Galaxy S24 Ultra',
      price: 1199.99,
      rating: 4.3
    },
    {
      id: 3,
      brand: 'Google',
      model: 'Pixel 8 Pro',
      price: 899.99,
      rating: 4.7
    }
  ];

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setPhones(samplePhones);
      setLoading(false);
    }, 1000);
  }, [samplePhones]);

  const filteredPhones = phones.filter(phone =>
    phone.brand.toLowerCase().includes(searchTerm.toLowerCase()) ||
    phone.model.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="App">
      <AppBar position="static">
        <Toolbar>
          <Phone sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Mobile Phone Catalogue
          </Typography>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Discover Amazing Phones
          </Typography>
          <Typography variant="body1" color="text.secondary" gutterBottom>
            Find the perfect phone for your needs
          </Typography>
        </Box>

        <TextField
          fullWidth
          variant="outlined"
          placeholder="Search phones by brand or model..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search />
              </InputAdornment>
            ),
          }}
          sx={{ mb: 4 }}
        />

        {loading ? (
          <Typography variant="h6" textAlign="center">
            Loading phones...
          </Typography>
        ) : (
          <Grid container spacing={3}>
            {filteredPhones.map((phone) => (
              <Grid key={phone.id} sx={{ gridColumn: { xs: 'span 12', sm: 'span 6', md: 'span 4' } }}>
                <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <CardMedia
                    component="img"
                    height="200"
                    image={`https://via.placeholder.com/300x200/cccccc/666666?text=${phone.brand}+${phone.model}`}
                    alt={`${phone.brand} ${phone.model}`}
                  />
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Typography gutterBottom variant="h6" component="h2">
                      {phone.brand} {phone.model}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <Rating value={phone.rating} precision={0.1} readOnly size="small" />
                      <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
                        ({phone.rating})
                      </Typography>
                    </Box>
                    <Typography variant="h6" color="primary" gutterBottom>
                      ${phone.price}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                      <Button variant="contained" size="small" fullWidth>
                        View Details
                      </Button>
                      <Button variant="outlined" size="small" fullWidth>
                        Add to Favorites
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}

        {!loading && filteredPhones.length === 0 && (
          <Typography variant="h6" textAlign="center" color="text.secondary">
            No phones found matching your search.
          </Typography>
        )}
      </Container>
    </div>
  );
}

export default App;
