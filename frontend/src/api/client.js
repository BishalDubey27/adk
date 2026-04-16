/**
 * API client for Tech Sarathi backend
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// API methods
export const api = {
  // Projects
  projects: {
    list: () => apiClient.get('/projects'),
    get: (id) => apiClient.get(`/projects/${id}`),
    create: (data) => apiClient.post('/projects', data),
    update: (id, data) => apiClient.patch(`/projects/${id}`, data),
    delete: (id) => apiClient.delete(`/projects/${id}`),
  },

  // Tasks
  tasks: {
    list: (projectId) => apiClient.get(`/projects/${projectId}/tasks`),
    update: (id, data) => apiClient.patch(`/tasks/${id}`, data),
  },

  // Escalations
  escalations: {
    list: (status = 'pending') => apiClient.get(`/escalations?status=${status}`),
    get: (id) => apiClient.get(`/escalations/${id}`),
    approve: (id, data) => apiClient.post(`/escalations/${id}/approve`, data),
  },

  // Audit
  audit: {
    list: (params = {}) => apiClient.get('/audit', { params }),
  },

  // Team
  team: {
    list: () => apiClient.get('/team'),
    get: (id) => apiClient.get(`/team/${id}`),
    create: (data) => apiClient.post('/team', data),
  },
};

export default apiClient;
