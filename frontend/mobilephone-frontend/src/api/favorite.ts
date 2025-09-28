import axios from 'axios';
import { API_BASE_URL } from '../config';

export const getFavoriteStatus = async (phoneId: number, token: string) => {
  const { data } = await axios.get(`${API_BASE_URL}/api/favorite/${phoneId}/status`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return data as { isFavorite: boolean };
};

export const addFavorite = async (phoneId: number, token: string) => {
  await axios.post(`${API_BASE_URL}/api/favorite/${phoneId}`, {}, {
    headers: { Authorization: `Bearer ${token}` },
  });
};

export const removeFavorite = async (phoneId: number, token: string) => {
  await axios.delete(`${API_BASE_URL}/api/favorite/${phoneId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
};


