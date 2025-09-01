# LexiAI API Reference

This document provides detailed information about the LexiAI API endpoints, including request parameters, response formats, and examples.

## Base URL

All API endpoints are relative to the base URL:

```
https://api.lexiai.com/api/v1
```

## Authentication

Most API endpoints require authentication using JWT (JSON Web Token). Include the token in the Authorization header:

```
Authorization: Bearer <token>
```

### Get Authentication Token

```
POST /auth/login
```

Authenticate a user and get a JWT token.

#### Request Body

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

#### Response

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "role": "user",
    "created_at": "2023-01-01T00:00:00Z"
  }
}
```

### Register New User

```
POST /auth/register
```

Register a new user and organization.

#### Request Body

```json
{
  "email": "newuser@example.com",
  "password": "password123",
  "first_name": "Jane",
  "last_name": "Smith",
  "organization_name": "Acme Inc."
}
```

#### Response

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 2,
    "email": "newuser@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "full_name": "Jane Smith",
    "role": "user",
    "created_at": "2023-01-02T00:00:00Z"
  },
  "organization": {
    "id": 1,
    "name": "Acme Inc.",
    "created_at": "2023-01-02T00:00:00Z"
  }
}
```

### Get Current User

```
GET /auth/me
```

Get information about the currently authenticated user.

#### Response

```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "role": "user",
    "created_at": "2023-01-01T00:00:00Z"
  }
}
```

### Refresh Token

```
POST /auth/refresh
```

Refresh the JWT token.

#### Response

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Logout

```
POST /auth/logout
```

Invalidate the current JWT token.

#### Response

```json
{
  "message": "Successfully logged out"
}
```

## Users

### Get All Users

```
GET /users
```

Get all users (admin only).

#### Query Parameters

- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20)
- `role` (optional): Filter by role (admin, user)
- `organization_id` (optional): Filter by organization

#### Response

```json
{
  "users": [
    {
      "id": 1,
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "full_name": "John Doe",
      "role": "user",
      "created_at": "2023-01-01T00:00:00Z"
    },
    {
      "id": 2,
      "email": "admin@example.com",
      "first_name": "Admin",
      "last_name": "User",
      "full_name": "Admin User",
      "role": "admin",
      "created_at": "2023-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_pages": 1,
    "total_items": 2
  }
}
```

### Get User by ID

```
GET /users/{id}
```

Get a specific user by ID.

#### Response

```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "role": "user",
    "created_at": "2023-01-01T00:00:00Z"
  }
}
```

### Update User

```
PUT /users/{id}
```

Update a user's information.

#### Request Body

```json
{
  "first_name": "Johnny",
  "last_name": "Doe",
  "role": "user"
}
```

#### Response

```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "Johnny",
    "last_name": "Doe",
    "full_name": "Johnny Doe",
    "role": "user",
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-03T00:00:00Z"
  }
}
```

### Delete User

```
DELETE /users/{id}
```

Delete a user.

#### Response

```json
{
  "message": "User deleted successfully"
}
```

## Organizations

### Get All Organizations

```
GET /organizations
```

Get all organizations for the current user.

#### Response

```json
{
  "organizations": [
    {
      "id": 1,
      "name": "Acme Inc.",
      "created_at": "2023-01-01T00:00:00Z",
      "role": "owner"
    }
  ]
}
```

### Create Organization

```
POST /organizations
```

Create a new organization.

#### Request Body

```json
{
  "name": "New Organization"
}
```

#### Response

```json
{
  "organization": {
    "id": 2,
    "name": "New Organization",
    "created_at": "2023-01-03T00:00:00Z",
    "role": "owner"
  }
}
```

### Get Organization by ID

```
GET /organizations/{id}
```

Get a specific organization by ID.

#### Response

```json
{
  "organization": {
    "id": 1,
    "name": "Acme Inc.",
    "created_at": "2023-01-01T00:00:00Z",
    "created_by": {
      "id": 1,
      "full_name": "John Doe"
    },
    "member_count": 5,
    "document_count": 10
  }
}
```

### Update Organization

```
PUT /organizations/{id}
```

Update an organization.

#### Request Body

```json
{
  "name": "Acme Corporation"
}
```

#### Response

```json
{
  "organization": {
    "id": 1,
    "name": "Acme Corporation",
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-03T00:00:00Z"
  }
}
```

### Delete Organization

```
DELETE /organizations/{id}
```

Delete an organization.

#### Response

```json
{
  "message": "Organization deleted successfully"
}
```

### Get Organization Members

```
GET /organizations/{id}/members
```

Get all members of an organization.

#### Response

```json
{
  "members": [
    {
      "id": 1,
      "email": "user@example.com",
      "full_name": "John Doe",
      "role": "owner",
      "joined_at": "2023-01-01T00:00:00Z"
    },
    {
      "id": 3,
      "email": "member@example.com",
      "full_name": "Team Member",
      "role": "member",
      "joined_at": "2023-01-02T00:00:00Z"
    }
  ]
}
```

### Add Organization Member

```
POST /organizations/{id}/members
```

Add a member to an organization.

#### Request Body

```json
{
  "email": "newmember@example.com",
  "role": "member"
}
```

#### Response

```json
{
  "message": "Invitation sent successfully",
  "invitation": {
    "id": 1,
    "email": "newmember@example.com",
    "role": "member",
    "expires_at": "2023-01-10T00:00:00Z"
  }
}
```

### Remove Organization Member

```
DELETE /organizations/{id}/members/{userId}
```

Remove a member from an organization.

#### Response

```json
{
  "message": "Member removed successfully"
}
```

## Documents

### Get All Documents

```
GET /documents
```

Get all documents for the current user.

#### Query Parameters

- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20)
- `organization_id` (optional): Filter by organization
- `status` (optional): Filter by status (uploaded, processing, analyzed, error)
- `search` (optional): Search by title or content

#### Response

```json
{
  "documents": [
    {
      "id": 1,
      "title": "Contract Agreement",
      "status": "analyzed",
      "created_at": "2023-01-01T00:00:00Z",
      "updated_at": "2023-01-01T00:00:00Z",
      "uploaded_by": {
        "id": 1,
        "full_name": "John Doe"
      },
      "organization": {
        "id": 1,
        "name": "Acme Inc."
      },
      "latest_version": {
        "id": 1,
        "version_number": 1,
        "file_name": "contract.pdf",
        "file_type": "application/pdf",
        "file_size": 1024000,
        "created_at": "2023-01-01T00:00:00Z"
      }
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_pages": 1,
    "total_items": 1
  }
}
```

### Upload Document

```
POST /documents
```

Upload a new document.

#### Request Body (multipart/form-data)

- `title`: Document title
- `file`: Document file (PDF, DOCX, TXT)
- `organization_id` (optional): Organization ID

#### Response

```json
{
  "document": {
    "id": 2,
    "title": "New Contract",
    "status": "uploaded",
    "created_at": "2023-01-03T00:00:00Z",
    "uploaded_by": {
      "id": 1,
      "full_name": "John Doe"
    },
    "organization": {
      "id": 1,
      "name": "Acme Inc."
    },
    "latest_version": {
      "id": 2,
      "version_number": 1,
      "file_name": "new_contract.pdf",
      "file_type": "application/pdf",
      "file_size": 2048000,
      "created_at": "2023-01-03T00:00:00Z"
    }
  }
}
```

### Get Document by ID

```
GET /documents/{id}
```

Get a specific document by ID.

#### Response

```json
{
  "document": {
    "id": 1,
    "title": "Contract Agreement",
    "status": "analyzed",
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z",
    "uploaded_by": {
      "id": 1,
      "full_name": "John Doe"
    },
    "organization": {
      "id": 1,
      "name": "Acme Inc."
    },
    "versions": [
      {
        "id": 1,
        "version_number": 1,
        "file_name": "contract.pdf",
        "file_type": "application/pdf",
        "file_size": 1024000,
        "created_at": "2023-01-01T00:00:00Z"
      }
    ],
    "shares": [
      {
        "id": 1,
        "shared_with_email": "colleague@example.com",
        "permission_level": "view",
        "created_at": "2023-01-02T00:00:00Z"
      }
    ]
  }
}
```

### Update Document

```
PUT /documents/{id}
```

Update a document's metadata.

#### Request Body

```json
{
  "title": "Updated Contract Title"
}
```

#### Response

```json
{
  "document": {
    "id": 1,
    "title": "Updated Contract Title",
    "status": "analyzed",
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-03T00:00:00Z"
  }
}
```

### Delete Document

```
DELETE /documents/{id}
```

Delete a document.

#### Response

```json
{
  "message": "Document deleted successfully"
}
```

### Get Document Versions

```
GET /documents/{id}/versions
```

Get all versions of a document.

#### Response

```json
{
  "versions": [
    {
      "id": 1,
      "version_number": 1,
      "file_name": "contract.pdf",
      "file_type": "application/pdf",
      "file_size": 1024000,
      "created_at": "2023-01-01T00:00:00Z",
      "created_by": {
        "id": 1,
        "full_name": "John Doe"
      }
    }
  ]
}
```

### Upload New Version

```
POST /documents/{id}/versions
```

Upload a new version of a document.

#### Request Body (multipart/form-data)

- `file`: Document file (PDF, DOCX, TXT)

#### Response

```json
{
  "version": {
    "id": 2,
    "version_number": 2,
    "file_name": "contract_v2.pdf",
    "file_type": "application/pdf",
    "file_size": 1048576,
    "created_at": "2023-01-03T00:00:00Z",
    "created_by": {
      "id": 1,
      "full_name": "John Doe"
    }
  }
}
```

### Share Document

```
POST /documents/{id}/share
```

Share a document with another user.

#### Request Body

```json
{
  "email": "colleague@example.com",
  "permission": "view"
}
```

#### Response

```json
{
  "message": "Document shared successfully",
  "share": {
    "id": 1,
    "shared_with_email": "colleague@example.com",
    "permission_level": "view",
    "created_at": "2023-01-03T00:00:00Z"
  }
}
```

### Get Document Shares

```
GET /documents/{id}/shares
```

Get all shares for a document.

#### Response

```json
{
  "shares": [
    {
      "id": 1,
      "shared_with_email": "colleague@example.com",
      "permission_level": "view",
      "created_at": "2023-01-02T00:00:00Z"
    }
  ]
}
```

### Remove Document Share

```
DELETE /documents/{id}/shares/{shareId}
```

Remove a share from a document.

#### Response

```json
{
  "message": "Share removed successfully"
}
```

## AI Analysis

### Analyze Document

```
POST /ai/analyze/{documentId}
```

Start AI analysis of a document.

#### Response

```json
{
  "message": "Document analysis started",
  "task_id": "12345678-1234-5678-1234-567812345678"
}
```

### Check Analysis Status

```
GET /ai/status/{taskId}
```

Check the status of a document analysis task.

#### Response

```json
{
  "status": "processing",
  "progress": 50,
  "message": "Analyzing document content"
}
```

### Get Document Clauses

```
GET /ai/clauses/{documentId}
```

Get all clauses extracted from a document.

#### Query Parameters

- `category` (optional): Filter by clause category
- `risk_level` (optional): Filter by risk level (high, medium, low, none)

#### Response

```json
{
  "clauses": [
    {
      "id": 1,
      "category": {
        "id": 1,
        "name": "Termination"
      },
      "text": "Either party may terminate this Agreement upon 30 days written notice.",
      "risk_level": "medium",
      "risk_description": "Short termination period may not provide sufficient time to transition services."
    },
    {
      "id": 2,
      "category": {
        "id": 2,
        "name": "Liability"
      },
      "text": "In no event shall either party be liable for any indirect, incidental, special, or consequential damages.",
      "risk_level": "low",
      "risk_description": "Standard liability limitation clause."
    }
  ]
}
```

### Get Document Summary

```
GET /ai/summary/{documentId}
```

Get the AI-generated summary of a document.

#### Response

```json
{
  "summary": {
    "overview": "This is a service agreement between Company A and Company B for software development services.",
    "parties": ["Company A", "Company B"],
    "key_terms": [
      "Term: 1 year",
      "Payment: $10,000 per month",
      "Termination: 30 days notice"
    ],
    "important_dates": [
      "Effective Date: January 1, 2023",
      "Expiration Date: December 31, 2023"
    ],
    "notable_provisions": [
      "Short termination period (30 days)",
      "Limited liability for both parties"
    ]
  }
}
```

### Get Document Obligations

```
GET /ai/obligations/{documentId}
```

Get all obligations extracted from a document.

#### Response

```json
{
  "obligations": [
    {
      "id": 1,
      "party": "Customer",
      "description": "Pay monthly service fee",
      "deadline": "15th of each month",
      "consequence": "Late fee of 1.5% per month on outstanding balance"
    },
    {
      "id": 2,
      "party": "Provider",
      "description": "Deliver monthly progress report",
      "deadline": "Last day of each month",
      "consequence": "Customer may withhold payment until report is delivered"
    }
  ]
}
```

### Search Document

```
POST /ai/search/{documentId}
```

Search a document with a natural language query.

#### Request Body

```json
{
  "query": "What is the termination period?"
}
```

#### Response

```json
{
  "result": {
    "answer": "The termination period is 30 days.",
    "context": "Either party may terminate this Agreement upon 30 days written notice.",
    "explanation": "The contract specifies a 30-day termination period with written notice."
  }
}
```

### Get Search History

```
GET /ai/search-history/{documentId}
```

Get search history for a document.

#### Response

```json
{
  "search_history": [
    {
      "id": 1,
      "query": "What is the termination period?",
      "created_at": "2023-01-02T00:00:00Z",
      "user": {
        "id": 1,
        "full_name": "John Doe"
      }
    },
    {
      "id": 2,
      "query": "What are the payment terms?",
      "created_at": "2023-01-03T00:00:00Z",
      "user": {
        "id": 1,
        "full_name": "John Doe"
      }
    }
  ]
}
```

## Comments

### Get Document Comments

```
GET /documents/{id}/comments
```

Get all comments for a document.

#### Response

```json
{
  "comments": [
    {
      "id": 1,
      "text": "This clause needs review by legal.",
      "created_at": "2023-01-02T00:00:00Z",
      "user": {
        "id": 1,
        "full_name": "John Doe"
      },
      "clause_id": 1
    }
  ]
}
```

### Add Comment

```
POST /documents/{id}/comments
```

Add a comment to a document or clause.

#### Request Body

```json
{
  "text": "This clause needs review by legal.",
  "clause_id": 1
}
```

#### Response

```json
{
  "comment": {
    "id": 1,
    "text": "This clause needs review by legal.",
    "created_at": "2023-01-03T00:00:00Z",
    "user": {
      "id": 1,
      "full_name": "John Doe"
    },
    "clause_id": 1
  }
}
```

### Update Comment

```
PUT /comments/{id}
```

Update a comment.

#### Request Body

```json
{
  "text": "This clause has been reviewed by legal."
}
```

#### Response

```json
{
  "comment": {
    "id": 1,
    "text": "This clause has been reviewed by legal.",
    "created_at": "2023-01-02T00:00:00Z",
    "updated_at": "2023-01-03T00:00:00Z",
    "user": {
      "id": 1,
      "full_name": "John Doe"
    },
    "clause_id": 1
  }
}
```

### Delete Comment

```
DELETE /comments/{id}
```

Delete a comment.

#### Response

```json
{
  "message": "Comment deleted successfully"
}
```

## Subscriptions

### Get Current Subscription

```
GET /subscriptions
```

Get the current subscription for the user's organization.

#### Response

```json
{
  "subscription": {
    "id": 1,
    "status": "active",
    "plan": {
      "id": 1,
      "name": "Standard",
      "price": 10000,
      "billing_interval": "month",
      "features": {
        "max_documents": 100,
        "max_users": 10,
        "advanced_ai": false
      }
    },
    "current_period_start": "2023-01-01T00:00:00Z",
    "current_period_end": "2023-02-01T00:00:00Z",
    "created_at": "2023-01-01T00:00:00Z"
  }
}
```

### Create Subscription

```
POST /subscriptions
```

Create a new subscription.

#### Request Body

```json
{
  "plan_id": 1,
  "payment_method_id": "pm_card_visa"
}
```

#### Response

```json
{
  "subscription": {
    "id": 1,
    "status": "active",
    "plan": {
      "id": 1,
      "name": "Standard",
      "price": 10000,
      "billing_interval": "month",
      "features": {
        "max_documents": 100,
        "max_users": 10,
        "advanced_ai": false
      }
    },
    "current_period_start": "2023-01-03T00:00:00Z",
    "current_period_end": "2023-02-03T00:00:00Z",
    "created_at": "2023-01-03T00:00:00Z"
  }
}
```

### Update Subscription

```
PUT /subscriptions/{id}
```

Update a subscription.

#### Request Body

```json
{
  "plan_id": 2
}
```

#### Response

```json
{
  "subscription": {
    "id": 1,
    "status": "active",
    "plan": {
      "id": 2,
      "name": "Premium",
      "price": 20000,
      "billing_interval": "month",
      "features": {
        "max_documents": 500,
        "max_users": 50,
        "advanced_ai": true
      }
    },
    "current_period_start": "2023-01-03T00:00:00Z",
    "current_period_end": "2023-02-03T00:00:00Z",
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-03T00:00:00Z"
  }
}
```

### Cancel Subscription

```
DELETE /subscriptions/{id}
```

Cancel a subscription.

#### Response

```json
{
  "message": "Subscription cancelled successfully",
  "subscription": {
    "id": 1,
    "status": "cancelled",
    "cancel_at_period_end": true,
    "current_period_end": "2023-02-03T00:00:00Z"
  }
}
```

### Get Subscription Plans

```
GET /subscriptions/plans
```

Get all available subscription plans.

#### Response

```json
{
  "plans": [
    {
      "id": 1,
      "name": "Standard",
      "description": "For small teams",
      "price": 10000,
      "billing_interval": "month",
      "features": {
        "max_documents": 100,
        "max_users": 10,
        "advanced_ai": false
      }
    },
    {
      "id": 2,
      "name": "Premium",
      "description": "For growing businesses",
      "price": 20000,
      "billing_interval": "month",
      "features": {
        "max_documents": 500,
        "max_users": 50,
        "advanced_ai": true
      }
    }
  ]
}
```

## GDPR Compliance

### Export User Data

```
POST /gdpr/export-data
```

Export all data for the current user.

#### Response

File download with user data in JSON format.

### Anonymize User Data

```
POST /gdpr/anonymize-data
```

Anonymize data for the current user.

#### Response

```json
{
  "success": true,
  "message": "User data anonymized successfully"
}
```

### Delete User Data

```
POST /gdpr/delete-data
```

Delete all data for the current user.

#### Response

```json
{
  "success": true,
  "message": "User data deleted successfully"
}
```

### Record User Consent

```
POST /gdpr/consent
```

Record user consent for data processing.

#### Request Body

```json
{
  "consent_type": "marketing",
  "consented": true
}
```

#### Response

```json
{
  "success": true,
  "message": "Consent recorded successfully"
}
```

### Get User Consents

```
GET /gdpr/consents
```

Get all consents for the current user.

#### Response

```json
{
  "success": true,
  "data": {
    "user_id": 1,
    "consents": [
      {
        "consent_type": "marketing",
        "consented": true,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
      },
      {
        "consent_type": "analytics",
        "consented": false,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-02T00:00:00Z"
      }
    ]
  }
}
```

## Error Responses

All API endpoints return standard error responses in the following format:

```json
{
  "error": "Error message",
  "details": {
    "field1": ["Error details for field1"],
    "field2": ["Error details for field2"]
  }
}
```

### Common HTTP Status Codes

- `200 OK`: Request succeeded
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required or failed
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

