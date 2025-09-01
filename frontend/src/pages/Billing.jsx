import { useState, useEffect } from 'react';
import { 
  CreditCard, 
  CheckCircle, 
  Calendar, 
  Users, 
  FileText,
  Download,
  AlertCircle,
  ChevronRight
} from 'lucide-react';
import { useOrganization } from '@/contexts/OrganizationContext';
import { billingApi } from '@/lib/api';
import { formatDate, formatCurrency } from '@/lib/utils';

import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
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
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export default function Billing() {
  const { currentOrganization } = useOrganization();
  const [subscription, setSubscription] = useState(null);
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [cancelDialogOpen, setCancelDialogOpen] = useState(false);
  const [cancelling, setCancelling] = useState(false);
  const [upgradeDialogOpen, setUpgradeDialogOpen] = useState(false);
  const [upgrading, setUpgrading] = useState(false);

  useEffect(() => {
    const fetchBillingData = async () => {
      if (!currentOrganization) {
        setLoading(false);
        return;
      }

      try {
        // In a real implementation, we would fetch actual data
        // const subscriptionData = await billingApi.getSubscription(currentOrganization.id);
        // const invoicesData = await billingApi.getInvoices(currentOrganization.id);
        // setSubscription(subscriptionData);
        // setInvoices(invoicesData.invoices);
        
        // For the MVP, we'll use mock data
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        setSubscription({
          id: 'sub_123456',
          status: 'active',
          plan: 'standard',
          price_per_user: 100,
          billing_cycle: 'monthly',
          current_period_start: '2023-08-01T00:00:00Z',
          current_period_end: '2023-09-01T00:00:00Z',
          seats: 5,
          seats_used: 4,
          payment_method: {
            brand: 'visa',
            last4: '4242',
            exp_month: 12,
            exp_year: 2024
          }
        });
        
        setInvoices([
          {
            id: 'inv_123456',
            amount: 500,
            status: 'paid',
            date: '2023-08-01T00:00:00Z',
            pdf_url: '#'
          },
          {
            id: 'inv_123455',
            amount: 500,
            status: 'paid',
            date: '2023-07-01T00:00:00Z',
            pdf_url: '#'
          },
          {
            id: 'inv_123454',
            amount: 400,
            status: 'paid',
            date: '2023-06-01T00:00:00Z',
            pdf_url: '#'
          }
        ]);
      } catch (error) {
        console.error('Error fetching billing data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchBillingData();
  }, [currentOrganization]);

  const handleCancelSubscription = async () => {
    setCancelling(true);
    
    try {
      // In a real implementation, we would call the API
      // await billingApi.cancelSubscription(currentOrganization.id);
      
      // For the MVP, we'll simulate cancellation
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSubscription({
        ...subscription,
        status: 'canceled',
        cancel_at_period_end: true
      });
      
      setCancelDialogOpen(false);
    } catch (error) {
      console.error('Error cancelling subscription:', error);
    } finally {
      setCancelling(false);
    }
  };

  const handleUpgradeSubscription = async () => {
    setUpgrading(true);
    
    try {
      // In a real implementation, we would call the API
      // await billingApi.upgradeSubscription(currentOrganization.id, {
      //   plan: 'premium'
      // });
      
      // For the MVP, we'll simulate upgrading
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSubscription({
        ...subscription,
        plan: 'premium',
        price_per_user: 200
      });
      
      setUpgradeDialogOpen(false);
    } catch (error) {
      console.error('Error upgrading subscription:', error);
    } finally {
      setUpgrading(false);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'active':
        return <Badge className="bg-green-100 text-green-800 hover:bg-green-100">Active</Badge>;
      case 'canceled':
        return <Badge className="bg-yellow-100 text-yellow-800 hover:bg-yellow-100">Canceled</Badge>;
      case 'past_due':
        return <Badge className="bg-red-100 text-red-800 hover:bg-red-100">Past Due</Badge>;
      default:
        return <Badge>{status}</Badge>;
    }
  };

  const getInvoiceStatusBadge = (status) => {
    switch (status) {
      case 'paid':
        return <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">Paid</Badge>;
      case 'open':
        return <Badge variant="outline" className="bg-yellow-50 text-yellow-700 border-yellow-200">Open</Badge>;
      case 'failed':
        return <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200">Failed</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Billing</h1>
        <p className="text-muted-foreground">
          Manage your subscription and billing information
        </p>
      </div>

      <Tabs defaultValue="subscription">
        <TabsList>
          <TabsTrigger value="subscription">Subscription</TabsTrigger>
          <TabsTrigger value="invoices">Invoices</TabsTrigger>
        </TabsList>
        
        {/* Subscription Tab */}
        <TabsContent value="subscription" className="space-y-6">
          {/* Current Plan */}
          <Card>
            <CardHeader>
              <CardTitle>Current Plan</CardTitle>
              <CardDescription>
                Your current subscription plan and details
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-4">
                  <Skeleton className="h-6 w-[200px]" />
                  <Skeleton className="h-4 w-[300px]" />
                  <Skeleton className="h-4 w-[250px]" />
                  <Skeleton className="h-4 w-[200px]" />
                </div>
              ) : subscription ? (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-medium capitalize">
                        {subscription.plan} Plan
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        {formatCurrency(subscription.price_per_user)} per user / month
                      </p>
                    </div>
                    <div>
                      {getStatusBadge(subscription.status)}
                    </div>
                  </div>
                  
                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    <div className="flex items-center gap-2">
                      <Calendar className="h-5 w-5 text-muted-foreground" />
                      <div>
                        <p className="text-sm font-medium">Current Period</p>
                        <p className="text-sm text-muted-foreground">
                          {formatDate(subscription.current_period_start)} - {formatDate(subscription.current_period_end)}
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <Users className="h-5 w-5 text-muted-foreground" />
                      <div>
                        <p className="text-sm font-medium">Team Members</p>
                        <p className="text-sm text-muted-foreground">
                          {subscription.seats_used} of {subscription.seats} seats used
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <CreditCard className="h-5 w-5 text-muted-foreground" />
                      <div>
                        <p className="text-sm font-medium">Payment Method</p>
                        <p className="text-sm text-muted-foreground">
                          {subscription.payment_method.brand.toUpperCase()} ending in {subscription.payment_method.last4}
                        </p>
                      </div>
                    </div>
                  </div>
                  
                  {subscription.status === 'canceled' && (
                    <Alert>
                      <AlertCircle className="h-4 w-4" />
                      <AlertTitle>Subscription Canceled</AlertTitle>
                      <AlertDescription>
                        Your subscription will end on {formatDate(subscription.current_period_end)}. You can reactivate your subscription at any time before this date.
                      </AlertDescription>
                    </Alert>
                  )}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-6">
                  <AlertCircle className="h-12 w-12 text-muted-foreground mb-4" />
                  <p className="text-muted-foreground text-center">
                    No active subscription found. Subscribe to get started.
                  </p>
                  <Button className="mt-4">Subscribe Now</Button>
                </div>
              )}
            </CardContent>
            {subscription && subscription.status === 'active' && (
              <CardFooter className="flex justify-between">
                <Dialog open={cancelDialogOpen} onOpenChange={setCancelDialogOpen}>
                  <DialogTrigger asChild>
                    <Button variant="outline">Cancel Subscription</Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Cancel Subscription</DialogTitle>
                      <DialogDescription>
                        Are you sure you want to cancel your subscription?
                      </DialogDescription>
                    </DialogHeader>
                    <div className="py-4">
                      <p className="text-sm text-muted-foreground">
                        Your subscription will remain active until the end of your current billing period on {formatDate(subscription.current_period_end)}. After this date, you will lose access to premium features.
                      </p>
                    </div>
                    <DialogFooter>
                      <Button
                        variant="outline"
                        onClick={() => setCancelDialogOpen(false)}
                        disabled={cancelling}
                      >
                        Keep Subscription
                      </Button>
                      <Button
                        variant="destructive"
                        onClick={handleCancelSubscription}
                        disabled={cancelling}
                      >
                        {cancelling ? 'Cancelling...' : 'Cancel Subscription'}
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
                
                <Dialog open={upgradeDialogOpen} onOpenChange={setUpgradeDialogOpen}>
                  <DialogTrigger asChild>
                    <Button>Upgrade Plan</Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Upgrade to Premium</DialogTitle>
                      <DialogDescription>
                        Upgrade to our premium plan for additional features
                      </DialogDescription>
                    </DialogHeader>
                    <div className="py-4 space-y-4">
                      <div className="flex items-center gap-2">
                        <CheckCircle className="h-5 w-5 text-green-500" />
                        <p className="text-sm">Unlimited document storage</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <CheckCircle className="h-5 w-5 text-green-500" />
                        <p className="text-sm">Advanced AI analysis features</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <CheckCircle className="h-5 w-5 text-green-500" />
                        <p className="text-sm">Priority support</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <CheckCircle className="h-5 w-5 text-green-500" />
                        <p className="text-sm">Custom clause templates</p>
                      </div>
                      
                      <div className="pt-4">
                        <p className="text-sm font-medium">
                          Price: {formatCurrency(200)} per user / month
                        </p>
                      </div>
                    </div>
                    <DialogFooter>
                      <Button
                        variant="outline"
                        onClick={() => setUpgradeDialogOpen(false)}
                        disabled={upgrading}
                      >
                        Cancel
                      </Button>
                      <Button
                        onClick={handleUpgradeSubscription}
                        disabled={upgrading}
                      >
                        {upgrading ? 'Upgrading...' : 'Upgrade Now'}
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </CardFooter>
            )}
          </Card>
          
          {/* Plan Comparison */}
          <Card>
            <CardHeader>
              <CardTitle>Plan Comparison</CardTitle>
              <CardDescription>
                Compare our available plans
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="border rounded-md">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-[200px]">Feature</TableHead>
                      <TableHead>Standard</TableHead>
                      <TableHead>Premium</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <TableRow>
                      <TableCell className="font-medium">Price</TableCell>
                      <TableCell>{formatCurrency(100)}/user/month</TableCell>
                      <TableCell>{formatCurrency(200)}/user/month</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell className="font-medium">Document Storage</TableCell>
                      <TableCell>100 documents</TableCell>
                      <TableCell>Unlimited</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell className="font-medium">AI Analysis</TableCell>
                      <TableCell>Basic</TableCell>
                      <TableCell>Advanced</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell className="font-medium">Team Members</TableCell>
                      <TableCell>Up to 10</TableCell>
                      <TableCell>Unlimited</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell className="font-medium">Support</TableCell>
                      <TableCell>Email</TableCell>
                      <TableCell>Priority</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell className="font-medium">Custom Templates</TableCell>
                      <TableCell>
                        <AlertCircle className="h-4 w-4 text-muted-foreground" />
                      </TableCell>
                      <TableCell>
                        <CheckCircle className="h-4 w-4 text-green-500" />
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        {/* Invoices Tab */}
        <TabsContent value="invoices" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Billing History</CardTitle>
              <CardDescription>
                View and download your past invoices
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="border rounded-md">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Invoice</TableHead>
                      <TableHead>Date</TableHead>
                      <TableHead>Amount</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {loading ? (
                      Array(3)
                        .fill(0)
                        .map((_, i) => (
                          <TableRow key={i}>
                            <TableCell>
                              <Skeleton className="h-4 w-[100px]" />
                            </TableCell>
                            <TableCell>
                              <Skeleton className="h-4 w-[100px]" />
                            </TableCell>
                            <TableCell>
                              <Skeleton className="h-4 w-[80px]" />
                            </TableCell>
                            <TableCell>
                              <Skeleton className="h-6 w-16" />
                            </TableCell>
                            <TableCell className="text-right">
                              <Skeleton className="h-8 w-8 rounded-full ml-auto" />
                            </TableCell>
                          </TableRow>
                        ))
                    ) : invoices.length > 0 ? (
                      invoices.map((invoice) => (
                        <TableRow key={invoice.id}>
                          <TableCell className="font-medium">
                            {invoice.id}
                          </TableCell>
                          <TableCell>{formatDate(invoice.date)}</TableCell>
                          <TableCell>{formatCurrency(invoice.amount)}</TableCell>
                          <TableCell>{getInvoiceStatusBadge(invoice.status)}</TableCell>
                          <TableCell className="text-right">
                            <Button variant="ghost" size="sm" asChild>
                              <a href={invoice.pdf_url} target="_blank" rel="noopener noreferrer">
                                <Download className="h-4 w-4 mr-1" />
                                PDF
                              </a>
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))
                    ) : (
                      <TableRow>
                        <TableCell colSpan={5} className="text-center py-8">
                          <div className="flex flex-col items-center justify-center">
                            <FileText className="h-12 w-12 text-muted-foreground mb-4" />
                            <p className="text-muted-foreground">
                              No invoices found.
                            </p>
                          </div>
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

