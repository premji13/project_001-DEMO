"""Fix: Make user_id not nullable and add created_at to email_otps

Revision ID: e361436fabe0
Revises: c590a88e1344
Create Date: 2026-05-14 16:48:53.723827

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e361436fabe0'
down_revision: Union[str, None] = 'c590a88e1344'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add created_at column with default value
    op.add_column('email_otps', sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()))
    
    # Delete any rows with NULL user_id (data cleanup)
    connection = op.get_bind()
    connection.execute(sa.text("DELETE FROM email_otps WHERE user_id IS NULL"))
    
    # Now make user_id NOT NULL
    op.alter_column('email_otps', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=False)


def downgrade() -> None:
    # Make user_id nullable again
    op.alter_column('email_otps', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # Drop created_at column
    op.drop_column('email_otps', 'created_at')
