from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

# Import models to ensure they are registered with SQLAlchemy
from src.models.user_consent import UserConsent
from src.models.user import User
from src.models.subscription import Subscription
from src.models.organization import Organization, OrganizationUser
from src.models.document import Document, DocumentVersion
from src.models.clause import Clause, ClauseCategory, ClauseCategoryMapping
from src.models.comment import Comment
from src.models.obligation import Obligation
from src.models.document_share import DocumentShare
from src.models.document_summary import DocumentSummary
from src.models.search_query import SearchQuery
from src.models.audit_log import AuditLog

def init_app(app):
    """Initialize database and migrations."""
    db.init_app(app)
    migrate.init_app(app, db)


