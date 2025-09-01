import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  FileText, 
  Users, 
  Clock, 
  AlertTriangle,
  Calendar,
  ArrowRight,
  Plus
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useOrganization } from '@/contexts/OrganizationContext';
import { documentsApi } from '@/lib/api';
import { formatDate, truncateText } from '@/lib/utils';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';

export default function Dashboard() {
  const { user } = useAuth();
  const { currentOrganization } = useOrganization();
  const [recentDocuments, setRecentDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalDocuments: 0,
    analyzedDocuments: 0,
    pendingDocuments: 0,
    highRiskClauses: 0,
  });

  useEffect(() => {
    const fetchDashboardData = async () => {
      if (!currentOrganization) {
        setLoading(false);
        return;
      }

      try {
        // In a real implementation, we would fetch actual data
        // const response = await documentsApi.getOrganizationDocuments(currentOrganization.id, { limit: 5 });
        // setRecentDocuments(response.documents);
        
        // For the MVP, we'll use mock data
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        setRecentDocuments([
          {
            id: 1,
            title: 'Service Agreement with Acme Corp',
            status: 'analyzed',
            created_at: '2023-08-20T14:30:00Z',
            updated_at: '2023-08-21T10:15:00Z',
            file_type: 'pdf',
            file_size: 1250000,
            risk_level: 'medium',
          },
          {
            id: 2,
            title: 'Employment Contract - Senior Developer',
            status: 'analyzed',
            created_at: '2023-08-18T09:45:00Z',
            updated_at: '2023-08-18T14:20:00Z',
            file_type: 'docx',
            file_size: 890000,
            risk_level: 'low',
          },
          {
            id: 3,
            title: 'Office Lease Agreement',
            status: 'processing',
            created_at: '2023-08-15T16:10:00Z',
            updated_at: '2023-08-15T16:10:00Z',
            file_type: 'pdf',
            file_size: 2450000,
            risk_level: null,
          },
        ]);
        
        setStats({
          totalDocuments: 12,
          analyzedDocuments: 9,
          pendingDocuments: 3,
          highRiskClauses: 7,
        });
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [currentOrganization]);

  const getStatusBadge = (status) => {
    switch (status) {
      case 'analyzed':
        return <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">Analyzed</Badge>;
      case 'processing':
        return <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">Processing</Badge>;
      case 'error':
        return <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200">Error</Badge>;
      default:
        return <Badge variant="outline">Pending</Badge>;
    }
  };

  const getRiskBadge = (risk) => {
    if (!risk) return null;
    
    switch (risk) {
      case 'high':
        return <Badge className="bg-red-100 text-red-800 hover:bg-red-100">High Risk</Badge>;
      case 'medium':
        return <Badge className="bg-yellow-100 text-yellow-800 hover:bg-yellow-100">Medium Risk</Badge>;
      case 'low':
        return <Badge className="bg-green-100 text-green-800 hover:bg-green-100">Low Risk</Badge>;
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome back, {user?.full_name || 'User'}
          </p>
        </div>
        <div className="mt-4 md:mt-0">
          <Button asChild>
            <Link to="/documents">
              <Plus className="mr-2 h-4 w-4" />
              Upload Document
            </Link>
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Documents</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton className="h-7 w-16" />
            ) : (
              <div className="text-2xl font-bold">{stats.totalDocuments}</div>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Analyzed Documents</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton className="h-7 w-16" />
            ) : (
              <div className="text-2xl font-bold">{stats.analyzedDocuments}</div>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Pending Documents</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton className="h-7 w-16" />
            ) : (
              <div className="text-2xl font-bold">{stats.pendingDocuments}</div>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">High Risk Clauses</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton className="h-7 w-16" />
            ) : (
              <div className="text-2xl font-bold">{stats.highRiskClauses}</div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Recent Documents */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Documents</CardTitle>
          <CardDescription>
            Recently uploaded and analyzed documents
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="flex items-center space-x-4">
                  <Skeleton className="h-12 w-12 rounded" />
                  <div className="space-y-2">
                    <Skeleton className="h-4 w-[250px]" />
                    <Skeleton className="h-4 w-[200px]" />
                  </div>
                </div>
              ))}
            </div>
          ) : recentDocuments.length > 0 ? (
            <div className="space-y-4">
              {recentDocuments.map((doc) => (
                <div key={doc.id} className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="flex h-12 w-12 items-center justify-center rounded-md bg-muted">
                      <FileText className="h-6 w-6" />
                    </div>
                    <div>
                      <p className="text-sm font-medium leading-none">
                        {truncateText(doc.title, 50)}
                      </p>
                      <div className="flex items-center pt-1 space-x-2">
                        {getStatusBadge(doc.status)}
                        {getRiskBadge(doc.risk_level)}
                        <span className="text-xs text-muted-foreground">
                          {formatDate(doc.created_at)}
                        </span>
                      </div>
                    </div>
                  </div>
                  <Button variant="ghost" size="sm" asChild>
                    <Link to={`/documents/${doc.id}`}>
                      View
                      <ArrowRight className="ml-1 h-4 w-4" />
                    </Link>
                  </Button>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-8">
              <FileText className="h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-muted-foreground text-center">
                No documents found. Upload your first document to get started.
              </p>
              <Button className="mt-4" asChild>
                <Link to="/documents">
                  <Plus className="mr-2 h-4 w-4" />
                  Upload Document
                </Link>
              </Button>
            </div>
          )}
        </CardContent>
        <CardFooter>
          <Button variant="outline" className="w-full" asChild>
            <Link to="/documents">View all documents</Link>
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}

