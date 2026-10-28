"""add uuid to users

Revision ID: d70bc751660b
Revises: 
Create Date: 2026-10-27 15:23:12.675445

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import uuid


# revision identifiers, used by Alembic.
revision: str = 'd70bc751660b'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('uuid', sa.String(36), unique=True, nullable=False, default=str(uuid.uuid4())))
    op.create_index('ix_users_uuid', 'users', ['uuid'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_users_uuid', table_name='users')
    op.drop_column('users', 'uuid')
