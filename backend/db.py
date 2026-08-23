import os
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Text,
    Integer,
    Date,
    ForeignKey,
    TIMESTAMP,
    CheckConstraint,
    UniqueConstraint,
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

tasks_table = Table(
    "tasks",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()),
    Column("family_id", UUID(as_uuid=True), ForeignKey("families.id", ondelete="CASCADE"), nullable=False),
    Column("title", Text, nullable=False),
    Column("start_date", Date, nullable=False),
    Column("start_time", Text),
    Column("recurrence", Text),
    Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=func.now()),
    Column("updated_at", TIMESTAMP(timezone=True), nullable=False, server_default=func.now()),
    CheckConstraint("recurrence IN ('daily', 'weekdays', 'weekly')", name="ck_tasks_recurrence"),
)

task_assignees_table = Table(
    "task_assignees",
    metadata,
    Column("task_id", UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    Column("member_id", UUID(as_uuid=True), ForeignKey("family_members.id", ondelete="CASCADE"), primary_key=True),
    Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=func.now()),
)

task_calendar_links_table = Table(
    "task_calendar_links",
    metadata,
    Column("task_id", UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    Column("member_id", UUID(as_uuid=True), ForeignKey("family_members.id", ondelete="CASCADE"), primary_key=True),
    Column("google_event_id", Text, nullable=False),
    Column("calendar_id", Text, nullable=False, server_default="primary"),
    Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=func.now()),
    Column("updated_at", TIMESTAMP(timezone=True), nullable=False, server_default=func.now()),
)

task_completions_table = Table(
    "task_completions",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()),
    Column("task_id", UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False),
    Column("occurrence_date", Date, nullable=False),
    Column("completed_by", UUID(as_uuid=True), ForeignKey("family_members.id", ondelete="SET NULL")),
    Column("completed_at", TIMESTAMP(timezone=True), nullable=False, server_default=func.now()),
    UniqueConstraint("task_id", "occurrence_date", name="uq_task_completions_task_occurrence"),
)
