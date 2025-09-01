import { useState, useEffect } from 'react';
import { 
  Users, 
  UserPlus, 
  Mail, 
  Calendar, 
  MoreHorizontal,
  Shield,
  UserCog,
  Trash,
  Search
} from 'lucide-react';
import { useOrganization } from '@/contexts/OrganizationContext';
import { formatDate, getInitials } from '@/lib/utils';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
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
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

export default function Team() {
  const { currentOrganization } = useOrganization();
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [inviteDialogOpen, setInviteDialogOpen] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState('member');
  const [inviting, setInviting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchTeamMembers = async () => {
      if (!currentOrganization) {
        setLoading(false);
        return;
      }

      try {
        // In a real implementation, we would fetch actual data
        // const response = await organizationsApi.getOrganizationMembers(currentOrganization.id);
        // setMembers(response.members);
        
        // For the MVP, we'll use mock data
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        setMembers([
          {
            id: 1,
            user: {
              id: 1,
              full_name: 'John Doe',
              email: 'john@example.com',
              avatar_url: null
            },
            role: 'owner',
            joined_at: '2023-07-15T10:30:00Z',
            status: 'active'
          },
          {
            id: 2,
            user: {
              id: 2,
              full_name: 'Jane Smith',
              email: 'jane@example.com',
              avatar_url: null
            },
            role: 'admin',
            joined_at: '2023-07-20T14:45:00Z',
            status: 'active'
          },
          {
            id: 3,
            user: {
              id: 3,
              full_name: 'Michael Johnson',
              email: 'michael@example.com',
              avatar_url: null
            },
            role: 'member',
            joined_at: '2023-08-05T09:15:00Z',
            status: 'active'
          },
          {
            id: 4,
            user: {
              id: 4,
              full_name: 'Sarah Williams',
              email: 'sarah@example.com',
              avatar_url: null
            },
            role: 'member',
            joined_at: '2023-08-10T16:20:00Z',
            status: 'pending'
          }
        ]);
      } catch (error) {
        console.error('Error fetching team members:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchTeamMembers();
  }, [currentOrganization]);

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
  };

  const handleInvite = async () => {
    if (!inviteEmail.trim()) return;
    
    setInviting(true);
    setError('');
    
    try {
      // In a real implementation, we would call the API
      // await organizationsApi.inviteMember(currentOrganization.id, {
      //   email: inviteEmail,
      //   role: inviteRole
      // });
      
      // For the MVP, we'll simulate inviting a member
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Add the new member to the list
      const newMember = {
        id: members.length + 1,
        user: {
          id: members.length + 1,
          full_name: inviteEmail.split('@')[0],
          email: inviteEmail,
          avatar_url: null
        },
        role: inviteRole,
        joined_at: new Date().toISOString(),
        status: 'pending'
      };
      
      setMembers([...members, newMember]);
      
      // Reset form and close dialog
      setInviteEmail('');
      setInviteRole('member');
      setInviteDialogOpen(false);
    } catch (error) {
      console.error('Error inviting member:', error);
      setError('Failed to send invitation. Please try again.');
    } finally {
      setInviting(false);
    }
  };

  const getRoleBadge = (role) => {
    switch (role) {
      case 'owner':
        return <Badge className="bg-purple-100 text-purple-800 hover:bg-purple-100">Owner</Badge>;
      case 'admin':
        return <Badge className="bg-blue-100 text-blue-800 hover:bg-blue-100">Admin</Badge>;
      case 'member':
        return <Badge className="bg-green-100 text-green-800 hover:bg-green-100">Member</Badge>;
      default:
        return <Badge>Unknown</Badge>;
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'active':
        return <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">Active</Badge>;
      case 'pending':
        return <Badge variant="outline" className="bg-yellow-50 text-yellow-700 border-yellow-200">Pending</Badge>;
      default:
        return <Badge variant="outline">Unknown</Badge>;
    }
  };

  // Filter members
  const filteredMembers = members.filter((member) => {
    const fullName = member.user.full_name.toLowerCase();
    const email = member.user.email.toLowerCase();
    const query = searchQuery.toLowerCase();
    
    return fullName.includes(query) || email.includes(query);
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Team</h1>
          <p className="text-muted-foreground">
            Manage your team members and their access
          </p>
        </div>
        <div className="mt-4 md:mt-0">
          <Dialog open={inviteDialogOpen} onOpenChange={setInviteDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <UserPlus className="mr-2 h-4 w-4" />
                Invite Member
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Invite Team Member</DialogTitle>
                <DialogDescription>
                  Invite a new member to join your organization
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                {error && (
                  <div className="text-sm font-medium text-destructive">
                    {error}
                  </div>
                )}
                <div className="space-y-2">
                  <Label htmlFor="email">Email Address</Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="colleague@example.com"
                    value={inviteEmail}
                    onChange={(e) => setInviteEmail(e.target.value)}
                    disabled={inviting}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="role">Role</Label>
                  <Select
                    value={inviteRole}
                    onValueChange={setInviteRole}
                    disabled={inviting}
                  >
                    <SelectTrigger id="role">
                      <SelectValue placeholder="Select a role" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="admin">Admin</SelectItem>
                      <SelectItem value="member">Member</SelectItem>
                    </SelectContent>
                  </Select>
                  <p className="text-xs text-muted-foreground">
                    <span className="font-medium">Admin:</span> Can manage team members, billing, and all documents.
                    <br />
                    <span className="font-medium">Member:</span> Can view and edit documents they have access to.
                  </p>
                </div>
              </div>
              <DialogFooter>
                <Button
                  variant="outline"
                  onClick={() => setInviteDialogOpen(false)}
                  disabled={inviting}
                >
                  Cancel
                </Button>
                <Button onClick={handleInvite} disabled={inviting || !inviteEmail.trim()}>
                  {inviting ? 'Sending...' : 'Send Invitation'}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
        <Input
          type="search"
          placeholder="Search team members..."
          className="pl-8"
          value={searchQuery}
          onChange={handleSearchChange}
        />
      </div>

      {/* Team members */}
      <Card>
        <CardHeader>
          <CardTitle>Team Members</CardTitle>
          <CardDescription>
            {currentOrganization?.name || 'Your organization'} has {members.length} members
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="border rounded-md">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Joined</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading ? (
                  Array(4)
                    .fill(0)
                    .map((_, i) => (
                      <TableRow key={i}>
                        <TableCell>
                          <div className="flex items-center gap-3">
                            <Skeleton className="h-8 w-8 rounded-full" />
                            <Skeleton className="h-4 w-[150px]" />
                          </div>
                        </TableCell>
                        <TableCell>
                          <Skeleton className="h-4 w-[180px]" />
                        </TableCell>
                        <TableCell>
                          <Skeleton className="h-6 w-16" />
                        </TableCell>
                        <TableCell>
                          <Skeleton className="h-6 w-16" />
                        </TableCell>
                        <TableCell>
                          <Skeleton className="h-4 w-[100px]" />
                        </TableCell>
                        <TableCell className="text-right">
                          <Skeleton className="h-8 w-8 rounded-full ml-auto" />
                        </TableCell>
                      </TableRow>
                    ))
                ) : filteredMembers.length > 0 ? (
                  filteredMembers.map((member) => (
                    <TableRow key={member.id}>
                      <TableCell>
                        <div className="flex items-center gap-3">
                          <Avatar>
                            <AvatarImage src={member.user.avatar_url} alt={member.user.full_name} />
                            <AvatarFallback>{getInitials(member.user.full_name)}</AvatarFallback>
                          </Avatar>
                          <div className="font-medium">{member.user.full_name}</div>
                        </div>
                      </TableCell>
                      <TableCell>{member.user.email}</TableCell>
                      <TableCell>{getRoleBadge(member.role)}</TableCell>
                      <TableCell>{getStatusBadge(member.status)}</TableCell>
                      <TableCell>{formatDate(member.joined_at)}</TableCell>
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
                            {member.role !== 'owner' && (
                              <>
                                <DropdownMenuItem>
                                  <UserCog className="mr-2 h-4 w-4" />
                                  Change Role
                                </DropdownMenuItem>
                                <DropdownMenuItem className="text-destructive">
                                  <Trash className="mr-2 h-4 w-4" />
                                  Remove
                                </DropdownMenuItem>
                              </>
                            )}
                            {member.role === 'owner' && (
                              <DropdownMenuItem disabled>
                                <Shield className="mr-2 h-4 w-4" />
                                Organization Owner
                              </DropdownMenuItem>
                            )}
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center py-8">
                      <div className="flex flex-col items-center justify-center">
                        <Users className="h-12 w-12 text-muted-foreground mb-4" />
                        <p className="text-muted-foreground">
                          No team members found matching your search.
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
    </div>
  );
}

