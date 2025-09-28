import React, { useState, useEffect } from 'react';
import { IconButton, Tooltip, Snackbar, Alert } from '@mui/material';
import { Star, StarBorder } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { getFavoriteStatus, addFavorite, removeFavorite } from '../api/favorite';

interface FavoriteStarProps {
  phoneId: number;
  size?: 'small' | 'medium' | 'large';
  position?: 'card' | 'details';
}

const FavoriteStar: React.FC<FavoriteStarProps> = ({ 
  phoneId, 
  size = 'medium',
  position = 'card' 
}) => {
  const { isAuthenticated, token } = useAuth();
  const [isFavorite, setIsFavorite] = useState(false);
  const [loading, setIsLoading] = useState(false);
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info';
  }>({ open: false, message: '', severity: 'info' });

  // Check favorite status when component mounts or user changes
  useEffect(() => {
    if (isAuthenticated && token) {
      checkFavoriteStatus();
    } else {
      setIsFavorite(false);
    }
  }, [isAuthenticated, token, phoneId]);

  const checkFavoriteStatus = async () => {
    try {
      const response = await getFavoriteStatus(phoneId, token!);
      setIsFavorite(response.isFavorite);
    } catch (error) {
      console.error('Failed to check favorite status:', error);
    }
  };

  const handleFavoriteClick = async () => {
    if (!isAuthenticated) {
      showSnackbar('Please login to use favorites', 'info');
      return;
    }

    setIsLoading(true);

    try {
      if (isFavorite) {
        // Remove from favorites
        await removeFavorite(phoneId, token!);
        setIsFavorite(false);
        showSnackbar('Removed from favorites', 'success');
      } else {
        // Add to favorites
        await addFavorite(phoneId, token!);
        setIsFavorite(true);
        showSnackbar('Added to favorites', 'success');
      }
    } catch (error: any) {
      const message = error.response?.data?.message || 'Failed to update favorites';
      showSnackbar(message, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const showSnackbar = (message: string, severity: 'success' | 'error' | 'info') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleSnackbarClose = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  const getStarIcon = () => {
    if (isFavorite) {
      return <Star sx={{ color: '#ffd700' }} />;
    }
    return <StarBorder />;
  };

  const getTooltipTitle = () => {
    if (!isAuthenticated) {
      return 'Login to add to favorites';
    }
    return isFavorite ? 'Remove from favorites' : 'Add to favorites';
  };

  return (
    <>
      <Tooltip title={getTooltipTitle()} placement="top">
        <IconButton
          onClick={handleFavoriteClick}
          disabled={loading}
          size={size}
          sx={{
            position: position === 'card' ? 'absolute' : 'static',
            top: position === 'card' ? 8 : 'auto',
            right: position === 'card' ? 8 : 'auto',
            zIndex: 1,
            backgroundColor: position === 'card' ? 'rgba(255, 255, 255, 0.8)' : 'transparent',
            '&:hover': {
              backgroundColor: position === 'card' ? 'rgba(255, 255, 255, 0.9)' : 'rgba(0, 0, 0, 0.04)',
            }
          }}
        >
          {getStarIcon()}
        </IconButton>
      </Tooltip>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          onClose={handleSnackbarClose} 
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </>
  );
};

export default FavoriteStar;
