"""restore_branch_ids

Revision ID: 1a9ebed9f9e4
Revises: d042812ab858
Create Date: 2026-04-27 18:09:07.670674

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1a9ebed9f9e4'
down_revision: Union[str, Sequence[str], None] = 'd042812ab858'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('global_search_index', sa.Column('allowed_branch_ids', sa.ARRAY(sa.Integer()), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('global_search_index', 'allowed_branch_ids')
