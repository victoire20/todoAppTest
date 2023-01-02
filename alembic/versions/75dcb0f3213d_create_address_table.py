"""create address table

Revision ID: 75dcb0f3213d
Revises: 457d124c8b25
Create Date: 2022-12-09 14:58:56.706206

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '75dcb0f3213d'
down_revision = '457d124c8b25'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('address',
                    sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
                    sa.Column('address1', sa.String(), nullable=False),
                    sa.Column('address2', sa.String(), nullable=False),
                    sa.Column('city', sa.String(), nullable=False),
                    sa.Column('state', sa.String(), nullable=False),
                    sa.Column('country', sa.String(), nullable=False),
                    sa.Column('postalcode', sa.String(), nullable=False)
                    )


def downgrade() -> None:
    op.drop_table('address')
