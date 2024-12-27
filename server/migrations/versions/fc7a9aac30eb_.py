"""empty message

Revision ID: fc7a9aac30eb
Revises: fbd29bf4605b
Create Date: 2024-12-26 15:10:44.032493

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "fc7a9aac30eb"
down_revision = "fbd29bf4605b"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("transactions", schema=None) as batch_op:
        batch_op.add_column(
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
            )
        )
        batch_op.drop_column("category")

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("transactions", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "category",
                postgresql.ENUM(
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
                autoincrement=False,
                nullable=True,
            )
        )
        batch_op.drop_column("_category")

    # ### end Alembic commands ###
