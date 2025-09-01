import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  FileText, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Download, 
  Share, 
  MessageSquare, 
  Calendar,
  Search,
  ChevronRight,
  ChevronDown,
  X,
  Send,
  Plus
} from 'lucide-react';
import { documentsApi, aiApi } from '@/lib/api';
import { formatDate, formatDateTime, truncateText } from '@/lib/utils';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { useAuth } from '@/contexts/AuthContext';
import { getInitials } from '@/lib/utils';

export default function DocumentDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const [document, setDocument] = useState(null);
  const [loading, setLoading] = useState(true);
  const [clauses, setClauses] = useState([]);
  const [summary, setSummary] = useState(null);
  const [obligations, setObligations] = useState([]);
  const [comments, setComments] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [searching, setSearching] = useState(false);
  const [searchHistory, setSearchHistory] = useState([]);
  const [activeTab, setActiveTab] = useState('overview');
  const [newComment, setNewComment] = useState('');
  const [addingComment, setAddingComment] = useState(false);
  const [selectedClause, setSelectedClause] = useState(null);
  const [shareDialogOpen, setShareDialogOpen] = useState(false);
  const [shareEmail, setShareEmail] = useState('');
  const [sharing, setSharing] = useState(false);

  useEffect(() => {
    const fetchDocumentData = async () => {
      setLoading(true);
      try {
        // In a real implementation, we would fetch actual data
        // const documentData = await documentsApi.getDocument(id);
        // setDocument(documentData);
        
        // For the MVP, we'll use mock data
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Mock document data
        setDocument({
          id: parseInt(id),
          title: 'Service Agreement with Acme Corp',
          status: 'analyzed',
          created_at: '2023-08-20T14:30:00Z',
          updated_at: '2023-08-21T10:15:00Z',
          file_type: 'pdf',
          file_size: 1250000,
          risk_level: 'medium',
          created_by: {
            id: 1,
            full_name: 'John Doe',
            email: 'john@example.com',
            avatar_url: null
          }
        });
        
        // Mock clauses data
        setClauses([
          {
            id: 1,
            category: { id: 1, name: 'Termination' },
            text: 'Either party may terminate this Agreement upon thirty (30) days written notice if the other party breaches any material term or condition of this Agreement and fails to cure such breach within such thirty (30) day period.',
            risk_level: 'medium',
            risk_description: 'Short termination period may not provide sufficient time to transition services.'
          },
          {
            id: 2,
            category: { id: 2, name: 'Liability' },
            text: 'In no event shall either party be liable for any indirect, incidental, special, punitive, or consequential damages, or for any loss of profits or revenue, whether incurred directly or indirectly, or any loss of data, use, goodwill, or other intangible losses, resulting from (a) your use or inability to use the service; (b) any unauthorized access to or use of our servers and/or any personal information stored therein.',
            risk_level: 'high',
            risk_description: 'Broad liability limitation may leave company exposed to significant risks.'
          },
          {
            id: 3,
            category: { id: 3, name: 'Payment' },
            text: 'Customer shall pay all fees specified in all Order Forms. Except as otherwise specified in an Order Form, (i) fees are based on Services purchased and not actual usage, (ii) payment obligations are non-cancelable and fees paid are non-refundable, and (iii) quantities purchased cannot be decreased during the relevant subscription term.',
            risk_level: 'medium',
            risk_description: 'Non-refundable payment terms may be problematic if services don\'t meet expectations.'
          },
          {
            id: 4,
            category: { id: 4, name: 'Confidentiality' },
            text: 'Each party shall maintain the confidentiality of all Confidential Information received from the other party and shall not disclose such Confidential Information to any third party without the prior written consent of the disclosing party.',
            risk_level: 'low',
            risk_description: 'Standard confidentiality clause with reasonable protections.'
          },
          {
            id: 5,
            category: { id: 5, name: 'Intellectual Property' },
            text: 'Customer shall own all rights, title and interest in and to the Customer Data. Provider shall own and retain all rights, title and interest in and to the Services, including all software, technology, and intellectual property rights therein.',
            risk_level: 'low',
            risk_description: 'Clear IP ownership provisions with standard terms.'
          }
        ]);
        
        // Mock summary data
        setSummary({
          overview: 'This is a service agreement between Acme Corp and the customer for the provision of software development services.',
          parties: ['Acme Corp (Provider)', 'Customer Inc. (Customer)'],
          key_terms: [
            'Initial term of 12 months with automatic renewal',
            'Monthly fee of $10,000 for services',
            '30-day termination notice required',
            'Confidentiality provisions for both parties'
          ],
          important_dates: [
            'Effective Date: January 1, 2023',
            'Initial Term End: December 31, 2023',
            'Payment Due: 15th of each month'
          ],
          notable_provisions: [
            'Broad liability limitations',
            'Non-refundable payment terms',
            'IP ownership split between parties'
          ]
        });
        
        // Mock obligations data
        setObligations([
          {
            id: 1,
            party: 'Customer',
            description: 'Pay monthly service fee',
            deadline: '15th of each month',
            consequence: 'Late fee of 1.5% per month on outstanding balance'
          },
          {
            id: 2,
            party: 'Provider',
            description: 'Deliver monthly service report',
            deadline: '5th of each month',
            consequence: 'Customer may withhold payment until report is delivered'
          },
          {
            id: 3,
            party: 'Customer',
            description: 'Provide necessary access and information',
            deadline: 'Within 3 business days of request',
            consequence: 'Provider not responsible for delays caused by lack of access'
          }
        ]);
        
        // Mock comments data
        setComments([
          {
            id: 1,
            user: {
              id: 1,
              full_name: 'John Doe',
              email: 'john@example.com',
              avatar_url: null
            },
            text: 'We should negotiate the liability clause to include a cap on damages.',
            created_at: '2023-08-21T15:30:00Z',
            clause_id: 2
          },
          {
            id: 2,
            user: {
              id: 2,
              full_name: 'Jane Smith',
              email: 'jane@example.com',
              avatar_url: null
            },
            text: 'The payment terms are standard for this type of agreement.',
            created_at: '2023-08-22T10:45:00Z',
            clause_id: 3
          }
        ]);
        
        // Mock search history
        setSearchHistory([
          {
            id: 1,
            query: 'What is the termination period?',
            result: {
              answer: 'The termination period is 30 days with written notice.',
              context: 'Either party may terminate this Agreement upon thirty (30) days written notice if the other party breaches any material term or condition of this Agreement and fails to cure such breach within such thirty (30) day period.',
              explanation: 'The contract specifies a 30-day termination period with written notice in case of material breach.'
            },
            created_at: '2023-08-22T14:20:00Z'
          },
          {
            id: 2,
            query: 'Who owns the intellectual property?',
            result: {
              answer: 'Customer owns Customer Data, Provider owns the Services.',
              context: 'Customer shall own all rights, title and interest in and to the Customer Data. Provider shall own and retain all rights, title and interest in and to the Services, including all software, technology, and intellectual property rights therein.',
              explanation: 'The contract divides IP ownership: customer data belongs to the customer, while the service technology belongs to the provider.'
            },
            created_at: '2023-08-22T16:05:00Z'
          }
        ]);
      } catch (error) {
        console.error('Error fetching document data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDocumentData();
  }, [id]);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    setSearching(true);
    setSearchResults(null);
    
    try {
      // In a real implementation, we would call the API
      // const result = await aiApi.searchDocument(id, searchQuery);
      // setSearchResults(result);
      
      // For the MVP, we'll simulate a search result
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const mockResult = {
        answer: 'The termination period is 30 days with written notice in case of material breach.',
        context: 'Either party may terminate this Agreement upon thirty (30) days written notice if the other party breaches any material term or condition of this Agreement and fails to cure such breach within such thirty (30) day period.',
        explanation: 'The contract specifies that either party can terminate the agreement if the other party breaches a material term and fails to fix the issue within 30 days after receiving written notice.'
      };
      
      setSearchResults(mockResult);
      
      // Add to search history
      const newSearchItem = {
        id: searchHistory.length + 1,
        query: searchQuery,
        result: mockResult,
        created_at: new Date().toISOString()
      };
      
      setSearchHistory([newSearchItem, ...searchHistory]);
    } catch (error) {
      console.error('Error searching document:', error);
    } finally {
      setSearching(false);
    }
  };

  const handleAddComment = async () => {
    if (!newComment.trim() || !selectedClause) return;
    
    setAddingComment(true);
    
    try {
      // In a real implementation, we would call the API
      // await documentsApi.addComment(id, {
      //   clause_id: selectedClause.id,
      //   text: newComment
      // });
      
      // For the MVP, we'll simulate adding a comment
      await new Promise(resolve => setTimeout(resolve, 500));
      
      const newCommentObj = {
        id: comments.length + 1,
        user: {
          id: user.id,
          full_name: user.full_name,
          email: user.email,
          avatar_url: user.avatar_url
        },
        text: newComment,
        created_at: new Date().toISOString(),
        clause_id: selectedClause.id
      };
      
      setComments([...comments, newCommentObj]);
      setNewComment('');
    } catch (error) {
      console.error('Error adding comment:', error);
    } finally {
      setAddingComment(false);
    }
  };

  const handleShare = async () => {
    if (!shareEmail.trim()) return;
    
    setSharing(true);
    
    try {
      // In a real implementation, we would call the API
      // await documentsApi.shareDocument(id, {
      //   email: shareEmail,
      //   permission: 'view'
      // });
      
      // For the MVP, we'll simulate sharing
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setShareEmail('');
      setShareDialogOpen(false);
    } catch (error) {
      console.error('Error sharing document:', error);
    } finally {
      setSharing(false);
    }
  };

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

  const getRiskIcon = (risk) => {
    switch (risk) {
      case 'high':
        return <AlertTriangle className="h-5 w-5 text-red-500" />;
      case 'medium':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      case 'low':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      default:
        return <Clock className="h-5 w-5 text-muted-foreground" />;
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <Skeleton className="h-8 w-[300px] mb-2" />
            <Skeleton className="h-4 w-[200px]" />
          </div>
          <div className="flex gap-2">
            <Skeleton className="h-10 w-24" />
            <Skeleton className="h-10 w-24" />
          </div>
        </div>
        <Skeleton className="h-[600px] w-full" />
      </div>
    );
  }

  if (!document) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <FileText className="h-16 w-16 text-muted-foreground mb-4" />
        <h2 className="text-2xl font-bold mb-2">Document Not Found</h2>
        <p className="text-muted-foreground mb-6">
          The document you're looking for doesn't exist or you don't have permission to view it.
        </p>
        <Button asChild>
          <Link to="/documents">Back to Documents</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Document header */}
      <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
        <div>
          <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
            <Link to="/documents" className="hover:underline">Documents</Link>
            <ChevronRight className="h-4 w-4" />
            <span>{truncateText(document.title, 30)}</span>
          </div>
          <h1 className="text-2xl font-bold">{document.title}</h1>
          <div className="flex flex-wrap items-center gap-2 mt-2">
            {getStatusBadge(document.status)}
            {document.risk_level && getRiskBadge(document.risk_level)}
            <span className="text-sm text-muted-foreground">
              Uploaded {formatDate(document.created_at)}
            </span>
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="outline" onClick={() => setShareDialogOpen(true)}>
            <Share className="mr-2 h-4 w-4" />
            Share
          </Button>
          <Button variant="outline">
            <Download className="mr-2 h-4 w-4" />
            Download
          </Button>
        </div>
      </div>

      {/* Main content */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid grid-cols-4 md:grid-cols-5 lg:w-[600px]">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="clauses">Clauses</TabsTrigger>
          <TabsTrigger value="obligations">Obligations</TabsTrigger>
          <TabsTrigger value="search">Search</TabsTrigger>
          <TabsTrigger value="comments" className="hidden md:block">Comments</TabsTrigger>
        </TabsList>
        
        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          {summary ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Document Summary</CardTitle>
                  <CardDescription>AI-generated summary of the contract</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm">{summary.overview}</p>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader>
                  <CardTitle>Key Parties</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {summary.parties.map((party, index) => (
                      <li key={index} className="flex items-center gap-2 text-sm">
                        <div className="h-2 w-2 rounded-full bg-primary" />
                        {party}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader>
                  <CardTitle>Key Terms</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {summary.key_terms.map((term, index) => (
                      <li key={index} className="flex items-center gap-2 text-sm">
                        <div className="h-2 w-2 rounded-full bg-primary" />
                        {term}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader>
                  <CardTitle>Important Dates</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {summary.important_dates.map((date, index) => (
                      <li key={index} className="flex items-center gap-2 text-sm">
                        <Calendar className="h-4 w-4 text-muted-foreground" />
                        {date}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
              
              <Card className="md:col-span-2">
                <CardHeader>
                  <CardTitle>Notable Provisions</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {summary.notable_provisions.map((provision, index) => (
                      <li key={index} className="flex items-center gap-2 text-sm">
                        <AlertTriangle className="h-4 w-4 text-yellow-500" />
                        {provision}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-12">
              <Clock className="h-16 w-16 text-muted-foreground mb-4" />
              <h2 className="text-xl font-bold mb-2">Analysis in Progress</h2>
              <p className="text-muted-foreground">
                The document is still being analyzed. Check back soon.
              </p>
            </div>
          )}
        </TabsContent>
        
        {/* Clauses Tab */}
        <TabsContent value="clauses" className="space-y-6">
          {clauses.length > 0 ? (
            <div className="grid grid-cols-1 gap-4">
              <Accordion type="single" collapsible className="w-full">
                {clauses.map((clause) => (
                  <AccordionItem key={clause.id} value={`clause-${clause.id}`}>
                    <AccordionTrigger className="hover:no-underline">
                      <div className="flex items-center gap-3 text-left">
                        {getRiskIcon(clause.risk_level)}
                        <div>
                          <div className="font-medium">{clause.category.name}</div>
                          <div className="text-sm text-muted-foreground">
                            {truncateText(clause.text, 60)}
                          </div>
                        </div>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent>
                      <div className="space-y-4 pt-2">
                        <div className="text-sm">{clause.text}</div>
                        
                        {clause.risk_level !== 'low' && (
                          <div className="flex items-start gap-2 p-3 bg-muted rounded-md">
                            <AlertTriangle className={`h-5 w-5 ${clause.risk_level === 'high' ? 'text-red-500' : 'text-yellow-500'}`} />
                            <div>
                              <div className="font-medium">Risk Assessment</div>
                              <div className="text-sm">{clause.risk_description}</div>
                            </div>
                          </div>
                        )}
                        
                        {/* Comments for this clause */}
                        <div className="pt-2">
                          <div className="flex items-center justify-between">
                            <h4 className="text-sm font-medium">Comments</h4>
                            <Button 
                              variant="ghost" 
                              size="sm" 
                              onClick={() => setSelectedClause(clause)}
                            >
                              <MessageSquare className="h-4 w-4 mr-1" />
                              Add Comment
                            </Button>
                          </div>
                          
                          <div className="mt-2 space-y-3">
                            {comments
                              .filter(comment => comment.clause_id === clause.id)
                              .map(comment => (
                                <div key={comment.id} className="flex gap-3">
                                  <Avatar className="h-8 w-8">
                                    <AvatarImage src={comment.user.avatar_url} alt={comment.user.full_name} />
                                    <AvatarFallback>{getInitials(comment.user.full_name)}</AvatarFallback>
                                  </Avatar>
                                  <div className="flex-1">
                                    <div className="flex items-center justify-between">
                                      <div className="font-medium text-sm">{comment.user.full_name}</div>
                                      <div className="text-xs text-muted-foreground">{formatDateTime(comment.created_at)}</div>
                                    </div>
                                    <div className="text-sm mt-1">{comment.text}</div>
                                  </div>
                                </div>
                              ))}
                            
                            {comments.filter(comment => comment.clause_id === clause.id).length === 0 && (
                              <div className="text-sm text-muted-foreground">No comments yet</div>
                            )}
                          </div>
                        </div>
                      </div>
                    </AccordionContent>
                  </AccordionItem>
                ))}
              </Accordion>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-12">
              <Clock className="h-16 w-16 text-muted-foreground mb-4" />
              <h2 className="text-xl font-bold mb-2">Analysis in Progress</h2>
              <p className="text-muted-foreground">
                The document is still being analyzed. Check back soon.
              </p>
            </div>
          )}
        </TabsContent>
        
        {/* Obligations Tab */}
        <TabsContent value="obligations" className="space-y-6">
          {obligations.length > 0 ? (
            <div className="grid grid-cols-1 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle>Key Obligations & Deadlines</CardTitle>
                  <CardDescription>
                    Important obligations extracted from the contract
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="border rounded-md">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b bg-muted/50">
                          <th className="text-left p-3 text-sm font-medium">Party</th>
                          <th className="text-left p-3 text-sm font-medium">Obligation</th>
                          <th className="text-left p-3 text-sm font-medium">Deadline</th>
                          <th className="text-left p-3 text-sm font-medium">Consequence</th>
                        </tr>
                      </thead>
                      <tbody>
                        {obligations.map((obligation) => (
                          <tr key={obligation.id} className="border-b">
                            <td className="p-3 text-sm">{obligation.party}</td>
                            <td className="p-3 text-sm">{obligation.description}</td>
                            <td className="p-3 text-sm">
                              <div className="flex items-center gap-2">
                                <Calendar className="h-4 w-4 text-muted-foreground" />
                                {obligation.deadline}
                              </div>
                            </td>
                            <td className="p-3 text-sm">{obligation.consequence}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-12">
              <Clock className="h-16 w-16 text-muted-foreground mb-4" />
              <h2 className="text-xl font-bold mb-2">Analysis in Progress</h2>
              <p className="text-muted-foreground">
                The document is still being analyzed. Check back soon.
              </p>
            </div>
          )}
        </TabsContent>
        
        {/* Search Tab */}
        <TabsContent value="search" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Ask Questions About This Document</CardTitle>
              <CardDescription>
                Use natural language to search for specific information
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2">
                <div className="flex-1">
                  <Input
                    placeholder="e.g., What is the termination period?"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                  />
                </div>
                <Button onClick={handleSearch} disabled={searching || !searchQuery.trim()}>
                  {searching ? 'Searching...' : 'Search'}
                </Button>
              </div>
              
              {/* Search Results */}
              {searchResults && (
                <div className="mt-6 space-y-4">
                  <div className="p-4 border rounded-md bg-muted/50">
                    <div className="font-medium mb-2">Answer:</div>
                    <p className="text-sm">{searchResults.answer}</p>
                    
                    <div className="mt-4">
                      <div className="font-medium mb-2">Context:</div>
                      <p className="text-sm italic bg-background p-2 rounded-md border">
                        "{searchResults.context}"
                      </p>
                    </div>
                    
                    <div className="mt-4">
                      <div className="font-medium mb-2">Explanation:</div>
                      <p className="text-sm">{searchResults.explanation}</p>
                    </div>
                  </div>
                </div>
              )}
              
              {/* Search History */}
              {searchHistory.length > 0 && (
                <div className="mt-6">
                  <h3 className="text-sm font-medium mb-3">Recent Searches</h3>
                  <div className="space-y-3">
                    {searchHistory.map((item) => (
                      <div key={item.id} className="p-3 border rounded-md">
                        <div className="flex items-center justify-between">
                          <div className="font-medium">{item.query}</div>
                          <div className="text-xs text-muted-foreground">
                            {formatDateTime(item.created_at)}
                          </div>
                        </div>
                        <p className="text-sm mt-1">{item.result.answer}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
        
        {/* Comments Tab */}
        <TabsContent value="comments" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Comments</CardTitle>
              <CardDescription>
                Collaborate with your team on this document
              </CardDescription>
            </CardHeader>
            <CardContent>
              {comments.length > 0 ? (
                <div className="space-y-4">
                  {comments.map((comment) => (
                    <div key={comment.id} className="flex gap-3 p-3 border rounded-md">
                      <Avatar className="h-8 w-8">
                        <AvatarImage src={comment.user.avatar_url} alt={comment.user.full_name} />
                        <AvatarFallback>{getInitials(comment.user.full_name)}</AvatarFallback>
                      </Avatar>
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <div className="font-medium text-sm">{comment.user.full_name}</div>
                          <div className="text-xs text-muted-foreground">{formatDateTime(comment.created_at)}</div>
                        </div>
                        <div className="text-sm mt-1">{comment.text}</div>
                        <div className="mt-2 text-xs text-muted-foreground">
                          On clause: {clauses.find(c => c.id === comment.clause_id)?.category.name || 'Unknown'}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-8">
                  <MessageSquare className="h-12 w-12 text-muted-foreground mb-4" />
                  <p className="text-muted-foreground text-center">
                    No comments yet. Add comments to specific clauses in the Clauses tab.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
      
      {/* Add Comment Dialog */}
      {selectedClause && (
        <Dialog open={!!selectedClause} onOpenChange={() => setSelectedClause(null)}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add Comment</DialogTitle>
              <DialogDescription>
                Add a comment to the {selectedClause.category.name} clause
              </DialogDescription>
            </DialogHeader>
            <div className="py-4">
              <div className="p-3 bg-muted rounded-md mb-4 text-sm">
                {truncateText(selectedClause.text, 200)}
              </div>
              <Textarea
                placeholder="Add your comment here..."
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                rows={4}
              />
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setSelectedClause(null)}>
                Cancel
              </Button>
              <Button onClick={handleAddComment} disabled={addingComment || !newComment.trim()}>
                {addingComment ? 'Adding...' : 'Add Comment'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}
      
      {/* Share Dialog */}
      <Dialog open={shareDialogOpen} onOpenChange={setShareDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Share Document</DialogTitle>
            <DialogDescription>
              Share this document with team members or clients
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <div className="space-y-4">
              <div>
                <Label htmlFor="email">Email Address</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="colleague@example.com"
                  value={shareEmail}
                  onChange={(e) => setShareEmail(e.target.value)}
                />
              </div>
              <div>
                <Label>Permission</Label>
                <Select defaultValue="view">
                  <SelectTrigger>
                    <SelectValue placeholder="Select permission" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="view">View only</SelectItem>
                    <SelectItem value="comment">Can comment</SelectItem>
                    <SelectItem value="edit">Can edit</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShareDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleShare} disabled={sharing || !shareEmail.trim()}>
              {sharing ? 'Sharing...' : 'Share'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

