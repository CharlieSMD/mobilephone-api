// Centralized frontend configuration

// API Base URL - prefer environment variable in production builds
export const API_BASE_URL =
  (process.env.REACT_APP_API_BASE_URL as string | undefined)?.replace(/\/+$/, '') ||
  'http://localhost:5198';

// Image Base URL - prefer CloudFront for production
export const IMAGE_BASE_URL =
  (process.env.REACT_APP_IMAGE_BASE_URL as string | undefined)?.replace(/\/+$/, '') ||
  API_BASE_URL;

export const getAbsoluteImageUrl = (path?: string): string => {
  if (!path) return '';
  if (path.startsWith('http://') || path.startsWith('https://')) return path;
  return `${IMAGE_BASE_URL}/${path.replace(/^\/+/, '')}`;
};


