"""Initial migration.

Revision ID: ba8d58bf1d5e
Revises:
Create Date: 2025-01-05 16:01:04.488331

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ba8d58bf1d5e"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users",
        sa.Column("username", sa.String(length=80), nullable=False),
        sa.Column("email", sa.String(length=120), nullable=False),
        sa.Column("password", sa.Text(), nullable=False),
        sa.Column("_created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("_updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )
    op.create_table(
        "accounts",
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("balance", sa.Float(), nullable=False),
        sa.Column(
            "account_type",
            sa.Enum("CHECKING", "SAVINGS", "CREDIT_CARD", name="accounttype"),
            nullable=False,
        ),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("_created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("_updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "transactions_files",
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=1024), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column(
            "_status",
            sa.Enum(
                "PENDING",
                "PROCESSING",
                "VALIDATED",
                "IMPORTED",
                "FAILED",
                name="transactionsfileimportstatus",
            ),
            nullable=False,
        ),
        sa.Column("preview_data", sa.JSON(), nullable=True),
        sa.Column("mapped_headers", sa.JSON(), nullable=True),
        sa.Column("error_log", sa.JSON(), nullable=True),
        sa.Column("account_id", sa.UUID(), nullable=False),
        sa.Column("_created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("_updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["account_id"],
            ["accounts.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("filename", "user_id", name="uq_filename_user"),
    )
    op.create_table(
        "transactions",
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("merchant", sa.String(length=255), nullable=False),
        sa.Column("date", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "_category",
            sa.Enum(
                "GROCERIES",
                "UTILITIES",
                "ENTERTAINMENT",
                "TRANSPORTATION",
                "INCOME",
                "OTHER",
                "HOUSING",
                "UNCATEGORIZED",
                name="transactioncategory",
            ),
            nullable=True,
        ),
        sa.Column("account_id", sa.UUID(), nullable=False),
        sa.Column("file_id", sa.UUID(), nullable=True),
        sa.Column("_created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("_updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["account_id"],
            ["accounts.id"],
        ),
        sa.ForeignKeyConstraint(
            ["file_id"],
            ["transactions_files.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("transactions")
    op.drop_table("transactions_files")
    op.drop_table("accounts")
    op.drop_table("users")

    # Now drop the enum type
    op.execute("DROP TYPE IF EXISTS accounttype")
    op.execute("DROP TYPE IF EXISTS transactionsfileimportstatus")
    op.execute("DROP TYPE IF EXISTS transactioncategory")

    # ### end Alembic commands ###