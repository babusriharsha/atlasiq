"""Create initial AtlasIQ schema

Revision ID: 269484c04bf5
Revises: 
Create Date: 2026-09-09 14:33:35.155371

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '269484c04bf5'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Baseline existing AtlasIQ schema."""
    pass


def downgrade() -> None:
    """Baseline existing AtlasIQ schema."""
    pass
