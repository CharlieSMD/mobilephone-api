import axios from 'axios';
import { API_BASE_URL } from '../config';

export interface LoginForm { username: string; password: string; }
export interface AuthResponse { token: string; user: any; }

export const login = async (form: LoginForm): Promise<AuthResponse> => {
  const { data } = await axios.post(`${API_BASE_URL}/api/user/login`, form);
  return data as AuthResponse;
};

export interface RegisterForm {
  username: string;
  password: string;
  email?: string;
  firstName?: string;
  lastName?: string;
}

export const register = async (form: RegisterForm): Promise<AuthResponse> => {
  const { data } = await axios.post(`${API_BASE_URL}/api/user/register`, form);
  return data as AuthResponse;
};


