# LexiAI Database Schema

## Overview

This document outlines the detailed database schema for the LexiAI MVP application. The schema is designed to support all core features including authentication, billing, document management, AI contract review, and collaboration.

## Database Tables

### Users

Stores user account information.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(20) NOT NULL DEFAULT 'user', -- 'admin' or 'user'
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Subscriptions

Manages user subscription information linked to Stripe.

```sql
CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stripe_customer_id VARCHAR(255) UNIQUE,
    stripe_subscription_id VARCHAR(255) UNIQUE,
    plan_type VARCHAR(50) NOT NULL, -- 'free', 'basic', 'premium'
    status VARCHAR(50) NOT NULL, -- 'active', 'canceled', 'past_due', 'trialing'
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Organizations

Supports multi-tenant architecture for team-based access.

```sql
CREATE TABLE organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### OrganizationUsers

Junction table for many-to-many relationship between users and organizations.

```sql
CREATE TABLE organization_users (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL DEFAULT 'member', -- 'owner', 'admin', 'member'
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(organization_id, user_id)
);
```

### Documents

Stores metadata about uploaded contracts and documents.

```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    uploaded_by_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    file_path VARCHAR(512) NOT NULL, -- S3 path or local storage path
    file_type VARCHAR(10) NOT NULL, -- 'pdf', 'docx', 'txt'
    file_size INTEGER NOT NULL, -- in bytes
    status VARCHAR(20) NOT NULL DEFAULT 'processing', -- 'processing', 'processed', 'error'
    processing_error TEXT, -- stores error message if processing failed
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### DocumentVersions

Tracks document versions for change management.

```sql
CREATE TABLE document_versions (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    file_path VARCHAR(512) NOT NULL,
    created_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(document_id, version_number)
);
```

### Clauses

Stores extracted clauses from documents.

```sql
CREATE TABLE clauses (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    clause_type VARCHAR(100) NOT NULL, -- 'termination', 'liability', 'confidentiality', etc.
    title VARCHAR(255),
    content TEXT NOT NULL,
    page_number INTEGER,
    start_position INTEGER, -- character position in document
    end_position INTEGER, -- character position in document
    risk_level VARCHAR(20), -- 'low', 'medium', 'high'
    risk_explanation TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### ClauseCategories

Predefined categories for clause classification.

```sql
CREATE TABLE clause_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### ClauseCategoryMappings

Maps clauses to categories (many-to-many).

```sql
CREATE TABLE clause_category_mappings (
    id SERIAL PRIMARY KEY,
    clause_id INTEGER NOT NULL REFERENCES clauses(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES clause_categories(id) ON DELETE CASCADE,
    confidence_score FLOAT, -- AI confidence in this categorization
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(clause_id, category_id)
);
```

### Obligations

Tracks obligations and deadlines extracted from contracts.

```sql
CREATE TABLE obligations (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    clause_id INTEGER REFERENCES clauses(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    due_date DATE,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'completed', 'overdue'
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Comments

Stores user comments on clauses.

```sql
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    clause_id INTEGER NOT NULL REFERENCES clauses(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### DocumentShares

Manages document sharing between users.

```sql
CREATE TABLE document_shares (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    permission_level VARCHAR(20) NOT NULL DEFAULT 'read', -- 'read', 'comment', 'edit'
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(document_id, user_id)
);
```

### DocumentSummaries

Stores AI-generated summaries of documents.

```sql
CREATE TABLE document_summaries (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    summary_text TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### SearchQueries

Logs user search queries for analytics and improvement.

```sql
CREATE TABLE search_queries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    query_text TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### AuditLogs

Tracks important system events for security and compliance.

```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL, -- 'user', 'document', 'clause', etc.
    entity_id INTEGER,
    details JSONB,
    ip_address VARCHAR(45),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

## Indexes

```sql
-- Users table indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- Subscriptions table indexes
CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);

-- Organization indexes
CREATE INDEX idx_organization_users_user_id ON organization_users(user_id);
CREATE INDEX idx_organization_users_org_id ON organization_users(organization_id);

-- Documents table indexes
CREATE INDEX idx_documents_org_id ON documents(organization_id);
CREATE INDEX idx_documents_uploaded_by ON documents(uploaded_by_user_id);
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_file_type ON documents(file_type);

-- Clauses table indexes
CREATE INDEX idx_clauses_document_id ON clauses(document_id);
CREATE INDEX idx_clauses_clause_type ON clauses(clause_type);
CREATE INDEX idx_clauses_risk_level ON clauses(risk_level);

-- Category mapping indexes
CREATE INDEX idx_clause_category_mappings_clause_id ON clause_category_mappings(clause_id);
CREATE INDEX idx_clause_category_mappings_category_id ON clause_category_mappings(category_id);

-- Obligations indexes
CREATE INDEX idx_obligations_document_id ON obligations(document_id);
CREATE INDEX idx_obligations_clause_id ON obligations(clause_id);
CREATE INDEX idx_obligations_due_date ON obligations(due_date);
CREATE INDEX idx_obligations_status ON obligations(status);

-- Comments indexes
CREATE INDEX idx_comments_clause_id ON comments(clause_id);
CREATE INDEX idx_comments_user_id ON comments(user_id);

-- Document shares indexes
CREATE INDEX idx_document_shares_document_id ON document_shares(document_id);
CREATE INDEX idx_document_shares_user_id ON document_shares(user_id);

-- Audit logs indexes
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_entity_type ON audit_logs(entity_type);
CREATE INDEX idx_audit_logs_entity_id ON audit_logs(entity_id);
```

## Relationships

1. **Users to Subscriptions**: One-to-one relationship
2. **Users to Organizations**: Many-to-many relationship through OrganizationUsers
3. **Organizations to Documents**: One-to-many relationship
4. **Documents to Clauses**: One-to-many relationship
5. **Clauses to ClauseCategories**: Many-to-many relationship through ClauseCategoryMappings
6. **Documents to Obligations**: One-to-many relationship
7. **Clauses to Comments**: One-to-many relationship
8. **Documents to DocumentShares**: One-to-many relationship
9. **Documents to DocumentSummaries**: One-to-one relationship

## Notes

1. The schema uses PostgreSQL-specific syntax but can be adapted for other SQL databases.
2. JSONB type is used for flexible storage of audit log details.
3. Foreign key constraints ensure referential integrity.
4. Timestamps track creation and modification times for all records.
5. Indexes are created on frequently queried columns to improve performance.
6. The schema supports multi-tenant architecture through the Organizations table.
7. Soft deletion could be implemented by adding `deleted_at` columns where appropriate.

