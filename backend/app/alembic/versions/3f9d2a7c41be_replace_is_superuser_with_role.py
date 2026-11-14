"""Replace is_superuser with role

Revision ID: 3f9d2a7c41be
Revises: fe56fa70289e
Create Date: 2026-11-14 13:55:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3f9d2a7c41be'
down_revision = 'fe56fa70289e'
branch_labels = None
depends_on = None


def upgrade():
    # A constant default is a metadata-only change on PostgreSQL 11+, and it
    # makes every existing user a member, the least-privileged role.
    op.add_column(
        "user",
        sa.Column("role", sa.String(length=20), nullable=False, server_default="member"),
    )
    op.create_check_constraint(
        "ck_user_role", "user", "role IN ('admin', 'manager', 'member')"
    )
    # Superusers keep exactly their previous powers; nobody becomes a manager.
    op.execute("""UPDATE "user" SET role = 'admin' WHERE is_superuser""")
    op.drop_column("user", "is_superuser")


def downgrade():
    op.add_column(
        "user",
        sa.Column(
            "is_superuser", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
    )
    # Only admins become superusers again; managers lose their extra access.
    op.execute("""UPDATE "user" SET is_superuser = (role = 'admin')""")
    op.alter_column("user", "is_superuser", server_default=None)
    op.drop_constraint("ck_user_role", "user", type_="check")
    op.drop_column("user", "role")
