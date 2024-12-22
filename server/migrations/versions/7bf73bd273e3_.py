"""empty message

Revision ID: 7bf73bd273e3
Revises: 4135ca824aaa
Create Date: 2024-12-22 17:11:16.298177

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "7bf73bd273e3"
down_revision = "4135ca824aaa"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("transactions_file_import", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "_status",
                sa.Enum(
                    "PENDING",
                    "PROCESSING",
                    "COMPLETED",
                    "FAILED",
                    name="transactionsfileimportstatus",
                ),
                nullable=False,
            )
        )
        batch_op.drop_column("status")

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("transactions_file_import", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "status",
                postgresql.ENUM(
                    "PENDING",
                    "PROCESSING",
                    "COMPLETED",
                    "FAILED",
                    name="transactionsfileimportstatus",
                ),
                autoincrement=False,
                nullable=False,
            )
        )
        batch_op.drop_column("_status")

    # ### end Alembic commands ###
