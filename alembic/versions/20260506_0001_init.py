"""init postgres schema

Revision ID: 20260506_0001
Revises: 
Create Date: 2026-05-06 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20260506_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tenants",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False, server_default="member"),
        sa.Column("refresh_token_hash", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
    )

    op.create_table(
        "invoices",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("vendor", sa.Text(), nullable=False),
        sa.Column("invoice_date", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(length=8), nullable=False, server_default="TRY"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="open"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )

    op.create_table(
        "cashflow_projections",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("projected_inflow", sa.Numeric(12, 2), nullable=False),
        sa.Column("projected_outflow", sa.Numeric(12, 2), nullable=False),
        sa.Column("net", sa.Numeric(12, 2), nullable=False),
        sa.Column("assumptions", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
    )

    op.create_index("ix_invoices_tenant_due", "invoices", ["tenant_id", "due_date"])
    op.create_index("ix_invoices_tenant", "invoices", ["tenant_id"])
    op.create_index("ix_users_tenant", "users", ["tenant_id"])
    op.create_index("ix_cashflow_tenant_period", "cashflow_projections", ["tenant_id", "period_start"])
    op.create_index("ix_cashflow_tenant", "cashflow_projections", ["tenant_id"])


def downgrade() -> None:
    op.drop_index("ix_cashflow_tenant", table_name="cashflow_projections")
    op.drop_index("ix_cashflow_tenant_period", table_name="cashflow_projections")
    op.drop_index("ix_users_tenant", table_name="users")
    op.drop_index("ix_invoices_tenant", table_name="invoices")
    op.drop_index("ix_invoices_tenant_due", table_name="invoices")

    op.drop_table("cashflow_projections")
    op.drop_table("invoices")
    op.drop_table("users")
    op.drop_table("tenants")
