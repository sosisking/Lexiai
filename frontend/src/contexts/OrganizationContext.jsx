import { createContext, useContext, useState, useEffect } from 'react';
import { organizationsApi } from '@/lib/api';
import { useAuth } from './AuthContext';

// Create the organization context
const OrganizationContext = createContext();

// Organization provider component
export function OrganizationProvider({ children }) {
  const { isAuthenticated } = useAuth();
  const [organizations, setOrganizations] = useState([]);
  const [currentOrganization, setCurrentOrganization] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch organizations when authenticated
  useEffect(() => {
    const fetchOrganizations = async () => {
      if (!isAuthenticated) {
        setOrganizations([]);
        setCurrentOrganization(null);
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);
      try {
        const response = await organizationsApi.getOrganizations();
        setOrganizations(response.organizations || []);
        
        // Set current organization to the first one if available
        if (response.organizations && response.organizations.length > 0) {
          const storedOrgId = localStorage.getItem('currentOrganizationId');
          const org = storedOrgId 
            ? response.organizations.find(o => o.id === parseInt(storedOrgId))
            : response.organizations[0];
            
          setCurrentOrganization(org || response.organizations[0]);
        }
      } catch (err) {
        setError(err.message);
        console.error('Error fetching organizations:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchOrganizations();
  }, [isAuthenticated]);

  // Create a new organization
  const createOrganization = async (data) => {
    setLoading(true);
    setError(null);
    try {
      const response = await organizationsApi.createOrganization(data);
      setOrganizations([...organizations, response.organization]);
      return response.organization;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Switch current organization
  const switchOrganization = (organizationId) => {
    const organization = organizations.find(org => org.id === organizationId);
    if (organization) {
      setCurrentOrganization(organization);
      localStorage.setItem('currentOrganizationId', organizationId);
    }
  };

  // Context value
  const value = {
    organizations,
    currentOrganization,
    loading,
    error,
    createOrganization,
    switchOrganization,
  };

  return <OrganizationContext.Provider value={value}>{children}</OrganizationContext.Provider>;
}

// Custom hook to use the organization context
export const useOrganization = () => {
  const context = useContext(OrganizationContext);
  if (!context) {
    throw new Error('useOrganization must be used within an OrganizationProvider');
  }
  return context;
};

