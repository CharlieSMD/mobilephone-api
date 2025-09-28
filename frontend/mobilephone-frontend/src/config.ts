// Centralized frontend configuration

// Prefer environment variable in production builds, fallback to localhost for dev
export const API_BASE_URL =
  (process.env.REACT_APP_API_BASE_URL as string | undefined)?.replace(/\/+$/, '') ||
  'http://13.222.58.155:5198';

export const getAbsoluteImageUrl = (path?: string): string => {
  if (!path) return '';
  if (path.startsWith('http://') || path.startsWith('https://')) return path;
  return `${API_BASE_URL}/${path.replace(/^\/+/, '')}`;
};


