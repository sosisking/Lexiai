// API client for LexiAI backend

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';

// Helper function to handle API responses
const handleResponse = async (response) => {
  const data = await response.json();
  
  if (!response.ok) {
    const error = data.error || response.statusText;
    throw new Error(error);
  }
  
  return data;
};

// Helper function to get auth header
const getAuthHeader = () => {
  const token = localStorage.getItem('token');
  return token ? { 'Authorization': `Bearer ${token}` } : {};
};

// Auth API
export const authApi = {
  register: async (userData) => {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });
    return handleResponse(response);
  },
  
  login: async (credentials) => {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials),
    });
    return handleResponse(response);
  },
  
  getCurrentUser: async () => {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: {
        ...getAuthHeader(),
      },
    });
    return handleResponse(response);
  },
  
  logout: async () => {
    const response = await fetch(`${API_BASE_URL}/auth/logout`, {
      method: 'POST',
      headers: {
        ...getAuthHeader(),
      },
    });
    return handleResponse(response);
  },
};

// Organizations API
export const organizationsApi = {
  getOrganizations: async () => {
    const response = await fetch(`${API_BASE_URL}/organizations`, {
      headers: {
        ...getAuthHeader(),
      },
    });
    return handleResponse(response);
  },
  
  getOrganization: async (id) => {
    const response = await fetch(`${API_BASE_URL}/organizations/${id}`, {
      headers: {
        ...getAuthHeader(),
      },
    });
    return handleResponse(response);
  },
  
  createOrganization: async (data) => {
    const response = await fetch(`${API_BASE_URL}/organizations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader(),
      },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },
};

// Documents API
export const documentsApi = {
  getOrganizationDocuments: async (organizationId, params = {}) => {
    const queryParams = new URLSearchParams(params).toString();
    const url = `${API_BASE_URL}/organizations/${organizationId}/documents${queryParams ? `?${queryParams}` : ''}`;
    
    const response = await fetch(url, {
      headers: {
        ...getAuthHeader(),
      },
    });
    return handleResponse(response);
  },
  
  uploadDocument: async (organizationId, formData) => {
    const response = await fetch(`${API_BASE_URL}/organizations/${organizationId}/documents`, {
      method: 'POST',
      headers: {
        ...getAuthHeader(),
      },
      body: formData,
    });
    return handleResponse(response);
  },
  
  getDocument: async (documentId) => {
    const response = await fetch(`${API_BASE_URL}/documents/${documentId}`, {
      headers: {
        ...getAuthHeader(),
      },
    });
    return handleResponse(response);
  },
  
  getDocumentContent: async (documentId) => {
    const response = await fetch(`${API_BASE_URL}/documents/${documentId}/content`, {
      headers: {
        ...getAuthHeader(),
      },
    });
    return response; // Return the response directly for blob handling
  },
  
  updateDocument: async (documentId, formData) => {
    const response = await fetch(`${API_BASE_URL}/documents/${documentId}`, {
      method: 'PUT',
      headers: {
        ...getAuthHeader(),
      },
      body: formData,
    });
    return handleResponse(response);
  },
  
  deleteDocument: async (documentId) => {
    const response = await fetch(`${API_BASE_URL}/documents/${documentId}`, {
      method: 'DELETE',
      headers: {
        ...getAuthHeader(),
      },
    });
    return handleResponse(response);
  },
  
  shareDocument: async (documentId, data) => {
    const response = await fetch(`${API_BASE_URL}/documents/${documentId}/share`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader(),
      },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },
  
  getSharedDocuments: async () => {
    const response = await fetch(`${API_BASE_URL}/users/me/shared-documents`, {
      headers: {
        ...getAuthHeader(),
      },
    });
    return handleResponse(response);
  },
};

// AI API
export const aiApi = {
  analyzeDocument: async (documentId) => {
    const response = await fetch(`${API_BASE_URL}/ai/documents/${documentId}/analyze`, {
      method: 'POST',
      headers: {
        ...getAuthHeader(),
      },
    });
    return handleResponse(response);
  },
  
  getDocumentClauses: async (documentId, params = {}) => {
    const queryParams = new URLSearchParams(params).toString();
    const url = `${API_BASE_URL}/ai/documents/${documentId}/clauses${queryParams ? `?${queryParams}` : ''}`;
    
    const response = await fetch(url, {
      headers: {
        ...getAuthHeader(),
      },
    });
    return handleResponse(response);
  },
  
  getDocumentSummary: async (documentId) => {
    const response = await fetch(`${API_BASE_URL}/ai/documents/${documentId}/summary`, {
      headers: {
        ...getAuthHeader(),
      },
    });
    return handleResponse(response);
  },
  
  getDocumentObligations: async (documentId) => {
    const response = await fetch(`${API_BASE_URL}/ai/documents/${documentId}/obligations`, {
      headers: {
        ...getAuthHeader(),
      },
    });
    return handleResponse(response);
  },
  
  searchDocument: async (documentId, query) => {
    const response = await fetch(`${API_BASE_URL}/ai/documents/${documentId}/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader(),
      },
      body: JSON.stringify({ query }),
    });
    return handleResponse(response);
  },
  
  getSearchHistory: async (documentId) => {
    const response = await fetch(`${API_BASE_URL}/ai/documents/${documentId}/search-history`, {
      headers: {
        ...getAuthHeader(),
      },
    });
    return handleResponse(response);
  },
};

// Billing API
export const billingApi = {
  getPlans: async () => {
    const response = await fetch(`${API_BASE_URL}/billing/plans`, {
      headers: {
        ...getAuthHeader(),
      },
    });
    return handleResponse(response);
  },
  
  createSubscription: async (data) => {
    const response = await fetch(`${API_BASE_URL}/billing/create-subscription`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader(),
      },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },
  
  cancelSubscription: async () => {
    const response = await fetch(`${API_BASE_URL}/billing/cancel-subscription`, {
      method: 'POST',
      headers: {
        ...getAuthHeader(),
      },
    });
    return handleResponse(response);
  },
  
  updateSubscription: async (data) => {
    const response = await fetch(`${API_BASE_URL}/billing/update-subscription`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader(),
      },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },
};

