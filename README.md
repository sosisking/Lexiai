# LexiAI - Contract Review and Due Diligence AI

LexiAI is a SaaS application that provides AI-powered contract review and due diligence capabilities. This MVP replicates the core functions of Kira Systems in a simplified form.

## Features

- **Authentication & Billing**
  - User signup/login with email + password
  - Stripe subscription billing at $100/user/month
  - Admin dashboard to manage subscriptions

- **Contract Upload & Management**
  - Upload contracts in PDF, DOCX, TXT formats
  - Secure document storage with role-based access
  - Document dashboard with search and filter

- **AI Contract Review Engine**
  - Extract and classify clauses (termination, liability, confidentiality, etc.)
  - Highlight risks in plain English
  - Provide summaries of key obligations and deadlines

- **Search & Query**
  - Natural language questions about contracts
  - Relevant clause retrieval with context

- **Collaboration**
  - Comments on specific clauses
  - Document sharing with permission levels
  - Export to PDF or Word

## Technical Stack

- **Frontend**: React + Tailwind CSS
- **Backend**: Flask (Python)
- **Database**: PostgreSQL
- **File Storage**: Local filesystem or AWS S3
- **AI**: OpenAI API for NLP clause extraction + summarization
- **Authentication**: JWT tokens
- **Deployment**: Docker + Docker Compose

## Prerequisites

- Docker and Docker Compose
- OpenAI API key
- Stripe API keys (for billing)
- AWS S3 credentials (optional, for cloud storage)

## Setup Instructions

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/lexiai.git
cd lexiai
```

2. **Configure environment variables**

```bash
cp .env.example .env
```

Edit the `.env` file and fill in your configuration values.

3. **Build and start the application**

```bash
./deploy.sh build
./deploy.sh up
```

4. **Initialize the database**

```bash
./deploy.sh db-init
```

5. **Access the application**

Open your browser and navigate to `http://localhost` (or the port you configured in `.env`).

## Development

### Project Structure

```
lexiai-mvp/
├── backend/               # Flask backend application
│   ├── src/               # Source code
│   │   ├── main.py        # Application entry point
│   │   ├── config.py      # Configuration
│   │   ├── models/        # Database models
│   │   ├── routes/        # API routes
│   │   ├── services/      # Business logic
│   │   ├── middleware/    # Middleware components
│   │   └── utils/         # Utility functions
│   ├── tests/             # Test suite
│   └── requirements.txt   # Python dependencies
├── frontend/              # React frontend application
│   ├── src/               # Source code
│   │   ├── components/    # React components
│   │   ├── contexts/      # React contexts
│   │   ├── lib/           # Utility libraries
│   │   ├── pages/         # Page components
│   │   └── App.jsx        # Main application component
│   ├── public/            # Static assets
│   └── package.json       # Node.js dependencies
├── docker-compose.yml     # Docker Compose configuration
├── Dockerfile.backend     # Backend Dockerfile
├── Dockerfile.frontend    # Frontend Dockerfile
├── nginx.conf             # Nginx configuration
├── deploy.sh              # Deployment script
└── README.md              # This file
```

### Useful Commands

- **Start the application**: `./deploy.sh up`
- **Stop the application**: `./deploy.sh down`
- **View logs**: `./deploy.sh logs`
- **Run tests**: `./deploy.sh test`
- **Open a shell in the backend container**: `./deploy.sh shell`
- **Run database migrations**: `./deploy.sh db-migrate`

## Security Features

- JWT-based authentication
- Role-based access control
- HTTPS support (configure in production)
- Secure password hashing
- GDPR compliance tools
- Content Security Policy
- Rate limiting
- Input validation and sanitization

## GDPR Compliance

LexiAI includes several features to help with GDPR compliance:

- User consent management
- Data export functionality
- Right to be forgotten (data deletion)
- Data anonymization
- Privacy audit reports
- Secure data storage

## Production Deployment

For production deployment, we recommend:

1. Using a proper domain name with SSL certificate
2. Setting up a reverse proxy (e.g., Nginx or Traefik)
3. Using a managed database service
4. Implementing proper monitoring and logging
5. Setting up regular backups
6. Using AWS S3 or similar for document storage

## License

[MIT License](LICENSE)

## Support

For support, please contact support@lexiai.com

