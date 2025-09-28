import axios from 'axios';
import { API_BASE_URL } from '../config';
import type { Phone } from '../types/phone';

export const getAllPhones = async (): Promise<Phone[]> => {
  const { data } = await axios.get(`${API_BASE_URL}/api/phone`);
  return data as Phone[];
};

export const getPhoneById = async (id: number): Promise<Phone> => {
  const { data } = await axios.get(`${API_BASE_URL}/api/phone/${id}`);
  return data as Phone;
};


