import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  FileText, 
  Search, 
  Filter, 
  Plus, 
  Upload,
  ArrowUpDown,
  MoreHorizontal,
  Trash,
  Share,
  Download
} from 'lucide-react';
import { useOrganization } from '@/contexts/OrganizationContext';
import { documentsApi } from '@/lib/api';
import { formatDate, formatFileSize, truncateText } from '@/lib/utils';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Label } from '@/components/ui/label';

export default function Documents() {
  const { currentOrganization } = useOrganization();
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadError, setUploadError] = useState('');
  const [uploadForm, setUploadForm] = useState({
    title: '',
    file: null,
  });

  useEffect(() => {
    const fetchDocuments = async () => {
      if (!currentOrganization) {
        setLoading(false);
        return;
      }

      try {
        // In a real implementation, we would fetch actual data
        // const response = await documentsApi.getOrganizationDocuments(currentOrganization.id);
        // setDocuments(response.documents);
        
        // For the MVP, we'll use mock data
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        setDocuments([
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
          {
            id: 4,
            title: 'Non-Disclosure Agreement',
            status: 'analyzed',
            created_at: '2023-08-10T11:20:00Z',
            updated_at: '2023-08-10T14:30:00Z',
            file_type: 'pdf',
            file_size: 750000,
            risk_level: 'high',
          },
          {
            id: 5,
            title: 'Software License Agreement',
            status: 'error',
            created_at: '2023-08-05T09:15:00Z',
            updated_at: '2023-08-05T09:45:00Z',
            file_type: 'docx',
            file_size: 1100000,
            risk_level: null,
          },
        ]);
      } catch (error) {
        console.error('Error fetching documents:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDocuments();
  }, [currentOrganization]);

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
  };

  const handleStatusFilterChange = (value) => {
    setStatusFilter(value);
  };

  const handleSortChange = (column) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder('asc');
    }
  };

  const handleUploadFormChange = (e) => {
    const { name, value, files } = e.target;
    
    if (name === 'file' && files.length > 0) {
      setUploadForm({
        ...uploadForm,
        file: files[0],
        title: files[0].name.split('.')[0], // Set title to filename by default
      });
    } else {
      setUploadForm({
        ...uploadForm,
        [name]: value,
      });
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    
    if (!uploadForm.file || !uploadForm.title) {
      setUploadError('Please provide a title and select a file');
      return;
    }

    setUploading(true);
    setUploadError('');
    
    try {
      // Simulate upload progress
      const interval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 95) {
            clearInterval(interval);
            return 95;
          }
          return prev + 5;
        });
      }, 200);

      // In a real implementation, we would upload the file
      // const formData = new FormData();
      // formData.append('file', uploadForm.file);
      // formData.append('title', uploadForm.title);
      // await documentsApi.uploadDocument(currentOrganization.id, formData);
      
      // For the MVP, we'll simulate a successful upload
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setUploadProgress(100);
      
      // Add the new document to the list
      const newDocument = {
        id: documents.length + 1,
        title: uploadForm.title,
        status: 'queued',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        file_type: uploadForm.file.name.split('.').pop().toLowerCase(),
        file_size: uploadForm.file.size,
        risk_level: null,
      };
      
      setDocuments([newDocument, ...documents]);
      
      // Reset form and close dialog
      setUploadForm({ title: '', file: null });
      setUploadDialogOpen(false);
    } catch (error) {
      console.error('Error uploading document:', error);
      setUploadError('Failed to upload document. Please try again.');
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'analyzed':
        return <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">Analyzed</Badge>;
      case 'processing':
        return <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">Processing</Badge>;
      case 'queued':
        return <Badge variant="outline" className="bg-yellow-50 text-yellow-700 border-yellow-200">Queued</Badge>;
      case 'error':
        return <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200">Error</Badge>;
      default:
        return <Badge variant="outline">Pending</Badge>;
    }
  };

  const getRiskBadge = (risk) => {
    if (!risk) return '-';
    
    switch (risk) {
      case 'high':
        return <Badge className="bg-red-100 text-red-800 hover:bg-red-100">High Risk</Badge>;
      case 'medium':
        return <Badge className="bg-yellow-100 text-yellow-800 hover:bg-yellow-100">Medium Risk</Badge>;
      case 'low':
        return <Badge className="bg-green-100 text-green-800 hover:bg-green-100">Low Risk</Badge>;
      default:
        return '-';
    }
  };

  // Filter and sort documents
  const filteredDocuments = documents.filter((doc) => {
    const matchesSearch = doc.title.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || doc.status === statusFilter;
    return matchesSearch && matchesStatus;
  }).sort((a, b) => {
    if (sortOrder === 'asc') {
      return a[sortBy] > b[sortBy] ? 1 : -1;
    } else {
      return a[sortBy] < b[sortBy] ? 1 : -1;
    }
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Documents</h1>
          <p className="text-muted-foreground">
            Manage and analyze your contracts and legal documents
          </p>
        </div>
        <div className="mt-4 md:mt-0">
          <Dialog open={uploadDialogOpen} onOpenChange={setUploadDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Upload className="mr-2 h-4 w-4" />
                Upload Document
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Upload Document</DialogTitle>
                <DialogDescription>
                  Upload a contract or legal document for AI analysis
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleUpload}>
                <div className="space-y-4 py-4">
                  {uploadError && (
                    <div className="text-sm font-medium text-destructive">
                      {uploadError}
                    </div>
                  )}
                  <div className="space-y-2">
                    <Label htmlFor="title">Document Title</Label>
                    <Input
                      id="title"
                      name="title"
                      value={uploadForm.title}
                      onChange={handleUploadFormChange}
                      placeholder="Enter document title"
                      disabled={uploading}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="file">File</Label>
                    <div className="flex items-center gap-2">
                      <Input
                        id="file"
                        name="file"
                        type="file"
                        accept=".pdf,.docx,.txt"
                        onChange={handleUploadFormChange}
                        disabled={uploading}
                      />
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Supported formats: PDF, DOCX, TXT (Max 16MB)
                    </p>
                  </div>
                  {uploading && (
                    <div className="space-y-2">
                      <div className="text-sm">Uploading: {uploadProgress}%</div>
                      <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
                        <div
                          className="h-full bg-primary"
                          style={{ width: `${uploadProgress}%` }}
                        />
                      </div>
                    </div>
                  )}
                </div>
                <DialogFooter>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setUploadDialogOpen(false)}
                    disabled={uploading}
                  >
                    Cancel
                  </Button>
                  <Button type="submit" disabled={uploading}>
                    {uploading ? 'Uploading...' : 'Upload'}
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Search and filters */}
      <div className="flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Search documents..."
            className="pl-8"
            value={searchQuery}
            onChange={handleSearchChange}
          />
        </div>
        <Select value={statusFilter} onValueChange={handleStatusFilterChange}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Statuses</SelectItem>
            <SelectItem value="analyzed">Analyzed</SelectItem>
            <SelectItem value="processing">Processing</SelectItem>
            <SelectItem value="queued">Queued</SelectItem>
            <SelectItem value="error">Error</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Documents table */}
      <div className="border rounded-md">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[300px]">
                <Button
                  variant="ghost"
                  className="p-0 font-medium"
                  onClick={() => handleSortChange('title')}
                >
                  Document
                  {sortBy === 'title' && (
                    <ArrowUpDown className="ml-2 h-4 w-4 inline" />
                  )}
                </Button>
              </TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Risk</TableHead>
              <TableHead>
                <Button
                  variant="ghost"
                  className="p-0 font-medium"
                  onClick={() => handleSortChange('created_at')}
                >
                  Date
                  {sortBy === 'created_at' && (
                    <ArrowUpDown className="ml-2 h-4 w-4 inline" />
                  )}
                </Button>
              </TableHead>
              <TableHead>Size</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              Array(5)
                .fill(0)
                .map((_, i) => (
                  <TableRow key={i}>
                    <TableCell>
                      <Skeleton className="h-6 w-[250px]" />
                    </TableCell>
                    <TableCell>
                      <Skeleton className="h-6 w-[100px]" />
                    </TableCell>
                    <TableCell>
                      <Skeleton className="h-6 w-[80px]" />
                    </TableCell>
                    <TableCell>
                      <Skeleton className="h-6 w-[100px]" />
                    </TableCell>
                    <TableCell>
                      <Skeleton className="h-6 w-[60px]" />
                    </TableCell>
                    <TableCell className="text-right">
                      <Skeleton className="h-8 w-8 rounded-full ml-auto" />
                    </TableCell>
                  </TableRow>
                ))
            ) : filteredDocuments.length > 0 ? (
              filteredDocuments.map((doc) => (
                <TableRow key={doc.id}>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <div className="flex h-8 w-8 items-center justify-center rounded-md bg-muted">
                        <FileText className="h-4 w-4" />
                      </div>
                      <Link
                        to={`/documents/${doc.id}`}
                        className="font-medium hover:underline"
                      >
                        {truncateText(doc.title, 40)}
                      </Link>
                    </div>
                  </TableCell>
                  <TableCell>{getStatusBadge(doc.status)}</TableCell>
                  <TableCell>{getRiskBadge(doc.risk_level)}</TableCell>
                  <TableCell>{formatDate(doc.created_at)}</TableCell>
                  <TableCell>{formatFileSize(doc.file_size)}</TableCell>
                  <TableCell className="text-right">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon">
                          <MoreHorizontal className="h-4 w-4" />
                          <span className="sr-only">Actions</span>
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuLabel>Actions</DropdownMenuLabel>
                        <DropdownMenuItem asChild>
                          <Link to={`/documents/${doc.id}`}>View Details</Link>
                        </DropdownMenuItem>
                        <DropdownMenuItem>
                          <Download className="mr-2 h-4 w-4" />
                          Download
                        </DropdownMenuItem>
                        <DropdownMenuItem>
                          <Share className="mr-2 h-4 w-4" />
                          Share
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem className="text-destructive">
                          <Trash className="mr-2 h-4 w-4" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={6} className="text-center py-8">
                  <div className="flex flex-col items-center justify-center">
                    <FileText className="h-12 w-12 text-muted-foreground mb-4" />
                    <p className="text-muted-foreground">
                      No documents found. Upload your first document to get started.
                    </p>
                    <Button
                      className="mt-4"
                      onClick={() => setUploadDialogOpen(true)}
                    >
                      <Plus className="mr-2 h-4 w-4" />
                      Upload Document
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}

