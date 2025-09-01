# LexiAI MVP Architecture

## Overview

LexiAI is a SaaS application for contract review and due diligence, replicating the core functions of Kira Systems in a simplified MVP form. The application allows users to upload contracts, extract and classify clauses, highlight risks, and provide summaries of key obligations and deadlines.

## Technical Stack

### Frontend
- **Framework**: React 19
- **UI Library**: Tailwind CSS with shadcn/ui components
- **State Management**: React Context API
- **Routing**: React Router DOM
- **HTTP Client**: Fetch API
- **Form Handling**: React Hook Form with Zod validation

### Backend
- **Framework**: Flask (Python)
- **API**: RESTful API
- **Authentication**: JWT (JSON Web Tokens)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **File Storage**: AWS S3 (simulated locally for MVP)
- **AI Integration**: OpenAI API

### DevOps
- **Deployment**: AWS or Vercel (TBD)
- **Version Control**: Git

## System Architecture

The application follows a multi-tier architecture:

1. **Presentation Layer**: React frontend
2. **Application Layer**: Flask backend API
3. **Data Layer**: PostgreSQL database and S3 file storage
4. **AI Layer**: OpenAI API integration

## Core Components

### Authentication & Billing
- User signup/login with email + password
- JWT-based authentication
- Stripe subscription billing
- Admin dashboard for subscription management

### Contract Upload & Management
- Document upload (PDF, DOCX, TXT)
- Secure document storage
- Role-based access control
- Search and filter functionality

### AI Contract Review Engine
- Clause extraction and classification
- Risk highlighting
- Key obligations and deadlines detection
- Contract summary generation

### Search & Query
- Natural language query processing
- Relevant clause retrieval with context

### Collaboration
- Commenting system
- Document sharing
- Export to PDF/Word

## Database Schema (Preliminary)

### Users
- id (PK)
- email
- password_hash
- first_name
- last_name
- role (admin, user)
- created_at
- updated_at

### Subscriptions
- id (PK)
- user_id (FK)
- stripe_customer_id
- stripe_subscription_id
- plan_type
- status
- current_period_start
- current_period_end
- created_at
- updated_at

### Documents
- id (PK)
- user_id (FK)
- title
- description
- file_path
- file_type (PDF, DOCX, TXT)
- status (processing, processed, error)
- created_at
- updated_at

### Clauses
- id (PK)
- document_id (FK)
- clause_type
- content
- page_number
- risk_level
- created_at
- updated_at

### Comments
- id (PK)
- clause_id (FK)
- user_id (FK)
- content
- created_at
- updated_at

### DocumentShares
- id (PK)
- document_id (FK)
- user_id (FK)
- permission_level (read, comment, edit)
- created_at
- updated_at

## API Endpoints (Preliminary)

### Authentication
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/logout
- GET /api/auth/me

### Users
- GET /api/users
- GET /api/users/:id
- PUT /api/users/:id
- DELETE /api/users/:id

### Subscriptions
- POST /api/subscriptions
- GET /api/subscriptions/:id
- PUT /api/subscriptions/:id
- DELETE /api/subscriptions/:id

### Documents
- POST /api/documents
- GET /api/documents
- GET /api/documents/:id
- PUT /api/documents/:id
- DELETE /api/documents/:id

### Clauses
- GET /api/documents/:id/clauses
- GET /api/clauses/:id
- PUT /api/clauses/:id

### Comments
- POST /api/clauses/:id/comments
- GET /api/clauses/:id/comments
- PUT /api/comments/:id
- DELETE /api/comments/:id

### Shares
- POST /api/documents/:id/shares
- GET /api/documents/:id/shares
- PUT /api/shares/:id
- DELETE /api/shares/:id

### Search
- POST /api/search

## Security Considerations

- HTTPS for all communications
- JWT for authentication
- Password hashing with bcrypt
- Role-based access control
- Input validation and sanitization
- GDPR compliance for data storage and processing
- Regular security audits

## Scalability Considerations

- Multi-tenant architecture
- Database indexing for performance
- Caching strategies
- Asynchronous processing for document analysis
- Horizontal scaling capabilities

## Future Enhancements (Post-MVP)

- Advanced document comparison
- Machine learning model fine-tuning
- Template library for common contracts
- Batch processing for multiple documents
- Integration with document management systems
- Mobile application

