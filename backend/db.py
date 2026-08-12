import os
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Text,
    Integer,
    ForeignKey,
    TIMESTAMP,
    func,
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY

DATABASE_URL = os.environ["DATABASE_URL"]
DB_SSLMODE = os.environ.get("DB_SSLMODE", "require")

engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=2,
    pool_pre_ping=True,
    pool_recycle=1800,
    connect_args={"sslmode": DB_SSLMODE},
)

metadata = MetaData()

families_table = Table(
    "families",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()),
    Column("name", Text, nullable=False),
    Column("username", Text, nullable=False, unique=True),
    Column("password_hash", Text, nullable=False),
    Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=func.now()),
)

family_members_table = Table(
    "family_members",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()),
    Column("family_id", UUID(as_uuid=True), ForeignKey("families.id", ondelete="CASCADE"), nullable=False),
    Column("slug", Text, nullable=False),
    Column("name", Text, nullable=False),
    Column("emoji", Text, nullable=False),
    Column("color", Text, nullable=False),
    Column("sort_order", Integer, nullable=False, server_default="0"),
    Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=func.now()),
)

oauth_tokens_table = Table(
    "oauth_tokens",
    metadata,
    Column("account_id", UUID(as_uuid=True), ForeignKey("family_members.id", ondelete="CASCADE"), primary_key=True),
    Column("access_token", Text),
    Column("refresh_token", Text),
    Column("token_uri", Text, nullable=False, server_default="https://oauth2.googleapis.com/token"),
    Column("client_id", Text),
    Column("client_secret", Text),
    Column("scopes", ARRAY(Text)),
    Column("expiry", TIMESTAMP(timezone=True)),
    Column("updated_at", TIMESTAMP(timezone=True), nullable=False, server_default=func.now()),
)
