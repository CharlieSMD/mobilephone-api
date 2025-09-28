import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  TextField,
  Autocomplete,
  Tooltip,
  Chip
} from '@mui/material';
import { Close, Palette } from '@mui/icons-material';
import ColorSelector from './ColorSelector';
import { getAbsoluteImageUrl } from '../config';
import { getAllPhones } from '../api/phone';
import { Phone } from '../types/phone';
import { formatSpec } from '../utils/format';

// Compact Color Selector for comparison table
const CompactColorSelector: React.FC<{
  colors?: string;
  colorImages?: string;
  selectedColor?: string;
  onColorChange: (color: string, imagePath?: string) => void;
}> = ({ colors, colorImages, selectedColor, onColorChange }) => {
  const [colorOptions, setColorOptions] = useState<Array<{name: string, imagePath?: string, colorCode?: string}>>([]);

  useEffect(() => {
    if (!colors) {
      setColorOptions([]);
      return;
    }

    const colorList = colors.split(',').map(c => c.trim()).filter(c => c.length > 0);
    let parsedColorImages: Record<string, string> = {};

    if (colorImages) {
      try {
        parsedColorImages = JSON.parse(colorImages);
      } catch (error) {
        console.warn('Failed to parse color images JSON:', error);
      }
    }

    const getColorCode = (colorName: string): string => {
      const colorMap: Record<string, string> = {
        'black': '#000000', 'white': '#FFFFFF', 'red': '#FF0000', 'blue': '#0000FF',
        'green': '#00FF00', 'yellow': '#FFFF00', 'purple': '#800080', 'pink': '#FFC0CB',
        'gold': '#FFD700', 'silver': '#C0C0C0', 'space black': '#1C1C1E', 'midnight': '#1C1C1E',
        'starlight': '#F5F5F7', 'graphit': '#4A4A4A', 'sierra blue': '#87CEEB', 'alpine green': '#4A5D23',
        'natural titanium': '#D4D4D2', 'desert titanium': '#E4D5B7', 'blue titanium': '#4A90E2',
        'white titanium': '#F5F5F7', 'black titanium': '#1C1C1E', 'cosmic grey': '#696969',
        'cosmic black': '#000000', 'cloud white': '#F5F5F5', 'phantom black': '#000000'
      };
      const normalizedName = colorName.toLowerCase().trim();
      return colorMap[normalizedName] || '#CCCCCC';
    };

    const options = colorList.map(colorName => ({
      name: colorName,
      imagePath: parsedColorImages[colorName],
      colorCode: getColorCode(colorName)
    }));

    setColorOptions(options);

    if (options.length > 0 && !selectedColor) {
      onColorChange(options[0].name, options[0].imagePath);
    }
  }, [colors, colorImages, selectedColor, onColorChange]);

  if (colorOptions.length === 0) return null;

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 0.5 }}>
      <Typography variant="caption" sx={{ fontSize: '0.65rem', color: '#666', fontWeight: 'medium' }}>
        Colors
      </Typography>
      <Box sx={{ display: 'flex', gap: 0.3 }}>
        {colorOptions.map((color, index) => {
          const isSelected = selectedColor === color.name;
          const hasImage = !!color.imagePath;
          
          return (
            <Tooltip key={index} title={`${color.name}${hasImage ? ' (with image)' : ''}`} arrow>
              <Box
                sx={{
                  width: 20,
                  height: 20,
                  borderRadius: '50%',
                  border: isSelected ? '2px solid #667eea' : '1px solid #e0e0e0',
                  backgroundColor: color.colorCode,
                  cursor: 'pointer',
                  position: 'relative',
                  overflow: 'hidden',
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    transform: 'scale(1.1)',
                    boxShadow: '0 2px 6px rgba(0,0,0,0.2)'
                  }
                }}
                onClick={() => onColorChange(color.name, color.imagePath)}
              >
                {hasImage && (
                  <Box
                    sx={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      bottom: 0,
                      backgroundImage: `url(${getAbsoluteImageUrl(color.imagePath)})`,
                      backgroundSize: 'cover',
                      backgroundPosition: 'center',
                      borderRadius: '50%',
                      opacity: 0.8
                    }}
                  />
                )}
                {isSelected && (
                  <Box
                    sx={{
                      position: 'absolute',
                      top: -2,
                      right: -2,
                      width: 6,
                      height: 6,
                      borderRadius: '50%',
                      backgroundColor: '#667eea',
                      border: '1px solid white',
                      zIndex: 2
                    }}
                  />
                )}
              </Box>
            </Tooltip>
          );
        })}
      </Box>
    </Box>
  );
};

// Phone type moved to shared types

interface PhoneCompareProps {
  phones: Phone[];
  open: boolean;
  onClose: () => void;
}

interface ComparePhone extends Phone {
  selectedColor?: string;
  selectedColorImage?: string;
}

const PhoneCompare: React.FC<PhoneCompareProps> = ({ phones: initialPhones, open, onClose }) => {
  const [comparePhones, setComparePhones] = useState<ComparePhone[]>([]);
  const [allPhones, setAllPhones] = useState<Phone[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open && initialPhones.length > 0) {
      setComparePhones(initialPhones.map(phone => ({ ...phone })));
      fetchAllPhones();
    }
  }, [open, initialPhones]);

  const fetchAllPhones = async () => {
    try {
      const list = await getAllPhones();
      setAllPhones(list);
    } catch (error) {
      console.error('Failed to fetch all phones:', error);
    }
  };

  const addPhoneToCompare = (phone: Phone) => {
    if (comparePhones.length < 4 && !comparePhones.some(p => p.id === phone.id)) {
      setComparePhones([...comparePhones, { ...phone }]);
    }
  };

  const removePhoneFromCompare = (phoneId: number) => {
    if (comparePhones.length > 1) {
      setComparePhones(comparePhones.filter(p => p.id !== phoneId));
    }
  };

  const handleColorChange = (phoneId: number, color: string, imagePath?: string) => {
    setComparePhones(prev => 
      prev.map(phone => 
        phone.id === phoneId 
          ? { ...phone, selectedColor: color, selectedColorImage: imagePath }
          : phone
      )
    );
  };

  const getCurrentImage = (phone: ComparePhone) => {
    if (phone.selectedColorImage) {
      return getAbsoluteImageUrl(phone.selectedColorImage);
    }
    return phone.imageUrl || '';
  };

  // formatting moved to utils

  const getSpecValue = (phone: ComparePhone, specKey: keyof Phone) => {
    const value = phone[specKey];
    if (specKey === 'weight' && value) return formatSpec(value as number, ' g');
    if (specKey === 'battery' && value) return formatSpec(value as number, ' mAh');
    if (specKey === 'screenSize' && value) return formatSpec(value as number, '"');
    return formatSpec(value as any);
  };

  const comparisonSpecs = [
    { key: 'brand' as keyof Phone, label: 'Brand' },
    { key: 'model' as keyof Phone, label: 'Model' },
    { key: 'storage' as keyof Phone, label: 'Storage' },
    { key: 'ram' as keyof Phone, label: 'RAM' },
    { key: 'screenSize' as keyof Phone, label: 'Screen Size' },
    { key: 'camera' as keyof Phone, label: 'Camera' },
    { key: 'battery' as keyof Phone, label: 'Battery' },
    { key: 'weight' as keyof Phone, label: 'Weight' },
    { key: 'dimensions' as keyof Phone, label: 'Dimensions' },
    { key: 'processor' as keyof Phone, label: 'Processor' },
    { key: 'os' as keyof Phone, label: 'Operating System' },
    { key: 'releaseYear' as keyof Phone, label: 'Release Year' },
    { key: 'networkType' as keyof Phone, label: 'Network Type' },
    { key: 'chargingPower' as keyof Phone, label: 'Charging Power' },
    { key: 'waterResistance' as keyof Phone, label: 'Water Resistance' },
    { key: 'material' as keyof Phone, label: 'Material' },
    { key: 'colors' as keyof Phone, label: 'Available Colors' }
  ];

  return (
    <Dialog 
      open={open} 
      onClose={onClose}
      maxWidth="xl"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 3,
          maxHeight: '95vh'
        }
      }}
    >
      <DialogTitle sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        pb: 1
      }}>
        <Typography variant="h5" component="div" sx={{ fontWeight: 'bold', color: '#667eea' }}>
          Phone Comparison
        </Typography>
        <Button
          onClick={onClose}
          sx={{ minWidth: 'auto', p: 1 }}
        >
          <Close />
        </Button>
      </DialogTitle>

      <DialogContent sx={{ pt: 2 }}>
        {/* Phone Selection Section */}
        <Box sx={{ mb: 3, p: 2, bgcolor: '#f8f9fa', borderRadius: 2 }}>
          <Typography variant="h6" gutterBottom sx={{ color: '#667eea' }}>
            Select Phones to Compare
          </Typography>
          
          {/* Current phones in comparison */}
          <Box sx={{ display: 'flex', gap: 2, mb: 2, flexWrap: 'wrap' }}>
            {comparePhones.map((phone, index) => (
              <Chip
                key={phone.id}
                label={`${phone.brand} ${phone.model}`}
                onDelete={comparePhones.length > 1 ? () => removePhoneFromCompare(phone.id) : undefined}
                color="primary"
                variant="outlined"
              />
            ))}
          </Box>

          {/* Add more phones */}
          {comparePhones.length < 4 && (
            <Autocomplete
              options={allPhones.filter(phone => !comparePhones.some(p => p.id === phone.id))}
              getOptionLabel={(option) => `${option.brand} ${option.model}`}
              value={null}
              onChange={(event, newValue) => {
                if (newValue) {
                  addPhoneToCompare(newValue);
                }
              }}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Add phone to compare"
                  placeholder="Search and select a phone..."
                  size="small"
                  sx={{ maxWidth: 300 }}
                />
              )}
            />
          )}
          
          {comparePhones.length >= 4 && (
            <Typography variant="body2" color="text.secondary">
              Maximum 4 phones can be compared at once
            </Typography>
          )}
        </Box>

        {/* Comparison Table */}
        {comparePhones.length > 0 && (
          <TableContainer component={Paper} sx={{ maxHeight: '60vh' }}>
            <Table stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ fontWeight: 'bold', bgcolor: '#f5f5f5', minWidth: 150 }}>
                    Specification
                  </TableCell>
                  {comparePhones.map((phone) => (
                    <TableCell key={phone.id} sx={{ fontWeight: 'bold', bgcolor: '#f5f5f5', minWidth: 200, textAlign: 'center' }}>
                      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 1 }}>
                        {/* Phone Name */}
                        <Box>
                          <Typography variant="body2" fontWeight="bold">
                            {phone.brand}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {phone.model}
                          </Typography>
                        </Box>

                        {/* Horizontal Layout: Phone Image + Color Selector */}
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, width: '100%', justifyContent: 'center' }}>
                          {/* Phone Image */}
                          <Box sx={{ 
                            width: 60, 
                            height: 60, 
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            border: '1px solid #e0e0e0',
                            borderRadius: 1,
                            bgcolor: '#fafafa',
                            flexShrink: 0
                          }}>
                            {getCurrentImage(phone) ? (
                              <img 
                                src={getCurrentImage(phone)}
                                alt={`${phone.brand} ${phone.model}`}
                                style={{ 
                                  maxWidth: '100%', 
                                  maxHeight: '100%', 
                                  objectFit: 'contain'
                                }}
                                onError={(e) => {
                                  const target = e.target as HTMLImageElement;
                                  target.style.display = 'none';
                                }}
                              />
                            ) : (
                              <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.6rem' }}>
                                No Image
                              </Typography>
                            )}
                          </Box>

                          {/* Color Selector for this phone - Compact Version */}
                          {phone.colors && (
                            <CompactColorSelector
                              colors={phone.colors}
                              colorImages={phone.colorImages}
                              selectedColor={phone.selectedColor}
                              onColorChange={(color, imagePath) => handleColorChange(phone.id, color, imagePath)}
                            />
                          )}
                        </Box>
                      </Box>
                    </TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {comparisonSpecs.map((spec) => (
                  <TableRow key={spec.key}>
                    <TableCell component="th" scope="row" sx={{ fontWeight: 'medium' }}>
                      {spec.label}
                    </TableCell>
                    {comparePhones.map((phone) => (
                      <TableCell key={`${phone.id}-${spec.key}`} sx={{ textAlign: 'center' }}>
                        {getSpecValue(phone, spec.key)}
                      </TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        {comparePhones.length === 0 && (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="h6" color="text.secondary">
              No phones selected for comparison
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Select phones using the search above to start comparing
            </Typography>
          </Box>
        )}
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

export default PhoneCompare;
