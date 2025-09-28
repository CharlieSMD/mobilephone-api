import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Divider
} from '@mui/material';
import { Close, Info, Storage, Memory, Monitor, Camera, BatteryFull } from '@mui/icons-material';
import ColorSelector from './ColorSelector';
import { getAbsoluteImageUrl } from '../config';
import { Phone } from '../types/phone';
import FavoriteStar from './FavoriteStar';
import { formatSpec } from '../utils/format';

// Phone type moved to shared types

interface PhoneDetailsProps {
  phone: Phone | null;
  open: boolean;
  onClose: () => void;
}

const PhoneDetails: React.FC<PhoneDetailsProps> = ({ phone, open, onClose }) => {
  const [selectedColor, setSelectedColor] = useState<string>('');
  const [selectedColorImage, setSelectedColorImage] = useState<string>('');

  if (!phone) return null;

  // formatting moved to utils

  const handleColorChange = (color: string, imagePath?: string) => {
    setSelectedColor(color);
    setSelectedColorImage(imagePath || '');
  };

  // Get current display image
  const getCurrentImage = () => {
    if (selectedColorImage) {
      // Add server address for relative paths
      return getAbsoluteImageUrl(selectedColorImage);
    }
    return phone.imageUrl || '';
  };

  return (
    <Dialog 
      open={open} 
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 3,
          maxHeight: '90vh'
        }
      }}
    >
      <DialogTitle sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        pb: 1
      }}>
        <Box>
          <Typography variant="h5" component="div" sx={{ fontWeight: 'bold', color: '#667eea' }}>
            {phone.brand} {phone.model}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Detailed Specifications
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <FavoriteStar phoneId={phone.id} position="details" />
          <Button
            onClick={onClose}
            sx={{ minWidth: 'auto', p: 1 }}
          >
            <Close />
          </Button>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ pt: 2 }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          {/* Basic Information */}
          <Box>
            <Typography variant="h6" gutterBottom sx={{ color: '#667eea', display: 'flex', alignItems: 'center' }}>
              <Info sx={{ mr: 1 }} />
              Basic Information
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2, minWidth: '200px' }}>
                <Storage sx={{ mr: 1, color: '#667eea' }} />
                <Box>
                  <Typography variant="body2" color="text.secondary">Storage</Typography>
                  <Typography variant="body1">{formatSpec(phone.storage)}</Typography>
                </Box>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2, minWidth: '200px' }}>
                <Memory sx={{ mr: 1, color: '#667eea' }} />
                <Box>
                  <Typography variant="body2" color="text.secondary">RAM</Typography>
                  <Typography variant="body1">{formatSpec(phone.ram)}</Typography>
                </Box>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2, minWidth: '200px' }}>
                <Monitor sx={{ mr: 1, color: '#667eea' }} />
                <Box>
                  <Typography variant="body2" color="text.secondary">Screen Size</Typography>
                  <Typography variant="body1">{formatSpec(phone.screenSize)}"</Typography>
                </Box>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2, minWidth: '200px' }}>
                <BatteryFull sx={{ mr: 1, color: '#667eea' }} />
                <Box>
                  <Typography variant="body2" color="text.secondary">Battery</Typography>
                  <Typography variant="body1">{formatSpec(phone.battery)} mAh</Typography>
                </Box>
              </Box>
            </Box>
          </Box>

          <Divider />

          {/* Color Selector */}
          {phone.colors && (
            <Box>
              <ColorSelector
                colors={phone.colors}
                colorImages={phone.colorImages}
                selectedColor={selectedColor}
                onColorChange={handleColorChange}
              />
            </Box>
          )}

          <Divider />

          {/* Product Image */}
          <Box>
            <Typography variant="h6" gutterBottom sx={{ color: '#667eea' }}>
              Product Image {selectedColor && `(${selectedColor})`}
            </Typography>
            <Box sx={{ 
              display: 'flex', 
              justifyContent: 'center', 
              alignItems: 'center',
              minHeight: '200px',
              border: '2px dashed #e0e0e0',
              borderRadius: 2,
              bgcolor: '#fafafa',
              position: 'relative'
            }}>
              {getCurrentImage() ? (
                <img 
                  src={getCurrentImage()}
                  alt={`${phone.brand} ${phone.model} ${selectedColor || ''}`}
                  style={{ 
                    maxWidth: '100%', 
                    maxHeight: '180px', 
                    objectFit: 'contain',
                    borderRadius: '8px',
                    transition: 'opacity 0.3s ease'
                  }}
                  onError={(e) => {
                    const target = e.target as HTMLImageElement;
                    target.style.display = 'none';
                    target.nextElementSibling?.setAttribute('style', 'display: block');
                  }}
                />
              ) : null}
              <Typography 
                variant="body2" 
                color="text.secondary" 
                sx={{ 
                  display: getCurrentImage() ? 'none' : 'block',
                  textAlign: 'center'
                }}
              >
                Image placeholder
              </Typography>
            </Box>
          </Box>

          <Divider />

          {/* Camera */}
          <Box>
            <Typography variant="h6" gutterBottom sx={{ color: '#667eea', display: 'flex', alignItems: 'center' }}>
              <Camera sx={{ mr: 1 }} />
              Camera
            </Typography>
            <Typography variant="body1">{formatSpec(phone.camera)}</Typography>
          </Box>

          <Divider />

          {/* Detailed Specifications */}
          <Box>
            <Typography variant="h6" gutterBottom sx={{ color: '#667eea' }}>
              Detailed Specifications
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
              <Box sx={{ mb: 2, minWidth: '200px' }}>
                <Typography variant="body2" color="text.secondary">Weight</Typography>
                <Typography variant="body1">{formatSpec(phone.weight)} {phone.weight ? 'g' : ''}</Typography>
              </Box>
              <Box sx={{ mb: 2, minWidth: '200px' }}>
                <Typography variant="body2" color="text.secondary">Dimensions</Typography>
                <Typography variant="body1">{formatSpec(phone.dimensions)}</Typography>
              </Box>
              <Box sx={{ mb: 2, minWidth: '200px' }}>
                <Typography variant="body2" color="text.secondary">Processor</Typography>
                <Typography variant="body1">{formatSpec(phone.processor)}</Typography>
              </Box>
              <Box sx={{ mb: 2, minWidth: '200px' }}>
                <Typography variant="body2" color="text.secondary">Operating System</Typography>
                <Typography variant="body1">{formatSpec(phone.os)}</Typography>
              </Box>
              <Box sx={{ mb: 2, minWidth: '200px' }}>
                <Typography variant="body2" color="text.secondary">Release Year</Typography>
                <Typography variant="body1">{formatSpec(phone.releaseYear)}</Typography>
              </Box>
              <Box sx={{ mb: 2, minWidth: '200px' }}>
                <Typography variant="body2" color="text.secondary">Network Type</Typography>
                <Typography variant="body1">{formatSpec(phone.networkType)}</Typography>
              </Box>
              <Box sx={{ mb: 2, minWidth: '200px' }}>
                <Typography variant="body2" color="text.secondary">Charging Power</Typography>
                <Typography variant="body1">{formatSpec(phone.chargingPower)}</Typography>
              </Box>
              <Box sx={{ mb: 2, minWidth: '200px' }}>
                <Typography variant="body2" color="text.secondary">Water Resistance</Typography>
                <Typography variant="body1">{formatSpec(phone.waterResistance)}</Typography>
              </Box>
              <Box sx={{ mb: 2, minWidth: '200px' }}>
                <Typography variant="body2" color="text.secondary">Material</Typography>
                <Typography variant="body1">{formatSpec(phone.material)}</Typography>
              </Box>
              <Box sx={{ mb: 2, minWidth: '200px' }}>
                <Typography variant="body2" color="text.secondary">Available Colors</Typography>
                <Typography variant="body1">{formatSpec(phone.colors)}</Typography>
              </Box>
            </Box>
          </Box>

          {/* Future: Additional product images can be added here */}
        </Box>
      </DialogContent>

      <DialogActions sx={{ p: 3, pt: 1 }}>
        <Button 
          onClick={onClose} 
          variant="contained" 
          sx={{ 
            bgcolor: '#667eea',
            '&:hover': { bgcolor: '#5a6fd8' }
          }}
        >
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default PhoneDetails;
