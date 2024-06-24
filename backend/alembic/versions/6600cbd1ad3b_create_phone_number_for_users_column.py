"""Create Phone number for users column

Revision ID: 6600cbd1ad3b
Revises:
Create Date: 2024-06-24 13:46:53.883485

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6600cbd1ad3b"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("phone_number", sa.String(11), nullable=True))


def downgrade() -> None:
    pass
