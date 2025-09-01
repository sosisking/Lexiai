# LexiAI Developer Guide

This guide provides technical documentation for developers working with the LexiAI platform, including architecture overview, API documentation, and development workflows.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Development Environment Setup](#development-environment-setup)
3. [Backend Development](#backend-development)
4. [Frontend Development](#frontend-development)
5. [API Documentation](#api-documentation)
6. [Database Schema](#database-schema)
7. [Authentication and Authorization](#authentication-and-authorization)
8. [AI Integration](#ai-integration)
9. [Testing](#testing)
10. [Deployment](#deployment)
11. [Monitoring and Logging](#monitoring-and-logging)
12. [Security Best Practices](#security-best-practices)

## Architecture Overview

LexiAI is built using a modern microservices architecture with the following components:

### System Components

- **Frontend**: React single-page application with Tailwind CSS
- **Backend API**: Flask RESTful API with JWT authentication
- **Database**: PostgreSQL for relational data storage
- **Cache**: Redis for caching and task queue
- **Storage**: Local filesystem or AWS S3 for document storage
- **AI Service**: Integration with OpenAI API for document analysis
- **Background Workers**: Celery for asynchronous task processing
- **Web Server**: Nginx for serving static files and API proxying

### Architecture Diagram

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Browser   │◄────►│    Nginx    │◄────►│  Frontend   │
└─────────────┘      └─────────────┘      │  (React)    │
                           │              └─────────────┘
                           ▼                     │
                     ┌─────────────┐             │
                     │  Backend    │◄────────────┘
                     │  API        │
                     │  (Flask)    │
                     └─────────────┘
                           │
           ┌───────────────┼───────────────┬───────────────┐
           ▼               ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │ PostgreSQL  │ │    Redis    │ │ Document    │ │   OpenAI    │
    │  Database   │ │             │ │  Storage    │ │     API     │
    └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Celery    │
                    │   Workers   │
                    └─────────────┘
```

### Data Flow

1. User interacts with the React frontend in the browser
2. Frontend makes API calls to the Flask backend
3. Backend authenticates requests using JWT tokens
4. Backend processes requests, interacting with:
   - PostgreSQL for data storage and retrieval
   - Redis for caching and task queuing
   - Document storage for file operations
   - OpenAI API for document analysis
5. Long-running tasks are delegated to Celery workers
6. Results are returned to the frontend via the API

## Development Environment Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Redis 7+
- Docker and Docker Compose (optional)

### Local Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/lexiai.git
cd lexiai
```

2. Set up the backend:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Edit .env with your configuration
flask db upgrade
flask run --host=0.0.0.0
```

3. Set up the frontend:

```bash
cd frontend
npm install
cp .env.example .env  # Edit .env with your configuration
npm run dev
```

4. Start Redis and Celery worker:

```bash
# In a new terminal
redis-server

# In another terminal
cd backend
source venv/bin/activate
celery -A src.tasks.celery worker --loglevel=info
```

### Docker Setup

Alternatively, use Docker Compose for a containerized development environment:

```bash
cp .env.example .env  # Edit .env with your configuration
docker-compose -f docker-compose.dev.yml up
```

## Backend Development

### Project Structure

```
backend/
├── src/                # Source code
│   ├── main.py         # Application entry point
│   ├── config.py       # Configuration
│   ├── models/         # Database models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── document.py
│   │   └── ...
│   ├── routes/         # API routes
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── document.py
│   │   └── ...
│   ├── services/       # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── ai_service.py
│   │   └── ...
│   ├── middleware/     # Middleware components
│   │   ├── __init__.py
│   │   ├── auth_middleware.py
│   │   └── ...
│   └── utils/          # Utility functions
│       ├── __init__.py
│       ├── security.py
│       └── ...
├── tests/              # Test suite
│   ├── __init__.py
│   ├── test_auth.py
│   └── ...
└── requirements.txt    # Python dependencies
```

### Adding a New Model

1. Create a new file in `src/models/` (e.g., `new_model.py`):

```python
from datetime import datetime
from src.models import db

class NewModel(db.Model):
    """Description of the new model."""
    
    __tablename__ = 'new_models'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('new_models', lazy=True))
    
    def __repr__(self):
        return f'<NewModel {self.id}: {self.name}>'
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user_id': self.user_id
        }
```

2. Import the model in `src/models/__init__.py`
3. Create a migration:

```bash
flask db migrate -m "Add new model"
flask db upgrade
```

### Adding a New API Endpoint

1. Create or update a route file in `src/routes/` (e.g., `new_model.py`):

```python
from flask import Blueprint, request, jsonify, g
from src.models.new_model import NewModel
from src.models import db
from src.middleware.auth_middleware import jwt_required

new_model_bp = Blueprint('new_model', __name__, url_prefix='/api/v1/new-models')

@new_model_bp.route('', methods=['GET'])
@jwt_required
def get_all_new_models():
    """Get all new models for the current user."""
    new_models = NewModel.query.filter_by(user_id=g.user.id).all()
    return jsonify({
        'new_models': [model.to_dict() for model in new_models]
    }), 200

@new_model_bp.route('', methods=['POST'])
@jwt_required
def create_new_model():
    """Create a new model."""
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({
            'error': 'Missing required fields: name'
        }), 400
    
    new_model = NewModel(
        name=data['name'],
        description=data.get('description', ''),
        user_id=g.user.id
    )
    
    db.session.add(new_model)
    db.session.commit()
    
    return jsonify({
        'message': 'New model created successfully',
        'new_model': new_model.to_dict()
    }), 201

@new_model_bp.route('/<int:id>', methods=['GET'])
@jwt_required
def get_new_model(id):
    """Get a specific new model."""
    new_model = NewModel.query.filter_by(id=id, user_id=g.user.id).first()
    
    if not new_model:
        return jsonify({
            'error': 'New model not found'
        }), 404
    
    return jsonify({
        'new_model': new_model.to_dict()
    }), 200

@new_model_bp.route('/<int:id>', methods=['PUT'])
@jwt_required
def update_new_model(id):
    """Update a specific new model."""
    new_model = NewModel.query.filter_by(id=id, user_id=g.user.id).first()
    
    if not new_model:
        return jsonify({
            'error': 'New model not found'
        }), 404
    
    data = request.get_json()
    
    if 'name' in data:
        new_model.name = data['name']
    
    if 'description' in data:
        new_model.description = data['description']
    
    db.session.commit()
    
    return jsonify({
        'message': 'New model updated successfully',
        'new_model': new_model.to_dict()
    }), 200

@new_model_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required
def delete_new_model(id):
    """Delete a specific new model."""
    new_model = NewModel.query.filter_by(id=id, user_id=g.user.id).first()
    
    if not new_model:
        return jsonify({
            'error': 'New model not found'
        }), 404
    
    db.session.delete(new_model)
    db.session.commit()
    
    return jsonify({
        'message': 'New model deleted successfully'
    }), 200
```

2. Register the blueprint in `src/main.py`:

```python
from src.routes.new_model import new_model_bp

# Register blueprints
app.register_blueprint(new_model_bp)
```

### Creating a Background Task

1. Define the task in `src/tasks.py`:

```python
from src.tasks.celery import celery_app
from src.models.new_model import NewModel
from src.models import db

@celery_app.task(bind=True)
def process_new_model(self, model_id):
    """Process a new model asynchronously."""
    try:
        # Get the model
        new_model = NewModel.query.get(model_id)
        if not new_model:
            return {'status': 'error', 'message': 'Model not found'}
        
        # Perform processing
        # ...
        
        # Update the model
        new_model.status = 'processed'
        db.session.commit()
        
        return {'status': 'success', 'model_id': model_id}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
```

2. Call the task from your API endpoint:

```python
from src.tasks import process_new_model

@new_model_bp.route('/<int:id>/process', methods=['POST'])
@jwt_required
def process_model(id):
    """Process a specific new model."""
    new_model = NewModel.query.filter_by(id=id, user_id=g.user.id).first()
    
    if not new_model:
        return jsonify({
            'error': 'New model not found'
        }), 404
    
    # Start the background task
    task = process_new_model.delay(new_model.id)
    
    return jsonify({
        'message': 'Processing started',
        'task_id': task.id
    }), 202
```

## Frontend Development

### Project Structure

```
frontend/
├── public/             # Static assets
├── src/                # Source code
│   ├── components/     # React components
│   │   ├── layout/     # Layout components
│   │   ├── ui/         # UI components
│   │   └── ...
│   ├── contexts/       # React contexts
│   │   ├── AuthContext.jsx
│   │   └── ...
│   ├── lib/            # Utility libraries
│   │   ├── api.js      # API client
│   │   └── ...
│   ├── pages/          # Page components
│   │   ├── Dashboard.jsx
│   │   └── ...
│   ├── App.jsx         # Main application component
│   ├── main.jsx        # Entry point
│   └── router.jsx      # Router configuration
├── .env.example        # Environment variables example
└── package.json        # Node.js dependencies
```

### Adding a New Component

1. Create a new component file in `src/components/` (e.g., `NewComponent.jsx`):

```jsx
import React, { useState } from 'react';
import { Button } from '@/components/ui/button';

export function NewComponent({ title, onAction }) {
  const [isActive, setIsActive] = useState(false);
  
  const handleClick = () => {
    setIsActive(!isActive);
    if (onAction) {
      onAction(isActive);
    }
  };
  
  return (
    <div className="p-4 border rounded-lg">
      <h3 className="text-lg font-medium">{title}</h3>
      <p className="text-gray-500 mt-1">
        This is a new component.
      </p>
      <Button 
        className={`mt-4 ${isActive ? 'bg-blue-600' : 'bg-gray-300'}`}
        onClick={handleClick}
      >
        {isActive ? 'Active' : 'Inactive'}
      </Button>
    </div>
  );
}
```

2. Use the component in a page:

```jsx
import { NewComponent } from '@/components/NewComponent';

export default function SomePage() {
  const handleComponentAction = (isActive) => {
    console.log(`Component is now ${isActive ? 'inactive' : 'active'}`);
  };
  
  return (
    <div className="container mx-auto py-8">
      <h1 className="text-2xl font-bold mb-6">Some Page</h1>
      <NewComponent 
        title="My New Component" 
        onAction={handleComponentAction} 
      />
    </div>
  );
}
```

### Adding a New Page

1. Create a new page file in `src/pages/` (e.g., `NewPage.jsx`):

```jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { NewComponent } from '@/components/NewComponent';

export default function NewPage() {
  const [data, setData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        const response = await api.get('/api/v1/new-models');
        setData(response.data.new_models);
        setError(null);
      } catch (err) {
        setError('Failed to fetch data');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchData();
  }, []);
  
  const handleCreate = () => {
    navigate('/new-models/create');
  };
  
  if (isLoading) {
    return <div className="flex justify-center p-8">Loading...</div>;
  }
  
  if (error) {
    return (
      <div className="p-8 text-red-500">
        Error: {error}
        <Button onClick={() => window.location.reload()} className="ml-4">
          Retry
        </Button>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">New Models</h1>
        <Button onClick={handleCreate}>Create New</Button>
      </div>
      
      {data.length === 0 ? (
        <div className="text-center p-8 bg-gray-50 rounded-lg">
          <p className="text-gray-500">No models found</p>
          <Button onClick={handleCreate} className="mt-4">
            Create Your First Model
          </Button>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {data.map((model) => (
            <NewComponent 
              key={model.id}
              title={model.name}
              onAction={() => navigate(`/new-models/${model.id}`)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
```

2. Add the page to the router in `src/router.jsx`:

```jsx
import NewPage from '@/pages/NewPage';

// Inside the router configuration
{
  path: 'new-models',
  element: <ProtectedRoute><NewPage /></ProtectedRoute>,
}
```

### API Integration

1. Define API endpoints in `src/lib/api.js`:

```javascript
import axios from 'axios';

// Create axios instance
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for authentication
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle authentication errors
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const authApi = {
  login: (credentials) => api.post('/api/v1/auth/login', credentials),
  register: (userData) => api.post('/api/v1/auth/register', userData),
  me: () => api.get('/api/v1/auth/me'),
  logout: () => api.post('/api/v1/auth/logout'),
};

export const newModelApi = {
  getAll: () => api.get('/api/v1/new-models'),
  get: (id) => api.get(`/api/v1/new-models/${id}`),
  create: (data) => api.post('/api/v1/new-models', data),
  update: (id, data) => api.put(`/api/v1/new-models/${id}`, data),
  delete: (id) => api.delete(`/api/v1/new-models/${id}`),
  process: (id) => api.post(`/api/v1/new-models/${id}/process`),
};
```

2. Use the API in components:

```jsx
import { useState } from 'react';
import { newModelApi } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useNavigate } from 'react-router-dom';

export default function CreateNewModel() {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!name) {
      setError('Name is required');
      return;
    }
    
    try {
      setIsSubmitting(true);
      setError(null);
      
      const response = await newModelApi.create({
        name,
        description,
      });
      
      navigate(`/new-models/${response.data.new_model.id}`);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create model');
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  return (
    <div className="container mx-auto py-8 max-w-md">
      <h1 className="text-2xl font-bold mb-6">Create New Model</h1>
      
      {error && (
        <div className="bg-red-50 text-red-500 p-4 rounded-lg mb-6">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="name" className="block text-sm font-medium mb-1">
            Name *
          </label>
          <Input
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>
        
        <div>
          <label htmlFor="description" className="block text-sm font-medium mb-1">
            Description
          </label>
          <textarea
            id="description"
            className="w-full p-2 border rounded-md"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={4}
          />
        </div>
        
        <div className="flex justify-end space-x-4">
          <Button
            type="button"
            variant="outline"
            onClick={() => navigate('/new-models')}
            disabled={isSubmitting}
          >
            Cancel
          </Button>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Creating...' : 'Create Model'}
          </Button>
        </div>
      </form>
    </div>
  );
}
```

## API Documentation

### Authentication

All API endpoints except for authentication endpoints require a valid JWT token.

#### Headers

```
Authorization: Bearer <token>
```

#### Authentication Endpoints

- `POST /api/v1/auth/login`: Log in with email and password
- `POST /api/v1/auth/register`: Register a new user
- `GET /api/v1/auth/me`: Get current user information
- `POST /api/v1/auth/refresh`: Refresh JWT token
- `POST /api/v1/auth/logout`: Log out and invalidate token

### User Endpoints

- `GET /api/v1/users`: Get all users (admin only)
- `GET /api/v1/users/:id`: Get user by ID
- `PUT /api/v1/users/:id`: Update user
- `DELETE /api/v1/users/:id`: Delete user

### Organization Endpoints

- `GET /api/v1/organizations`: Get all organizations for current user
- `POST /api/v1/organizations`: Create a new organization
- `GET /api/v1/organizations/:id`: Get organization by ID
- `PUT /api/v1/organizations/:id`: Update organization
- `DELETE /api/v1/organizations/:id`: Delete organization
- `GET /api/v1/organizations/:id/members`: Get organization members
- `POST /api/v1/organizations/:id/members`: Add member to organization
- `DELETE /api/v1/organizations/:id/members/:userId`: Remove member from organization

### Document Endpoints

- `GET /api/v1/documents`: Get all documents for current user
- `POST /api/v1/documents`: Upload a new document
- `GET /api/v1/documents/:id`: Get document by ID
- `PUT /api/v1/documents/:id`: Update document metadata
- `DELETE /api/v1/documents/:id`: Delete document
- `GET /api/v1/documents/:id/versions`: Get document versions
- `POST /api/v1/documents/:id/versions`: Upload a new document version
- `GET /api/v1/documents/:id/shares`: Get document shares
- `POST /api/v1/documents/:id/share`: Share document with another user

### AI Analysis Endpoints

- `POST /api/v1/ai/analyze/:documentId`: Analyze a document
- `GET /api/v1/ai/status/:taskId`: Check analysis task status
- `GET /api/v1/ai/clauses/:documentId`: Get document clauses
- `GET /api/v1/ai/summary/:documentId`: Get document summary
- `GET /api/v1/ai/obligations/:documentId`: Get document obligations
- `POST /api/v1/ai/search/:documentId`: Search document with natural language query
- `GET /api/v1/ai/search-history/:documentId`: Get search history for document

### Subscription Endpoints

- `GET /api/v1/subscriptions`: Get current subscription
- `POST /api/v1/subscriptions`: Create a new subscription
- `PUT /api/v1/subscriptions/:id`: Update subscription
- `DELETE /api/v1/subscriptions/:id`: Cancel subscription
- `GET /api/v1/subscriptions/plans`: Get available subscription plans

## Database Schema

### Users Table

| Column        | Type         | Description                     |
|---------------|--------------|---------------------------------|
| id            | Integer      | Primary key                     |
| email         | String(255)  | User email (unique)             |
| password_hash | String(255)  | Hashed password                 |
| first_name    | String(100)  | User first name                 |
| last_name     | String(100)  | User last name                  |
| role          | String(20)   | User role (admin, user)         |
| is_active     | Boolean      | Account status                  |
| created_at    | DateTime     | Account creation timestamp      |
| updated_at    | DateTime     | Account update timestamp        |
| last_login_at | DateTime     | Last login timestamp            |
| anonymized_at | DateTime     | Anonymization timestamp         |

### Organizations Table

| Column        | Type         | Description                     |
|---------------|--------------|---------------------------------|
| id            | Integer      | Primary key                     |
| name          | String(255)  | Organization name               |
| created_by_id | Integer      | Foreign key to users.id         |
| created_at    | DateTime     | Creation timestamp              |
| updated_at    | DateTime     | Update timestamp                |

### OrganizationUsers Table

| Column          | Type         | Description                     |
|-----------------|--------------|---------------------------------|
| id              | Integer      | Primary key                     |
| organization_id | Integer      | Foreign key to organizations.id |
| user_id         | Integer      | Foreign key to users.id         |
| role            | String(20)   | Role in organization            |
| created_at      | DateTime     | Creation timestamp              |
| updated_at      | DateTime     | Update timestamp                |

### Documents Table

| Column            | Type         | Description                     |
|-------------------|--------------|---------------------------------|
| id                | Integer      | Primary key                     |
| title             | String(255)  | Document title                  |
| organization_id   | Integer      | Foreign key to organizations.id |
| uploaded_by_user_id | Integer    | Foreign key to users.id         |
| status            | String(20)   | Document status                 |
| created_at        | DateTime     | Creation timestamp              |
| updated_at        | DateTime     | Update timestamp                |

### DocumentVersions Table

| Column          | Type         | Description                     |
|-----------------|--------------|---------------------------------|
| id              | Integer      | Primary key                     |
| document_id     | Integer      | Foreign key to documents.id     |
| version_number  | Integer      | Version number                  |
| file_path       | String(255)  | Path to file in storage         |
| file_name       | String(255)  | Original file name              |
| file_type       | String(50)   | File MIME type                  |
| file_size       | Integer      | File size in bytes              |
| created_at      | DateTime     | Creation timestamp              |
| created_by_id   | Integer      | Foreign key to users.id         |

### Clauses Table

| Column              | Type         | Description                       |
|---------------------|--------------|-----------------------------------|
| id                  | Integer      | Primary key                       |
| document_version_id | Integer      | Foreign key to document_versions.id |
| category_id         | Integer      | Foreign key to clause_categories.id |
| text                | Text         | Clause text content               |
| start_offset        | Integer      | Start position in document        |
| end_offset          | Integer      | End position in document          |
| risk_level          | String(20)   | Risk level (high, medium, low, none) |
| risk_description    | Text         | Description of the risk           |
| created_at          | DateTime     | Creation timestamp                |

### ClauseCategories Table

| Column      | Type         | Description                     |
|-------------|--------------|---------------------------------|
| id          | Integer      | Primary key                     |
| name        | String(100)  | Category name                   |
| description | Text         | Category description            |

### Comments Table

| Column       | Type         | Description                     |
|--------------|--------------|---------------------------------|
| id           | Integer      | Primary key                     |
| document_id  | Integer      | Foreign key to documents.id     |
| clause_id    | Integer      | Foreign key to clauses.id       |
| user_id      | Integer      | Foreign key to users.id         |
| text         | Text         | Comment text                    |
| created_at   | DateTime     | Creation timestamp              |
| updated_at   | DateTime     | Update timestamp                |

### DocumentSummaries Table

| Column              | Type         | Description                       |
|---------------------|--------------|-----------------------------------|
| id                  | Integer      | Primary key                       |
| document_version_id | Integer      | Foreign key to document_versions.id |
| overview            | Text         | Document overview                 |
| parties             | JSON         | Key parties involved              |
| key_terms           | JSON         | Key terms and provisions          |
| important_dates     | JSON         | Important dates and deadlines     |
| notable_provisions  | JSON         | Notable provisions                |
| created_at          | DateTime     | Creation timestamp                |

### Obligations Table

| Column              | Type         | Description                       |
|---------------------|--------------|-----------------------------------|
| id                  | Integer      | Primary key                       |
| document_version_id | Integer      | Foreign key to document_versions.id |
| clause_id           | Integer      | Foreign key to clauses.id         |
| party               | String(255)  | Responsible party                 |
| description         | Text         | Obligation description            |
| deadline            | String(255)  | Deadline or due date              |
| consequence         | Text         | Consequence of non-fulfillment    |
| created_at          | DateTime     | Creation timestamp                |

### DocumentShares Table

| Column            | Type         | Description                     |
|-------------------|--------------|---------------------------------|
| id                | Integer      | Primary key                     |
| document_id       | Integer      | Foreign key to documents.id     |
| user_id           | Integer      | Foreign key to users.id         |
| shared_with_email | String(255)  | Email of recipient              |
| permission_level  | String(20)   | Permission level                |
| created_at        | DateTime     | Creation timestamp              |
| expires_at        | DateTime     | Expiration timestamp            |

### SearchQueries Table

| Column       | Type         | Description                     |
|--------------|--------------|---------------------------------|
| id           | Integer      | Primary key                     |
| document_id  | Integer      | Foreign key to documents.id     |
| user_id      | Integer      | Foreign key to users.id         |
| query_text   | Text         | Search query text               |
| result       | JSON         | Search result                   |
| created_at   | DateTime     | Creation timestamp              |

### Subscriptions Table

| Column                 | Type         | Description                     |
|------------------------|--------------|---------------------------------|
| id                     | Integer      | Primary key                     |
| user_id                | Integer      | Foreign key to users.id         |
| organization_id        | Integer      | Foreign key to organizations.id |
| plan_id                | Integer      | Foreign key to subscription_plans.id |
| status                 | String(20)   | Subscription status             |
| current_period_start   | DateTime     | Current period start            |
| current_period_end     | DateTime     | Current period end              |
| stripe_subscription_id | String(255)  | Stripe subscription ID          |
| stripe_customer_id     | String(255)  | Stripe customer ID              |
| created_at             | DateTime     | Creation timestamp              |
| updated_at             | DateTime     | Update timestamp                |

### SubscriptionPlans Table

| Column          | Type         | Description                     |
|-----------------|--------------|---------------------------------|
| id              | Integer      | Primary key                     |
| name            | String(100)  | Plan name                       |
| description     | Text         | Plan description                |
| price           | Integer      | Price in cents                  |
| billing_interval | String(20)  | Billing interval                |
| features        | JSON         | Plan features                   |
| stripe_price_id | String(255)  | Stripe price ID                 |
| is_active       | Boolean      | Plan availability               |
| created_at      | DateTime     | Creation timestamp              |
| updated_at      | DateTime     | Update timestamp                |

### AuditLogs Table

| Column        | Type         | Description                     |
|---------------|--------------|---------------------------------|
| id            | Integer      | Primary key                     |
| user_id       | Integer      | Foreign key to users.id         |
| action        | String(100)  | Action performed                |
| resource_type | String(100)  | Type of resource                |
| resource_id   | Integer      | ID of resource                  |
| details       | JSON         | Action details                  |
| ip_address    | String(45)   | IP address                      |
| user_agent    | String(255)  | User agent                      |
| created_at    | DateTime     | Creation timestamp              |

### UserConsents Table

| Column        | Type         | Description                     |
|---------------|--------------|---------------------------------|
| id            | Integer      | Primary key                     |
| user_id       | Integer      | Foreign key to users.id         |
| consent_type  | String(50)   | Type of consent                 |
| consented     | Boolean      | Whether consent was given       |
| ip_address    | String(45)   | IP address                      |
| user_agent    | String(255)  | User agent                      |
| created_at    | DateTime     | Creation timestamp              |
| updated_at    | DateTime     | Update timestamp                |

## Authentication and Authorization

### JWT Authentication

LexiAI uses JWT (JSON Web Tokens) for authentication. The authentication flow is as follows:

1. User logs in with email and password
2. Server validates credentials and generates a JWT token
3. Token is returned to the client and stored (typically in localStorage)
4. Client includes the token in the Authorization header for subsequent requests
5. Server validates the token for each protected endpoint
6. Token expires after a configured time period (default: 1 hour)
7. Client can refresh the token using the refresh endpoint

### Role-Based Access Control

LexiAI implements role-based access control (RBAC) with the following roles:

- **System Administrator**: Full access to all system features
- **Organization Administrator**: Full access to their organization's resources
- **Manager**: Can manage documents and team members within their organization
- **Member**: Standard user with access to shared documents

Access control is implemented at multiple levels:

1. **Route-level**: Using middleware to restrict access to certain endpoints
2. **Resource-level**: Checking permissions before performing operations
3. **Data-level**: Filtering query results based on user permissions

### Middleware Implementation

Authentication and authorization are implemented using middleware:

```python
from flask import g, request, jsonify
from functools import wraps
import jwt
from src.models.user import User

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if token is in headers
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Authentication token is missing'}), 401
        
        try:
            # Decode token
            payload = jwt.decode(
                token, 
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
            
            # Get user from database
            user = User.query.get(payload['sub'])
            if not user or not user.is_active:
                return jsonify({'error': 'User not found or inactive'}), 401
            
            # Store user in Flask's g object
            g.user = user
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not g.user or not g.user.is_admin():
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    
    return decorated

def organization_admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        org_id = kwargs.get('org_id') or request.view_args.get('org_id')
        if not org_id:
            return jsonify({'error': 'Organization ID is required'}), 400
        
        # Check if user is organization admin
        org_user = OrganizationUser.query.filter_by(
            organization_id=org_id,
            user_id=g.user.id,
            role='owner'
        ).first()
        
        if not org_user and not g.user.is_admin():
            return jsonify({'error': 'Organization admin privileges required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated
```

## AI Integration

### OpenAI API Integration

LexiAI integrates with the OpenAI API for document analysis. The integration is implemented in the `AIService` class:

```python
import openai
from src.config import Config

class AIService:
    """Service for AI-powered document analysis."""
    
    def __init__(self):
        """Initialize the AI service."""
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
    
    def analyze_document(self, text):
        """
        Analyze a document using OpenAI API.
        
        Args:
            text: Document text to analyze
            
        Returns:
            dict: Analysis results
        """
        try:
            # Prepare the prompt
            prompt = f"""
            Analyze the following contract text and extract:
            1. Clauses with categories (e.g., termination, liability, confidentiality)
            2. Risk assessment for each clause (high, medium, low, none)
            3. Summary of the document
            4. Key obligations and deadlines
            
            Contract text:
            {text[:10000]}  # Limit text length for API
            
            Provide the analysis in JSON format with the following structure:
            {{
                "clauses": [
                    {{
                        "category": "category_name",
                        "text": "clause_text",
                        "risk_level": "risk_level",
                        "risk_description": "description_of_risk"
                    }}
                ],
                "summary": {{
                    "overview": "document_overview",
                    "parties": ["party1", "party2"],
                    "key_terms": ["term1", "term2"],
                    "important_dates": ["date1", "date2"],
                    "notable_provisions": ["provision1", "provision2"]
                }},
                "obligations": [
                    {{
                        "party": "responsible_party",
                        "description": "obligation_description",
                        "deadline": "deadline_or_timeframe",
                        "consequence": "consequence_of_non_fulfillment"
                    }}
                ]
            }}
            """
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a legal expert specializing in contract analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=4000
            )
            
            # Parse and return the response
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            # Log the error
            current_app.logger.error(f"Error analyzing document: {str(e)}")
            raise
    
    def search_document(self, document_text, query):
        """
        Search a document using natural language query.
        
        Args:
            document_text: Document text to search
            query: Natural language query
            
        Returns:
            dict: Search results
        """
        try:
            # Prepare the prompt
            prompt = f"""
            Answer the following question based on the contract text:
            
            Question: {query}
            
            Contract text:
            {document_text[:10000]}  # Limit text length for API
            
            Provide the answer in JSON format with the following structure:
            {{
                "answer": "direct_answer_to_question",
                "context": "relevant_clause_or_text_from_contract",
                "explanation": "explanation_of_answer"
            }}
            """
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a legal expert specializing in contract analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1000
            )
            
            # Parse and return the response
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            # Log the error
            current_app.logger.error(f"Error searching document: {str(e)}")
            raise
```

### Document Processing Pipeline

The document processing pipeline consists of the following steps:

1. **Upload**: User uploads a document
2. **Text Extraction**: Extract text from the document (PDF, DOCX, TXT)
3. **Analysis**: Analyze the document using the OpenAI API
4. **Storage**: Store the analysis results in the database
5. **Notification**: Notify the user when analysis is complete

This pipeline is implemented as a background task using Celery:

```python
@celery_app.task(bind=True)
def process_document(self, document_version_id):
    """
    Process a document asynchronously.
    
    Args:
        document_version_id: ID of the document version to process
        
    Returns:
        dict: Processing result
    """
    try:
        # Get document version
        document_version = DocumentVersion.query.get(document_version_id)
        if not document_version:
            return {'status': 'error', 'message': 'Document version not found'}
        
        # Get document
        document = Document.query.get(document_version.document_id)
        if not document:
            return {'status': 'error', 'message': 'Document not found'}
        
        # Update document status
        document.status = 'processing'
        db.session.commit()
        
        # Get storage service
        storage_service = StorageService()
        
        # Get document text
        file_path = document_version.file_path
        file_type = document_version.file_type
        
        # Extract text based on file type
        if file_type == 'application/pdf':
            text = storage_service.extract_text_from_pdf(file_path)
        elif file_type in ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
            text = storage_service.extract_text_from_docx(file_path)
        else:
            text = storage_service.read_text_file(file_path)
        
        # Analyze document
        ai_service = AIService()
        analysis_result = ai_service.analyze_document(text)
        
        # Store clauses
        for clause_data in analysis_result.get('clauses', []):
            # Get or create clause category
            category = ClauseCategory.query.filter_by(name=clause_data['category']).first()
            if not category:
                category = ClauseCategory(name=clause_data['category'])
                db.session.add(category)
                db.session.flush()
            
            # Create clause
            clause = Clause(
                document_version_id=document_version_id,
                category_id=category.id,
                text=clause_data['text'],
                risk_level=clause_data['risk_level'],
                risk_description=clause_data['risk_description']
            )
            db.session.add(clause)
        
        # Store summary
        summary_data = analysis_result.get('summary', {})
        summary = DocumentSummary(
            document_version_id=document_version_id,
            overview=summary_data.get('overview', ''),
            parties=summary_data.get('parties', []),
            key_terms=summary_data.get('key_terms', []),
            important_dates=summary_data.get('important_dates', []),
            notable_provisions=summary_data.get('notable_provisions', [])
        )
        db.session.add(summary)
        
        # Store obligations
        for obligation_data in analysis_result.get('obligations', []):
            obligation = Obligation(
                document_version_id=document_version_id,
                party=obligation_data['party'],
                description=obligation_data['description'],
                deadline=obligation_data['deadline'],
                consequence=obligation_data.get('consequence', '')
            )
            db.session.add(obligation)
        
        # Update document status
        document.status = 'analyzed'
        db.session.commit()
        
        return {
            'status': 'success',
            'document_id': document.id,
            'document_version_id': document_version_id
        }
        
    except Exception as e:
        # Log the error
        current_app.logger.error(f"Error processing document: {str(e)}")
        
        # Update document status
        try:
            document.status = 'error'
            db.session.commit()
        except:
            db.session.rollback()
        
        return {'status': 'error', 'message': str(e)}
```

## Testing

### Unit Testing

Unit tests are written using Python's `unittest` framework. Here's an example of a unit test for the authentication API:

```python
import unittest
import json
from .base import BaseTestCase

class AuthTestCase(BaseTestCase):
    """Test case for authentication API."""
    
    def test_login_success(self):
        """Test successful login."""
        response = self.client.post(
            '/api/v1/auth/login',
            json={
                'email': 'user@example.com',
                'password': 'userpassword'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('access_token', data)
        self.assertIn('user', data)
        self.assertEqual(data['user']['email'], 'user@example.com')
```

### Integration Testing

Integration tests verify that different components work together correctly:

```python
class DocumentIntegrationTestCase(BaseTestCase):
    """Integration test case for document processing."""
    
    def test_document_upload_and_analysis(self):
        """Test document upload and analysis flow."""
        # Log in to get token
        login_response = self.client.post(
            '/api/v1/auth/login',
            json={
                'email': 'user@example.com',
                'password': 'userpassword'
            }
        )
        token = json.loads(login_response.data)['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Create test PDF file
        with open('test.pdf', 'wb') as f:
            f.write(b'%PDF-1.5\nTest PDF content')
        
        # Upload document
        with open('test.pdf', 'rb') as f:
            upload_response = self.client.post(
                '/api/v1/documents',
                headers=headers,
                data={
                    'title': 'Test Document',
                    'file': (f, 'test.pdf')
                },
                content_type='multipart/form-data'
            )
        
        self.assertEqual(upload_response.status_code, 201)
        document_data = json.loads(upload_response.data)
        document_id = document_data['document']['id']
        
        # Start analysis
        analyze_response = self.client.post(
            f'/api/v1/ai/analyze/{document_id}',
            headers=headers
        )
        
        self.assertEqual(analyze_response.status_code, 202)
        task_data = json.loads(analyze_response.data)
        task_id = task_data['task_id']
        
        # Check task status (would normally poll)
        status_response = self.client.get(
            f'/api/v1/ai/status/{task_id}',
            headers=headers
        )
        
        self.assertEqual(status_response.status_code, 200)
        
        # Clean up
        os.remove('test.pdf')
```

### Running Tests

Tests can be run using the provided script:

```bash
python run_tests.py
```

Or individually:

```bash
python -m unittest tests.test_auth
```

## Deployment

### Docker Deployment

The application can be deployed using Docker and Docker Compose:

```bash
# Build the images
docker-compose build

# Start the services
docker-compose up -d

# Initialize the database
docker-compose exec backend flask db upgrade
```

### AWS Deployment

For production deployment on AWS, refer to the AWS deployment guide in the `docs` directory.

### Monitoring and Logging

The application uses structured logging for better observability:

```python
import logging
import json
from flask import request, g

class StructuredLogFormatter(logging.Formatter):
    """Formatter for structured JSON logs."""
    
    def format(self, record):
        """Format log record as JSON."""
        log_data = {
            'timestamp': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add request context if available
        if hasattr(g, 'request_id'):
            log_data['request_id'] = g.request_id
        
        if hasattr(request, 'remote_addr'):
            log_data['ip'] = request.remote_addr
        
        if hasattr(g, 'user'):
            log_data['user_id'] = g.user.id
        
        # Add exception info if available
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

def setup_logging(app):
    """Set up structured logging for the application."""
    handler = logging.StreamHandler()
    handler.setFormatter(StructuredLogFormatter())
    
    app.logger.handlers = [handler]
    app.logger.setLevel(logging.INFO)
    
    # Set werkzeug logger level
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
```

## Security Best Practices

### Password Hashing

Passwords are hashed using Werkzeug's `generate_password_hash` function, which uses PBKDF2 with SHA-256:

```python
from werkzeug.security import generate_password_hash, check_password_hash

def set_password(self, password):
    """Set password hash."""
    self.password_hash = generate_password_hash(password)

def check_password(self, password):
    """Check password against hash."""
    return check_password_hash(self.password_hash, password)
```

### Input Validation

All user input is validated before processing:

```python
from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    """Schema for validating user data."""
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)

def validate_user_data(data):
    """Validate user data."""
    schema = UserSchema()
    errors = schema.validate(data)
    if errors:
        return False, errors
    return True, None
```

### CSRF Protection

CSRF protection is implemented for all state-changing operations:

```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()

def create_app(config=None):
    """Create Flask application."""
    app = Flask(__name__)
    # ...
    csrf.init_app(app)
    # ...
    return app
```

### Content Security Policy

A strict Content Security Policy is enforced:

```python
@app.after_request
def add_security_headers(response):
    """Add security headers to all responses."""
    # Content Security Policy
    csp = (
        "default-src 'self'; "
        "script-src 'self' https://js.stripe.com; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self'; "
        "connect-src 'self' https://api.openai.com https://api.stripe.com; "
        "frame-src https://js.stripe.com; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "form-action 'self'; "
        "frame-ancestors 'self';"
    )
    response.headers['Content-Security-Policy'] = csp
    
    # Other security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    return response
```

### Rate Limiting

Rate limiting is implemented to prevent abuse:

```python
def rate_limit(limit=100, per=60, scope_func=lambda: request.remote_addr):
    """
    Rate limiting decorator for API endpoints.
    
    Args:
        limit: Maximum number of requests allowed
        per: Time period in seconds
        scope_func: Function to determine the scope (e.g., IP address)
    
    Returns:
        Decorated function
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Implementation details...
            pass
        return wrapped
    return decorator
```

### Secure File Handling

Files are validated and stored securely:

```python
def save_file(file, allowed_extensions=None):
    """
    Save a file securely.
    
    Args:
        file: File object to save
        allowed_extensions: List of allowed file extensions
        
    Returns:
        str: Path to saved file
    """
    if allowed_extensions and not allowed_file(file.filename, allowed_extensions):
        raise ValueError(f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}")
    
    # Generate a secure filename
    filename = secure_filename(file.filename)
    
    # Add a unique identifier to prevent overwriting
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    
    # Create directory if it doesn't exist
    os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Save the file
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(file_path)
    
    return file_path
```

### GDPR Compliance

GDPR compliance features are implemented:

```python
def export_user_data(user_id):
    """
    Export all user data in compliance with GDPR right to data portability.
    
    Args:
        user_id: ID of the user whose data should be exported
        
    Returns:
        dict: Path to the exported data file
    """
    # Implementation details...
    pass

def delete_user_data(user_id):
    """
    Delete all user data in compliance with GDPR right to be forgotten.
    
    Args:
        user_id: ID of the user whose data should be deleted
        
    Returns:
        dict: Result of the operation
    """
    # Implementation details...
    pass

def record_consent(user_id, consent_type, consented=True):
    """
    Record user consent for various data processing activities.
    
    Args:
        user_id: ID of the user giving consent
        consent_type: Type of consent (e.g., 'marketing', 'analytics')
        consented: Whether the user consented or not
        
    Returns:
        dict: Result of the operation
    """
    # Implementation details...
    pass
```

