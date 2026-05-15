"""Convert user_type to ENUM

Revision ID: 9244f930ce2f
Revises: 02079e9ec801
Create Date: 2026-05-15 11:25:35.202863

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9244f930ce2f'
down_revision: Union[str, None] = '02079e9ec801'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create ENUM type
    usertype = sa.Enum('USER', 'ADMIN', 'SUPERADMIN', name='usertype')
    usertype.create(op.get_bind(), checkfirst=True)
    
    # Update existing data: lowercase 'user' to uppercase 'USER'
    op.execute("UPDATE users SET user_type = UPPER(user_type)")
    
    # Remove server default first
    op.alter_column('users', 'user_type',
               existing_server_default=sa.text("'user'"),
               server_default=None)
    
    # Alter column to use ENUM
    op.alter_column('users', 'user_type',
               existing_type=sa.VARCHAR(),
               type_=usertype,
               postgresql_using="user_type::usertype",
               existing_nullable=False)
    
    # Set new default (without extra quotes)
    op.execute("ALTER TABLE users ALTER COLUMN user_type SET DEFAULT 'USER'::usertype")


def downgrade() -> None:
    # Remove default
    op.execute("ALTER TABLE users ALTER COLUMN user_type DROP DEFAULT")
    
    # Revert to VARCHAR
    op.alter_column('users', 'user_type',
               existing_type=sa.Enum('USER', 'ADMIN', 'SUPERADMIN', name='usertype'),
               type_=sa.VARCHAR(),
               postgresql_using="user_type::character varying",
               existing_nullable=False)
    
    # Update data back to lowercase
    op.execute("UPDATE users SET user_type = LOWER(user_type)")
    
    # Set old default
    op.alter_column('users', 'user_type',
               server_default="'user'")
    
    # Drop ENUM type
    op.execute("DROP TYPE usertype")




