"""add apt num col

Revision ID: cc5558e3bcd4
Revises: 47cd012d5cb1
Create Date: 2023-08-13 11:08:21.884148

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cc5558e3bcd4'
down_revision: Union[str, None] = '47cd012d5cb1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('address', sa.Column('apt_num', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('address', 'apt_num')
