# LexiAI Project Structure

## Overview

This document outlines the directory structure and organization for the LexiAI MVP application, covering both the backend (Flask) and frontend (React) components.

## Backend Structure

```
backend/
├── venv/                      # Python virtual environment
├── src/
│   ├── models/                # Database models
│   │   ├── __init__.py
│   │   ├── user.py            # User model
│   │   ├── subscription.py    # Subscription model
│   │   ├── organization.py    # Organization model
│   │   ├── document.py        # Document model
│   │   ├── clause.py          # Clause model
│   │   ├── comment.py         # Comment model
│   │   └── audit.py           # Audit log model
│   │
│   ├── routes/                # API routes
│   │   ├── __init__.py
│   │   ├── auth.py            # Authentication routes
│   │   ├── users.py           # User management routes
│   │   ├── subscriptions.py   # Subscription management routes
│   │   ├── documents.py       # Document management routes
│   │   ├── clauses.py         # Clause management routes
│   │   ├── comments.py        # Comment management routes
│   │   ├── search.py          # Search functionality routes
│   │   └── admin.py           # Admin dashboard routes
│   │
│   ├── services/              # Business logic services
│   │   ├── __init__.py
│   │   ├── auth_service.py    # Authentication service
│   │   ├── document_service.py # Document processing service
│   │   ├── ai_service.py      # OpenAI integration service
│   │   ├── storage_service.py # File storage service
│   │   ├── billing_service.py # Stripe integration service
│   │   └── search_service.py  # Search service
│   │
│   ├── utils/                 # Utility functions
│   │   ├── __init__.py
│   │   ├── security.py        # Security utilities
│   │   ├── validators.py      # Input validation
│   │   ├── file_processors.py # File processing utilities
│   │   └── helpers.py         # General helper functions
│   │
│   ├── middleware/            # Middleware components
│   │   ├── __init__.py
│   │   ├── auth_middleware.py # Authentication middleware
│   │   ├── error_handler.py   # Error handling middleware
│   │   └── logging_middleware.py # Logging middleware
│   │
│   ├── static/                # Static files (built frontend will be served from here)
│   │
│   ├── database/              # Database files
│   │   └── app.db             # SQLite database (for development)
│   │
│   ├── config.py              # Application configuration
│   ├── main.py                # Application entry point
│   └── app.py                 # Flask application factory
│
├── migrations/                # Database migrations
├── tests/                     # Test files
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_documents.py
│   └── test_ai.py
│
├── .env.example               # Example environment variables
├── .gitignore                 # Git ignore file
├── requirements.txt           # Python dependencies
└── README.md                  # Backend documentation
```

## Frontend Structure

```
frontend/
├── public/                    # Public assets
│   ├── favicon.ico
│   ├── robots.txt
│   └── index.html             # HTML entry point
│
├── src/
│   ├── assets/                # Static assets
│   │   ├── images/            # Image files
│   │   ├── icons/             # Icon files
│   │   └── styles/            # Global styles
│   │
│   ├── components/            # Reusable components
│   │   ├── ui/                # UI components from shadcn/ui
│   │   ├── layout/            # Layout components
│   │   │   ├── Header.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   ├── Footer.jsx
│   │   │   └── Layout.jsx
│   │   │
│   │   ├── auth/              # Authentication components
│   │   │   ├── LoginForm.jsx
│   │   │   ├── SignupForm.jsx
│   │   │   └── PasswordReset.jsx
│   │   │
│   │   ├── documents/         # Document-related components
│   │   │   ├── DocumentList.jsx
│   │   │   ├── DocumentCard.jsx
│   │   │   ├── DocumentUpload.jsx
│   │   │   └── DocumentViewer.jsx
│   │   │
│   │   ├── clauses/           # Clause-related components
│   │   │   ├── ClauseList.jsx
│   │   │   ├── ClauseCard.jsx
│   │   │   └── ClauseViewer.jsx
│   │   │
│   │   ├── comments/          # Comment-related components
│   │   │   ├── CommentList.jsx
│   │   │   └── CommentForm.jsx
│   │   │
│   │   ├── search/            # Search-related components
│   │   │   ├── SearchBar.jsx
│   │   │   └── SearchResults.jsx
│   │   │
│   │   └── admin/             # Admin dashboard components
│   │       ├── UserManagement.jsx
│   │       └── SubscriptionManagement.jsx
│   │
│   ├── hooks/                 # Custom React hooks
│   │   ├── useAuth.js
│   │   ├── useDocuments.js
│   │   ├── useClauses.js
│   │   └── useSearch.js
│   │
│   ├── context/               # React context providers
│   │   ├── AuthContext.jsx
│   │   ├── DocumentContext.jsx
│   │   └── UIContext.jsx
│   │
│   ├── lib/                   # Utility functions and libraries
│   │   ├── api.js             # API client
│   │   ├── auth.js            # Authentication utilities
│   │   ├── formatting.js      # Data formatting utilities
│   │   └── validation.js      # Form validation utilities
│   │
│   ├── pages/                 # Page components
│   │   ├── auth/
│   │   │   ├── Login.jsx
│   │   │   ├── Signup.jsx
│   │   │   └── ForgotPassword.jsx
│   │   │
│   │   ├── dashboard/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Documents.jsx
│   │   │   └── Settings.jsx
│   │   │
│   │   ├── document/
│   │   │   ├── DocumentDetail.jsx
│   │   │   ├── DocumentEdit.jsx
│   │   │   └── DocumentUpload.jsx
│   │   │
│   │   ├── admin/
│   │   │   ├── AdminDashboard.jsx
│   │   │   ├── UserManagement.jsx
│   │   │   └── SubscriptionManagement.jsx
│   │   │
│   │   ├── Home.jsx           # Landing page
│   │   ├── Pricing.jsx        # Pricing page
│   │   ├── NotFound.jsx       # 404 page
│   │   └── ErrorBoundary.jsx  # Error boundary page
│   │
│   ├── routes/                # Route definitions
│   │   ├── PrivateRoute.jsx   # Protected route component
│   │   ├── AdminRoute.jsx     # Admin-only route component
│   │   └── AppRoutes.jsx      # Main route definitions
│   │
│   ├── App.css                # App-specific styles
│   ├── App.jsx                # Main App component
│   ├── index.css              # Global styles
│   └── main.jsx               # Entry point
│
├── .env.example               # Example environment variables
├── .gitignore                 # Git ignore file
├── package.json               # NPM dependencies and scripts
├── vite.config.js             # Vite configuration
└── README.md                  # Frontend documentation
```

## Configuration Files

### Backend Configuration

The backend configuration will be managed through environment variables and a `config.py` file:

```python
# src/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False') == 'True'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///database/app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    
    # File storage configuration
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
    
    # OpenAI configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Stripe configuration
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    # CORS configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
```

### Frontend Configuration

The frontend configuration will be managed through environment variables:

```
# .env.example
VITE_API_URL=http://localhost:5000/api
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_your_key
```

## Development Workflow

1. **Backend Development**:
   - Activate virtual environment: `source venv/bin/activate`
   - Run development server: `python src/main.py`
   - API will be available at `http://localhost:5000/api`

2. **Frontend Development**:
   - Run development server: `pnpm run dev`
   - Frontend will be available at `http://localhost:5173`

3. **Production Build**:
   - Build frontend: `pnpm run build`
   - Copy build files to backend static folder
   - Deploy backend application

## Deployment

For the MVP, we'll deploy the application as a monolith, with the Flask backend serving the React frontend from its static directory. This simplifies deployment and avoids CORS issues.

### Deployment Steps

1. Build the frontend:
   ```
   cd frontend
   pnpm run build
   ```

2. Copy the frontend build to the backend static directory:
   ```
   cp -r frontend/dist/* backend/src/static/
   ```

3. Deploy the backend application to the chosen hosting provider (AWS or Vercel).

## Version Control

The project will use Git for version control, with a main branch and feature branches for development:

- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: Feature branches
- `bugfix/*`: Bug fix branches

