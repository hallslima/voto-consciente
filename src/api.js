const LOCAL_API_BASE_URL = 'http://127.0.0.1:8000';

export function normalizeApiBaseUrl(value) {
  const configuredUrl = value?.trim() || LOCAL_API_BASE_URL;
  return configuredUrl.replace(/\/+$/, '');
}

export const API_BASE_URL = normalizeApiBaseUrl(import.meta.env?.VITE_API_BASE_URL);

export function apiUrl(path) {
  return `${API_BASE_URL}/${String(path).replace(/^\/+/, '')}`;
}
