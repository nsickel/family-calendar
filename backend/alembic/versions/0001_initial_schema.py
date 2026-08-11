"""initial schema: families, family_members, oauth_tokens

Revision ID: 0001
Revises:
Create Date: 2026-08-11

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # gen_random_uuid() is a Postgres core built-in since v13 (Supabase runs
    # 15+); no CREATE EXTENSION needed. Requires local dev Postgres >= 13.
    op.create_table(
        "families",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("username", sa.Text, nullable=False, unique=True),
        sa.Column("password_hash", sa.Text, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "family_members",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("family_id", pg.UUID(as_uuid=True), sa.ForeignKey("families.id", ondelete="CASCADE"), nullable=False),
        sa.Column("slug", sa.Text, nullable=False),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("emoji", sa.Text, nullable=False),
        sa.Column("color", sa.Text, nullable=False),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("family_id", "slug", name="uq_family_members_family_slug"),
    )
    op.create_index("ix_family_members_family_id", "family_members", ["family_id"])

    op.create_table(
        "oauth_tokens",
        sa.Column("account_id", pg.UUID(as_uuid=True), sa.ForeignKey("family_members.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("access_token", sa.Text),
        sa.Column("refresh_token", sa.Text),
        sa.Column("token_uri", sa.Text, nullable=False, server_default="https://oauth2.googleapis.com/token"),
        sa.Column("client_id", sa.Text),
        sa.Column("client_secret", sa.Text),
        sa.Column("scopes", pg.ARRAY(sa.Text)),
        sa.Column("expiry", sa.TIMESTAMP(timezone=True)),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("oauth_tokens")
    op.drop_index("ix_family_members_family_id", table_name="family_members")
    op.drop_table("family_members")
    op.drop_table("families")
