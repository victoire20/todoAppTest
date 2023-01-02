"""create address_id to userrs

Revision ID: 0505d7eda4a7
Revises: 75dcb0f3213d
Create Date: 2022-12-09 15:06:45.244248

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0505d7eda4a7'
down_revision = '75dcb0f3213d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('address_id', sa.Integer(), nullable=True))
    op.create_foreign_key('address_users_fk', source_table='users', referent_table='address',
                          local_cols=['address_id'], remote_cols=['id'], ondelete="CASCADE")


def downgrade() -> None:
    op.drop_constraint('address_users_fk', table_name="users")
    op.drop_column('users', 'address_id')
