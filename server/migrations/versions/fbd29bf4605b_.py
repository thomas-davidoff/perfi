"""empty message

Revision ID: fbd29bf4605b
Revises: ac79b6c59474
Create Date: 2024-12-26 14:42:35.360015

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "fbd29bf4605b"
down_revision = "ac79b6c59474"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("transactions_files", schema=None) as batch_op:
        batch_op.add_column(sa.Column("account_id", sa.UUID(), nullable=False))
        batch_op.create_foreign_key(None, "accounts", ["account_id"], ["id"])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("transactions_files", schema=None) as batch_op:
        batch_op.drop_constraint(None, type_="foreignkey")
        batch_op.drop_column("account_id")

    # ### end Alembic commands ###
