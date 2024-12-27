"""empty message

Revision ID: 4135ca824aaa
Revises: 648f0af4b146
Create Date: 2024-12-22 16:35:54.674778

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4135ca824aaa"
down_revision = "648f0af4b146"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "transactions_file_import",
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=1024), nullable=True),
        sa.Column("error_log", sa.JSON(), nullable=True),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "PENDING",
                "PROCESSING",
                "COMPLETED",
                "FAILED",
                name="transactionsfileimportstatus",
            ),
            nullable=False,
        ),
        sa.Column("processed_at", sa.DateTime(), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("_created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("_updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("filename", "user_id", name="uq_filename_user"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("transactions_file_import")
    # ### end Alembic commands ###
