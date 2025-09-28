import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Tooltip,
  CircularProgress
} from '@mui/material';
import { getAbsoluteImageUrl } from '../config';
import { Palette } from '@mui/icons-material';

interface ColorOption {
  name: string;
  imagePath?: string;
  colorCode?: string; // For fallback color display
}

interface ColorSelectorProps {
  colors?: string; // Comma-separated color names
  colorImages?: string; // JSON string mapping colors to image paths
  selectedColor?: string;
  onColorChange: (color: string, imagePath?: string) => void;
  disabled?: boolean;
}

const ColorSelector: React.FC<ColorSelectorProps> = ({
  colors,
  colorImages,
  selectedColor,
  onColorChange,
  disabled = false
}) => {
  const [colorOptions, setColorOptions] = useState<ColorOption[]>([]);
  const [loading, setLoading] = useState(false);

  // Parse colors and color images
  useEffect(() => {
    if (!colors) {
      setColorOptions([]);
      return;
    }

    const colorList = colors.split(',').map(c => c.trim()).filter(c => c.length > 0);
    let parsedColorImages: Record<string, string> = {};

    // Parse color images JSON
    if (colorImages) {
      try {
        parsedColorImages = JSON.parse(colorImages);
      } catch (error) {
        console.warn('Failed to parse color images JSON:', error);
      }
    }

    // Create color options
    const options: ColorOption[] = colorList.map(colorName => ({
      name: colorName,
      imagePath: parsedColorImages[colorName],
      colorCode: getColorCode(colorName)
    }));

    setColorOptions(options);

    // Auto-select first color if none selected
    if (options.length > 0 && !selectedColor) {
      onColorChange(options[0].name, options[0].imagePath);
    }
  }, [colors, colorImages, selectedColor, onColorChange]);

  // Get color code for fallback display
  const getColorCode = (colorName: string): string => {
    const colorMap: Record<string, string> = {
      'black': '#000000',
      'white': '#FFFFFF',
      'red': '#FF0000',
      'blue': '#0000FF',
      'green': '#00FF00',
      'yellow': '#FFFF00',
      'purple': '#800080',
      'pink': '#FFC0CB',
      'gold': '#FFD700',
      'silver': '#C0C0C0',
      'space black': '#1C1C1E',
      'midnight': '#1C1C1E',
      'starlight': '#F5F5F7',
      'graphite': '#4A4A4A',
      'sierra blue': '#87CEEB',
      'alpine green': '#4A5D23',
      'natural titanium': '#D4D4D2',
      'desert titanium': '#E4D5B7',
      'blue titanium': '#4A90E2',
      'white titanium': '#F5F5F7',
      'black titanium': '#1C1C1E',
      'cosmic grey': '#696969',
      'cosmic black': '#000000',
      'cloud white': '#F5F5F5',
      'phantom black': '#000000',
      'cream': '#F5F5DC',
      'lavender': '#E6E6FA',
      'sky blue': '#87CEEB',
      'lime': '#00FF00',
      'mystic bronze': '#CD7F32',
      'mystic black': '#000000',
      'golden black': '#8B4513',
      'cocoa gold': '#D2691E',
      'pearl white': '#F8F8FF',
      'charm pink': '#FFB6C1'
    };

    const normalizedName = colorName.toLowerCase().trim();
    return colorMap[normalizedName] || '#CCCCCC'; // Default grey
  };

  const handleColorClick = (color: ColorOption) => {
    if (disabled) return;
    
    setLoading(true);
    onColorChange(color.name, color.imagePath);
    
    // Simulate loading for better UX
    setTimeout(() => {
      setLoading(false);
    }, 300);
  };

  if (colorOptions.length === 0) {
    return null;
  }

  return (
    <Box sx={{ mb: 3 }}>
      <Typography 
        variant="h6" 
        gutterBottom 
        sx={{ 
          color: '#667eea', 
          display: 'flex', 
          alignItems: 'center',
          mb: 2
        }}
      >
        <Palette sx={{ mr: 1 }} />
        Available Colors
      </Typography>
      
      <Box sx={{ 
        display: 'flex', 
        flexWrap: 'nowrap', // Prevent wrapping
        gap: 0.8, // Reduce spacing for compact layout
        alignItems: 'flex-start', // Align to top
        overflowX: 'auto', // Allow horizontal scroll if content overflows
        pb: 1 // Add space for scrollbar
      }}>
        {colorOptions.map((color, index) => {
          const isSelected = selectedColor === color.name;
          const hasImage = !!color.imagePath;
          
          return (
            <Tooltip 
              key={index}
              title={`${color.name}${hasImage ? ' (with actual phone image)' : ''}`}
              arrow
              placement="top"
            >
              <Box
                sx={{
                  position: 'relative',
                  cursor: disabled ? 'default' : 'pointer',
                  opacity: disabled ? 0.6 : 1,
                  transition: 'all 0.2s ease',
                  minWidth: '40px', // Reduce width since no text space needed
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  '&:hover': disabled ? {} : {
                    transform: 'scale(1.05)',
                    zIndex: 1
                  }
                }}
                onClick={() => handleColorClick(color)}
              >
                {/* Color circle */}
                <Box
                  sx={{
                    width: 32,
                    height: 32,
                    borderRadius: '50%',
                    border: isSelected ? '2px solid #667eea' : '1px solid #e0e0e0',
                    backgroundColor: color.colorCode,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    position: 'relative',
                    overflow: 'visible', // Make indicator fully visible
                    boxShadow: isSelected ? '0 3px 8px rgba(102, 126, 234, 0.3)' : '0 1px 4px rgba(0,0,0,0.1)',
                    transition: 'all 0.2s ease',
                    '&:hover': disabled ? {} : {
                      boxShadow: '0 3px 10px rgba(0,0,0,0.2)',
                      borderColor: '#667eea'
                    }
                  }}
                >
                  {/* Image overlay if available */}
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
                        opacity: 0.9,
                        border: '1px solid rgba(255,255,255,0.3)' // Add white border for clearer image
                      }}
                    />
                  )}
                  
                  {/* Loading indicator */}
                  {loading && isSelected && (
                    <CircularProgress 
                      size={20} 
                      sx={{ 
                        color: '#667eea',
                        position: 'absolute',
                        zIndex: 2
                      }} 
                    />
                  )}
                  
                  {/* Selected indicator */}
                  {isSelected && !loading && (
                    <Box
                      sx={{
                        position: 'absolute',
                        top: -3,
                        right: -3,
                        width: 10,
                        height: 10,
                        borderRadius: '50%',
                        backgroundColor: '#667eea',
                        border: '2px solid white',
                        zIndex: 2
                      }}
                    />
                  )}
                </Box>
                
                {/* Color name - removed text, only keep tooltip */}
              </Box>
            </Tooltip>
          );
        })}
      </Box>
      
      {/* Image indicator */}
      {colorOptions.some(c => c.imagePath) && (
        <Typography 
          variant="caption" 
          sx={{ 
            display: 'block',
            mt: 1,
            color: '#999',
            fontSize: '0.7rem'
          }}
        >
          💡 Hover over colors to see names • Colors with images show actual phone appearance
        </Typography>
      )}
    </Box>
  );
};

export default ColorSelector;
