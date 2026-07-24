"""task_management

Revision ID: 003
Revises: 002
Create Date: 2026-07-23

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import re

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _generate_valid_key(name: str, slug: str, existing_keys: set[str]) -> str:
    """
    Generate a valid 2-10 char uppercase ASCII key matching ^[A-Z][A-Z0-9]{1,9}$
    Collision safe per organization.
    """
    raw = (name or slug or "PET").upper()
    cleaned = re.sub(r"[^A-Z0-9]", "", raw)

    # Ensure it starts with a letter
    if not cleaned or not cleaned[0].isalpha():
        cleaned = "PET" + cleaned

    base_key = cleaned[:10]
    if len(base_key) < 2:
        base_key = base_key + "X"

    candidate = base_key
    counter = 1
    while candidate in existing_keys:
        suffix = str(counter)
        max_base_len = 10 - len(suffix)
        candidate = base_key[:max_base_len] + suffix
        counter += 1

    existing_keys.add(candidate)
    return candidate


def upgrade() -> None:
    conn = op.get_bind()

    # Step 1: Add projects.key (nullable) & projects.next_task_number (NOT NULL DEFAULT 1)
    op.add_column("projects", sa.Column("key", sa.String(length=10), nullable=True))
    op.add_column(
        "projects",
        sa.Column("next_task_number", sa.Integer(), server_default="1", nullable=False),
    )

    # Step 2: Backfill existing Phase 3 projects with deterministic collision-safe keys
    projects_res = conn.execute(
        sa.text(
            "SELECT id, organization_id, name, slug FROM projects ORDER BY created_at ASC"
        )
    )
    org_keys: dict[str, set[str]] = {}

    for row in projects_res:
        p_id = row.id
        org_id = str(row.organization_id)
        if org_id not in org_keys:
            org_keys[org_id] = set()

        generated_key = _generate_valid_key(row.name, row.slug, org_keys[org_id])
        conn.execute(
            sa.text("UPDATE projects SET key = :key WHERE id = :id"),
            {"key": generated_key, "id": p_id},
        )

    # Step 3: Enforce NOT NULL, CHECK, and UNIQUE constraints on projects.key
    op.alter_column("projects", "key", nullable=False)
    op.create_check_constraint(
        "projects_key_format_check", "projects", "key ~ '^[A-Z][A-Z0-9]{1,9}$'"
    )
    op.create_unique_constraint(
        "uq_projects_organization_key", "projects", ["organization_id", "key"]
    )

    # Step 4: Create tasks table
    op.create_table(
        "tasks",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("task_number", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("acceptance_criteria", sa.Text(), nullable=True),
        sa.Column(
            "status", sa.String(length=50), server_default="backlog", nullable=False
        ),
        sa.Column(
            "priority", sa.String(length=50), server_default="medium", nullable=False
        ),
        sa.Column("created_by", sa.UUID(), nullable=False),
        sa.Column("assigned_to", sa.UUID(), nullable=True),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.ForeignKeyConstraint(
            ["assigned_to"],
            ["users.id"],
            name=op.f("fk_tasks_assigned_to_users"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
            name=op.f("fk_tasks_created_by_users"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_tasks_project_id_projects"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tasks")),
        sa.UniqueConstraint(
            "project_id", "task_number", name="uq_tasks_project_number"
        ),
        sa.CheckConstraint("version >= 1", name="ck_tasks_version"),
        sa.CheckConstraint(
            "status IN ('backlog', 'ready', 'in_progress', 'blocked', 'review', 'completed', 'cancelled')",
            name="ck_tasks_status",
        ),
        sa.CheckConstraint(
            "priority IN ('low', 'medium', 'high', 'urgent')", name="ck_tasks_priority"
        ),
        sa.CheckConstraint("length(trim(title)) > 0", name="ck_tasks_title_nonempty"),
    )
    op.create_index(
        "idx_tasks_project_status", "tasks", ["project_id", "status"], unique=False
    )
    op.create_index(
        "idx_tasks_project_assignee",
        "tasks",
        ["project_id", "assigned_to"],
        unique=False,
    )
    op.create_index(
        "idx_tasks_project_created", "tasks", ["project_id", "created_at"], unique=False
    )

    # Step 5: Create task_comments table
    op.create_table(
        "task_comments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("task_id", sa.UUID(), nullable=False),
        sa.Column("author_id", sa.UUID(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.ForeignKeyConstraint(
            ["author_id"],
            ["users.id"],
            name=op.f("fk_task_comments_author_id_users"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["task_id"],
            ["tasks.id"],
            name=op.f("fk_task_comments_task_id_tasks"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_task_comments")),
        sa.CheckConstraint("version >= 1", name="ck_task_comments_version"),
        sa.CheckConstraint(
            "length(trim(body)) > 0", name="ck_task_comments_body_nonempty"
        ),
    )
    op.create_index(
        "idx_task_comments_task_created",
        "task_comments",
        ["task_id", "created_at"],
        unique=False,
    )

    # Step 6: Create labels table
    op.create_table(
        "labels",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column(
            "color", sa.String(length=50), server_default="#6B7280", nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_labels_project_id_projects"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_labels")),
        sa.UniqueConstraint("project_id", "slug", name="uq_labels_project_slug"),
        sa.CheckConstraint("version >= 1", name="ck_labels_version"),
        sa.CheckConstraint("color ~ '^#[0-9A-Fa-f]{6}$'", name="ck_labels_color_hex"),
    )
    op.create_index("idx_labels_project", "labels", ["project_id"], unique=False)
    op.create_index(
        "ix_labels_project_lower_name",
        "labels",
        ["project_id", sa.text("LOWER(name)")],
        unique=True,
    )
    op.create_index(
        "ix_labels_project_lower_slug",
        "labels",
        ["project_id", sa.text("LOWER(slug)")],
        unique=True,
    )

    # Step 7: Create task_labels association table
    op.create_table(
        "task_labels",
        sa.Column("task_id", sa.UUID(), nullable=False),
        sa.Column("label_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["label_id"],
            ["labels.id"],
            name=op.f("fk_task_labels_label_id_labels"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["task_id"],
            ["tasks.id"],
            name=op.f("fk_task_labels_task_id_tasks"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("task_id", "label_id", name=op.f("pk_task_labels")),
    )

    # Step 8: Create task_dependencies table
    op.create_table(
        "task_dependencies",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("task_id", sa.UUID(), nullable=False),
        sa.Column("depends_on_task_id", sa.UUID(), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
            name=op.f("fk_task_dependencies_created_by_users"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["depends_on_task_id"],
            ["tasks.id"],
            name=op.f("fk_task_dependencies_depends_on_task_id_tasks"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["task_id"],
            ["tasks.id"],
            name=op.f("fk_task_dependencies_task_id_tasks"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_task_dependencies")),
        sa.UniqueConstraint(
            "task_id", "depends_on_task_id", name="uq_task_dependencies_pair"
        ),
        sa.CheckConstraint(
            "task_id <> depends_on_task_id", name="ck_task_dependencies_no_self"
        ),
    )
    op.create_index(
        "idx_task_deps_task", "task_dependencies", ["task_id"], unique=False
    )
    op.create_index(
        "idx_task_deps_target",
        "task_dependencies",
        ["depends_on_task_id"],
        unique=False,
    )

    # Step 9: Create task_activities immutable table
    op.create_table(
        "task_activities",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("task_id", sa.UUID(), nullable=False),
        sa.Column("actor_id", sa.UUID(), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("previous_value", sa.Text(), nullable=True),
        sa.Column("new_value", sa.Text(), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["actor_id"],
            ["users.id"],
            name=op.f("fk_task_activities_actor_id_users"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["task_id"],
            ["tasks.id"],
            name=op.f("fk_task_activities_task_id_tasks"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_task_activities")),
    )
    op.create_index(
        "idx_task_activities_task",
        "task_activities",
        ["task_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_task_activities_task", table_name="task_activities")
    op.drop_table("task_activities")

    op.drop_index("idx_task_deps_target", table_name="task_dependencies")
    op.drop_index("idx_task_deps_task", table_name="task_dependencies")
    op.drop_table("task_dependencies")

    op.drop_table("task_labels")

    op.drop_index("ix_labels_project_lower_slug", table_name="labels")
    op.drop_index("ix_labels_project_lower_name", table_name="labels")
    op.drop_index("idx_labels_project", table_name="labels")
    op.drop_table("labels")

    op.drop_index("idx_task_comments_task_created", table_name="task_comments")
    op.drop_table("task_comments")

    op.drop_index("idx_tasks_project_created", table_name="tasks")
    op.drop_index("idx_tasks_project_assignee", table_name="tasks")
    op.drop_index("idx_tasks_project_status", table_name="tasks")
    op.drop_table("tasks")

    op.drop_constraint("uq_projects_organization_key", "projects", type_="unique")
    op.drop_constraint("projects_key_format_check", "projects", type_="check")
    op.drop_column("projects", "next_task_number")
    op.drop_column("projects", "key")
