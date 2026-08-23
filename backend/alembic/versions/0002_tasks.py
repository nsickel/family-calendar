"""tasks, task_assignees, task_calendar_links, task_completions

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-23

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

# revision identifiers, used by Alembic.
revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tasks",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("family_id", pg.UUID(as_uuid=True), sa.ForeignKey("families.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("start_date", sa.Date, nullable=False),
        sa.Column("start_time", sa.Text),
        sa.Column("recurrence", sa.Text),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("recurrence IN ('daily', 'weekdays', 'weekly')", name="ck_tasks_recurrence"),
    )
    op.create_index("ix_tasks_family_id", "tasks", ["family_id"])

    op.create_table(
        "task_assignees",
        sa.Column("task_id", pg.UUID(as_uuid=True), sa.ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("member_id", pg.UUID(as_uuid=True), sa.ForeignKey("family_members.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_task_assignees_member_id", "task_assignees", ["member_id"])

    op.create_table(
        "task_calendar_links",
        sa.Column("task_id", pg.UUID(as_uuid=True), sa.ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("member_id", pg.UUID(as_uuid=True), sa.ForeignKey("family_members.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("google_event_id", sa.Text, nullable=False),
        sa.Column("calendar_id", sa.Text, nullable=False, server_default="primary"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_task_calendar_links_member_id", "task_calendar_links", ["member_id"])

    op.create_table(
        "task_completions",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("task_id", pg.UUID(as_uuid=True), sa.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("occurrence_date", sa.Date, nullable=False),
        sa.Column("completed_by", pg.UUID(as_uuid=True), sa.ForeignKey("family_members.id", ondelete="SET NULL")),
        sa.Column("completed_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("task_id", "occurrence_date", name="uq_task_completions_task_occurrence"),
    )
    op.create_index("ix_task_completions_task_id", "task_completions", ["task_id"])


def downgrade() -> None:
    op.drop_index("ix_task_completions_task_id", table_name="task_completions")
    op.drop_table("task_completions")
    op.drop_index("ix_task_calendar_links_member_id", table_name="task_calendar_links")
    op.drop_table("task_calendar_links")
    op.drop_index("ix_task_assignees_member_id", table_name="task_assignees")
    op.drop_table("task_assignees")
    op.drop_index("ix_tasks_family_id", table_name="tasks")
    op.drop_table("tasks")
